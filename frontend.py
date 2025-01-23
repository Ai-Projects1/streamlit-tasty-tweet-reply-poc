import base64
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part,HarmCategory,HarmBlockThreshold
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
safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.OFF,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.OFF,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.OFF,
            }

# safety_settings = [
#     SafetySetting(
#         category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
#         threshold=SafetySetting.HarmBlockThreshold.OFF
#     ),
#     SafetySetting(
#         category=SafetySetting.HARM_CATEGORY_DANGEROUS_CONTENT,
#         threshold=SafetySetting.HarmBlockThreshold.OFF
#     ),
#     SafetySetting(
#         category=SafetySetting.HARM_CATEGORY_SEXUALLY_EXPLICIT,
#         threshold=SafetySetting.HarmBlockThreshold.OFF
#     ),
#     SafetySetting(
#         category=SafetySetting.HARM_CATEGORY_HARASSMENT,
#         threshold=SafetySetting.HarmBlockThreshold.OFF
#     ),
# ]

# System instruction
system_instruction = '''
    You are posting a picture in Twitter and you need to generate a suggestive and flirty caption for that picture. here are some examples:
    caption 1: thick is the new sexy🤭,
    caption 2: more than you can handle🤭,
    caption 3: can i sit next to you?🤭,
    caption 4: have you seen mine?🤭,
    caption 5: don't just stare at me🤭,
    caption 6: who wants a squeeze? 🤭,
    caption 7: wanna hit it from behind?,
    caption 8: my laundry vid got leaked    
'''

# Streamlit app
st.title("Twitter Reply AI Model")
st.text("You can upload multiple images (optional) or provide a prompt for reply generation")

# File uploader for multiple images (optional)
uploaded_files = st.file_uploader("Upload images (optional, you can select multiple)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Display the uploaded images in the UI
image_inputs = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)
        
        # Convert image to base64
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")
        image.thumbnail((300, 300))  # Resize to reduce size
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=50)  # Compress and save as JPEG
        buffer.seek(0)
        encoded_image = base64.b64encode(buffer.read()).decode("utf-8")
        image_input = f"data:image/jpeg;base64,{encoded_image}"
        image_inputs.append(image_input)

# Text input for prompt
user_prompt = st.text_area("Enter your prompt here", "")

# Submit button
if st.button("Generate Reply"):
    if user_prompt or image_inputs:  # Allow generation with either prompt or images
        try:
            # Initialize Vertex AI generative model
            model = GenerativeModel(
                "gemini-1.5-pro-002",
                system_instruction=system_instruction
            )
            chat = model.start_chat()

            # Prepare inputs: prompt-only or images + prompt
            inputs = ['create 5 captions for this image input.']
            inputs += image_inputs
            inputs += user_prompt
            inputs += [
                'Answer in this format:',
                'Reply 1:, Reply 2:'
            ]

            print('inputs',inputs)
            # Send the inputs to the model
            response = chat.send_message(
                inputs,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )


            # Display the generated reply
            st.subheader("Generated Reply")
            st.write(response.text)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt or upload at least one image before generating a reply.")
