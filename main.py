import streamlit as st
import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv
import PIL.Image
from vertexai.generative_models import (
    GenerativeModel,
    HarmCategory,
    HarmBlockThreshold,
    Part,
    SafetySetting,
    GenerationConfig
)


# Load the environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
if not api_key:
    st.error("API key not found. Please set GEMINI_API_KEY in your .env file.")
else:
    genai.configure(api_key=api_key)

# Streamlit app setup
st.title("Bump Generator")
st.markdown("Upload an image, provide a prompt, and get AI-generated output.")
prompt = st.text_input("Enter your prompt")

safety_settings =  [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]



if st.button("Generate Output"):
    if not prompt:
        st.error("Please enter a prompt.")
    else:
        image_path = r'assets/sample2.png'
        image_file = PIL.Image.open(image_path)
        
        try:

            # Simulate API call (adjust as needed for your API's requirements)
            model = genai.GenerativeModel("gemini-1.5-pro")
            contents = [f'{prompt}:\n',image_file]
            response = model.generate_content(contents, safety_settings=safety_settings)

            # Display results
            st.image(image_path, caption="Uploaded Image", use_column_width=True)
            st.success("Response:")
            st.write(response.text)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")