import base64
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part,Image, HarmCategory, HarmBlockThreshold
from PIL import Image as PILImage
import streamlit as st
import io
import tempfile
import os

# Generation config for Vertex AI
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

# Safety settings for Vertex AI
safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.OFF,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.OFF,
}

# System instruction
system_instruction = '''
    You are posting a picture on Twitter and you need to generate a flirty caption for that picture. Here are some examples:
    caption 1: thick is the new sexy🤭,
    caption 2: more than you can handle🤭,
    caption 3: can I sit next to you?🤭,
    caption 4: have you seen mine?🤭,
    caption 5: don't just stare at me🤭,
    caption 6: who wants a squeeze? 🤭,
    caption 7: wanna hit it from behind?,
    caption 8: my laundry vid got leaked
'''

# Streamlit app
st.title("Twitter Reply AI Model")
st.text("Upload an image and provide a prompt for reply generation")

# File uploader for a single image
uploaded_file = st.file_uploader("Upload an image (only one allowed)", type=["png", "jpg", "jpeg"], accept_multiple_files=False)

# Placeholder for image input
image_input = None
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_file_path = temp_file.name  # Get the full path to the file

        print('temp_file_path',temp_file_path)
    image = PILImage.open(uploaded_file)
    st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)

    # Convert image to base64
    if image.mode in ("RGBA", "LA"):
        image = image.convert("RGB")
    image.thumbnail((300, 300))  # Resize to reduce size
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=50)  # Compress and save as JPEG
    buffer.seek(0)
    encoded_image = base64.b64encode(buffer.read()).decode("utf-8")
    image_input = Part.from_image(Image.load_from_file(temp_file_path))

# Text input for prompt
user_prompt = st.text_area("Enter your prompt here", "")

# Submit button
if st.button("Generate Reply"):
    if user_prompt or image_input:  # Allow generation with either prompt or an image
        try:
            # Initialize Vertex AI generative model
            model = GenerativeModel(
                "gemini-1.5-flash-002",
                # system_instruction=system_instruction
            )
            chat = model.start_chat()

            # Prepare inputs: prompt-only or image + prompt
            inputs = []
            # inputs.append(system_instruction)
            if image_input:
                inputs.append("Describe the image and generate 10 captions based on the image. Should be witty, suggestive and humurous. It should just be one sentence/one liner")
                inputs.append(image_input)
            if user_prompt:
                inputs.append(user_prompt)
            
            inputs.append('Answer in this format and please add some emojis in the replies:')
            inputs.append('Description: \n, Reply 1: \n Reply 2: \n')

            # Send the inputs to the model
            response = chat.send_message(
                inputs,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

            # Display the generated reply
            st.subheader("Generated Reply")
            st.write(response.text)

            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt or upload an image before generating a reply.")
