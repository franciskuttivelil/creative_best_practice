## Creative Best Practice App

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from time import sleep
import typing_extensions as typing


GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

## Class that defines response json schema
class Analysis(typing.TypedDict):
    strengths: list[str]
    areas_of_weakness: list[str]
    recommendation: list[str]

## Function to load Gemini model and get respones

def get_gemini_response(input,image):
    model = genai.GenerativeModel('gemini-1.5-pro')
    generation_config=genai.GenerationConfig(response_mime_type="application/json",
                                           response_schema = list[Analysis])
    response = model.generate_content([input,image[0]],
                                      #generation_config=generation_config
                                      )
    return response.text
    

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")


##initialize our streamlit app
st.set_page_config(page_title="Ad Creative Best Practices App", layout = "wide")

##create the sidebar
with st.sidebar:
    st.image("https://www.mcsaatchiperformance.com/wp-content/themes/mandcsaatchiperformance/assets/img/logo-upright.png", width = 300)
    with st.form("inputs", border=False):
        st.divider()
        uploaded_file = st.file_uploader("Upload an Ad Creative", type=["jpg", "jpeg", "png"])

        image=""   
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            #st.write("Uploaded Image")
            #st.image(image, use_column_width=True)
        
        with st.expander("Advanced Settings"):
            advertising_channel = st.selectbox("Advertising Channel",("Facebook", "Instagram", "Google", "Tiktok", "Snapchat"),index=None,
                                  placeholder="Select advertising channel...")

        submit=st.form_submit_button("Analyse Ad Creative",type="primary",use_container_width=True)


##create the main page
placeholder = st.empty()
sleep(0.01)
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

print(input_prompt)
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
            with st.spinner('Analysing Ad Creative...'):
                image_data = input_image_setup(uploaded_file)
                response=get_gemini_response(input_prompt,image_data)

            st.success("Done!")

        placeholder.empty()
        sleep(1)
        with placeholder.container():
            col1, col2= st.columns([0.3,0.7], gap="large")

            with col1:
                st.header("Ad Creative")
                st.divider()
                st.image(image, use_column_width=True)
            
            with col2:
                st.header("Does the Ad Creative meet best practices?")
                st.divider()
                st.write(response)
