## Creative Best Practice App

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from time import sleep
import typing_extensions as typing
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import tempfile

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)


#Create temporary file out of uploaded file so that it can be uploaded to Gemini
def create_path_for_uploaded_file(uploaded_file):
    byte_stream = uploaded_file

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    # Write the content of the BytesIO object to the temporary file
        temp_file.write(byte_stream.getvalue())
        temp_file_path = temp_file.name

    return temp_file_path

def upload_to_gemini(path, mime_type=None):
  #Uploads the given file to Gemini.
  #See https://ai.google.dev/gemini-api/docs/prompting_with_media
 
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

#Delete file uploaded to Gemini
def delete_ad_creative_file_from_gemini(ad_creative_file):
    genai.delete_file(ad_creative_file.name)
    print(f'Deleted {ad_creative_file.display_name}.')

def wait_for_files_active(files):
  #Waits for the given files to be active.

  #Some files uploaded to the Gemini API need to be processed before they can be
  #used as prompt inputs. The status can be seen by querying the file's "state"
  #field.

  #This implementation uses a simple blocking polling loop. Production code
  #should probably employ a more sophisticated approach.
  
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

## Function to load Gemini model and get respones
def get_gemini_response(input,ad_creative):
    generation_config = {
                         "temperature": 1,
                         "top_p": 0.95,
                         "top_k": 64,
                         "response_mime_type": "text/plain"
                         }
    model = genai.GenerativeModel(model_name = 'gemini-1.5-pro',
                                  generation_config=generation_config)

    safety_settings = {HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                       HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                       HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                       HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
                       }
    response = model.generate_content([input,ad_creative[0]],
                                      safety_settings=safety_settings
                                      )
    return response.text
    
##initialize our streamlit app
st.set_page_config(page_title="Ad Creative Best Practices App", layout = "wide")

##create the sidebar
with st.sidebar:
    st.image("https://www.mcsaatchiperformance.com/wp-content/themes/mandcsaatchiperformance/assets/img/logo-upright.png", width = 300)
    with st.form("inputs", border=False):
        st.divider()
        uploaded_file = st.file_uploader("Upload an Ad Creative", type=["jpg", "jpeg", "png","mp4"])
        
        uploaded_file_type = ""
        image = ""
        video_bytes = ""
        if uploaded_file is not None:
            uploaded_file_type = ((uploaded_file.type).split("/"))[0]
            if uploaded_file_type == "image":
                image = Image.open(uploaded_file)
        
        with st.expander("Advanced Settings"):
            advertising_channel = st.selectbox("Advertising Channel",("Facebook", "Instagram", "Google", "Tiktok", "Snapchat"),index=None,
                                  placeholder="Select advertising channel...")

        submit=st.form_submit_button("Analyse Ad Creative",type="primary",use_container_width=True)


##create the main page
placeholder = st.empty()
sleep(0.5)
with placeholder.container():
    st.title("Ad Creative Best Practices App")
    st.divider()
    st.header("What does this app do?")
    st.write("This app helps analyse if an ad creative meets best practices. It provides the creative's strengths, what can be improved\
          and how the ad creative can be optimised.")
    st.header("How to use this app?")
    st.write("In the sidebar to the left, upload your ad creative, add a few details and\
          press 'Analyse Ad Creative'. The app will generate insights on your ad creative and then provide recommendations")

advertising_channel_prompt = ''
if advertising_channel is not None:
    advertising_channel_prompt = 'The advertising channel the creative will be served on is {}.'.format(advertising_channel)

input_prompt = """
               I am marketing analyst. I want to make sure that the ad creatives I use are meeting best practices. 
               Please analyse the ad creative to see if meets best practices like size of logo, actionable call to action etc.{}
               Please include in the response an introduction, the creative's strengths, areas to improve, recommendations on how to improve it, general best practices and conclusion.
               Please find the creative attached
               """.format(advertising_channel_prompt)

## Define behaviour when Analyse button is clicked
if submit:
    if uploaded_file is None:
        placeholder.empty()
        sleep(0.5)
        placeholder.error("Please upload an Ad Creative to analyse using the 'Browse files' button in the sidebar on the left")
    else:
        placeholder.empty()
        sleep(0.5)
        with placeholder.container():
            with st.spinner('Uploading Ad Creative...'):
                #Upload ad creative to Gemini
                path_ad_creative = create_path_for_uploaded_file(uploaded_file)
                ad_creative_file = [upload_to_gemini(path_ad_creative, mime_type=uploaded_file.type),]

                # Some files have a processing delay. Wait for them to be ready.
                wait_for_files_active(ad_creative_file)

            with st.spinner('Analysing Ad Creative...'):
                response = ""
                try:
                    #Get Response from Gemini
                    response=get_gemini_response(input_prompt,ad_creative_file)
                    #Delete file uploaded to Gemini
                    delete_ad_creative_file_from_gemini(ad_creative_file)
                    #Delete temporary file
                    os.remove(path_ad_creative)
                except Exception as e: 
                    print(e)

            st.success("Done!")

        placeholder.empty()
        sleep(0.5)
        with placeholder.container():
            col1, col2= st.columns([0.3,0.7], gap="large")

            with col1:
                #Show ad creative on first column of the main page
                st.header("Ad Creative")
                st.divider()
                if uploaded_file_type == "image":
                    st.image(image, use_column_width=True)
                elif uploaded_file_type == "video":
                    st.video(uploaded_file)
                
            
            with col2:
                #Show Gemini response on second column of the main page
                st.header("Does the Ad Creative meet best practices?")
                st.divider()
                with st.container(height=700,border=False):
                    st.markdown(response)
