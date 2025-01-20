import base64
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part
import streamlit as st
from PIL import Image
import io

# Generation config for Vertex AI
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

# Safety settings for Vertex AI
safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

# Streamlit app
st.title("Dynamic Vertex AI Frontend")
st.header("Upload an image and provide a prompt for caption generation")

# File uploader for images
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# Display the uploaded image in the UI
if uploaded_file:
    # Open and display the image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

# Text input for prompt
user_prompt = st.text_area("Enter your prompt here", "")

# Submit button
if st.button("Generate Caption"):
    if uploaded_file and user_prompt:
        try:
            # Read the uploaded image and compress it
            if image.mode in ("RGBA", "LA"):
                image = image.convert("RGB")
            image.thumbnail((300, 300))  # Resize to reduce size
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=50)  # Compress and save as JPEG
            buffer.seek(0)
            encoded_image = base64.b64encode(buffer.read()).decode("utf-8")
            image_input = f"data:image/jpeg;base64,{encoded_image}"

            # Initialize Vertex AI generative model
            model = GenerativeModel(
                "projects/275499389350/locations/us-central1/endpoints/2831525016011538432",
            )
            chat = model.start_chat()

            # Send the prompt and image to the model
            response = chat.send_message(
                [image_input, user_prompt],
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

            # Display the generated caption
            st.subheader("Generated Caption")
            st.write(response.text)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload an image and enter a prompt before generating a caption.")
