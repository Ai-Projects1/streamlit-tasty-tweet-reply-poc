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
    You are replying from a main post in Twitter. Your replies must be explicit and NSFW.
    Here are some sample main post with their equivalent replies. 
    {
        "Main caption": "Ɓack’shot videos? Drop them here 👇",
        "Reply": "don't just stare at me🤭"
    },
    {
        "Main caption": "me or a ps5 pro",
        "Reply": "thick is the new sexy🤭"
    },
    {
        "Main caption": "Big booba thread, ladies do your thing 👇",
        "Reply": "who wants a squeeze? 🤭"
    },
    {
        "Main caption": "ladies we want 🍒🍒, show us !",
        "Reply": "who likes 🍒 this size?🤭"
    },
    {
        "Main caption": "If this is true, then she really went crazy with the Cop 👮‍♂️ 🥵🍑",
        "Reply": "That same cop pulled the same thing on me too. 🤭"
    },
    {
        "Main caption": "Who else saw the full video of what happened at the supermarket park? 🥵👀🤯",
        "Reply": "would you ride with me? 🤭"
    },
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
                "gemini-1.5-flash-002",
                system_instruction=system_instruction
            )
            chat = model.start_chat()

            # Prepare inputs: prompt-only or images + prompt
            inputs = image_inputs + [user_prompt] if user_prompt else image_inputs

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
