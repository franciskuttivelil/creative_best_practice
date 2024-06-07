## Creative Best Practice App

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

st.write("GEMINI_API_KEY", st.secrets["GEMINI_API_KEY"])
genai.configure(api_key=GEMINI_API_KEY)

## Function to load OpenAI model and get respones

def get_gemini_response(input,image):
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content([input,image[0]])
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

st.set_page_config(page_title="Ad Creative Best Practices App")
row1_col1, row1_col2, row1_col3 = st.columns(3)
row2_col1, row2_col2, row2_col3 = st.columns(3)
row3_col1, row3_col2, row3_col3 = st.columns(3)
with row1_col2:
    st.image("https://www.mcsaatchiperformance.com/wp-content/uploads/2019/10/mc-saatchi-performance.png", width=400)
st.header("Ad Creative Best Practices App")
uploaded_file = st.file_uploader("Upload an Ad Creative", type=["jpg", "jpeg", "png"])
image=""   
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", width=200)


submit=st.button("Analyse Ad Creative")

input_prompt = """
               I am marketing analyst. I want to make sure that the ad creatives I use are meeting best practices. Please analyse the ad creative to see if meets best practices like size of logo, actionable call to action etc. Please find the creative attached
               """

## If ask button is clicked

if submit:
    image_data = input_image_setup(uploaded_file)
    response=get_gemini_response(input_prompt,image_data)
    st.subheader("Does the Ad Creative meet best practices?")
    st.write(response)
