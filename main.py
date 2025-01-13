import streamlit as st
import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv

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

# Image upload
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
prompt = st.text_input("Enter your prompt")

if st.button("Generate Output"):
    if not uploaded_file:
        st.error("Please upload an image.")
    elif not prompt:
        st.error("Please enter a prompt.")
    else:
        # Save the uploaded file temporarily
        assets_dir = Path("assets")
        assets_dir.mkdir(exist_ok=True)  # Create the assets directory if it doesn't exist
        image_path = assets_dir / uploaded_file.name  # Create a dynamic file path
        
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        print(image_path)
        try:
            # Prepare image data for API
            image_part = {
                "mime_type": "image/png" if image_path.suffix == ".png" else "image/jpeg",
                "data": image_path.read_bytes(),
            }

            # Simulate API call (adjust as needed for your API's requirements)
            model = genai.GenerativeModel("gemini-1.5-pro")
            contents = [str(image_part), prompt]
            response = model.generate_content(contents)

            # Display results
            st.image(image_path, caption="Uploaded Image", use_column_width=True)
            st.success("Response:")
            st.write(response.text)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            # Cleanup: Delete the temporary file
            try:
                image_path.unlink()
                st.info(f"Temporary file deleted: {image_path}")
            except Exception as cleanup_error:
                st.error(f"Error deleting temporary file: {str(cleanup_error)}")
