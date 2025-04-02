import base64
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part,Image, HarmCategory, HarmBlockThreshold
from PIL import Image as PILImage
import streamlit as st
import io
import tempfile
import os
import json
import requests
from google.oauth2 import service_account
import pyperclip
import time
from datetime import datetime
import re

# Set page config to wide mode
st.set_page_config(layout="wide")

# Detect mobile devices
def is_mobile():
    try:
        import user_agents
        user_agent = st.get_user_agent()
        return user_agents.parse(user_agent).is_mobile
    except:
        # Fallback to viewport width detection
        return False

# Initialize session state for mobile view
if 'mobile_view' not in st.session_state:
    st.session_state.mobile_view = is_mobile()

# Add this after the session state initialization
if 'last_copy_time' not in st.session_state:
    st.session_state.last_copy_time = datetime.now()
if 'copied_text' not in st.session_state:
    st.session_state.copied_text = ""
if 'copied_captions' not in st.session_state:
    st.session_state.copied_captions = set()
if 'button_states' not in st.session_state:
    st.session_state.button_states = {}

def copy_and_mark(text, key):
    """Helper function to copy text and update session state"""
    pyperclip.copy(text)
    st.session_state.copied_captions.add(key)
    time.sleep(0.1)  # Small delay to prevent rapid clicking

def handle_copy(text, button_id):
    """Handle copy action and button state"""
    if button_id not in st.session_state.button_states:
        st.session_state.button_states[button_id] = "📋"
    
    if st.session_state.button_states[button_id] == "📋":
        pyperclip.copy(text)
        st.session_state.button_states[button_id] = "✅"
    else:
        st.session_state.button_states[button_id] = "📋"

def copy_text(text, button_id):
    """Copy text and update button state"""
    pyperclip.copy(text)
    st.session_state.button_states[button_id] = True

def copy_to_clipboard(text):
    """Copy text to clipboard"""
    pyperclip.copy(text)
    st.toast("Copied to clipboard!", icon="✅")

# Custom CSS for responsive design
st.markdown("""
    <style>
    .stApp {
        max-width: 100%;
        padding: 1rem;
    }
    
    /* Center title */
    .title-container {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .title-container h1 {
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    /* Card styles with dark mode support */
    .header-card {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        background-color: #161a1d;
        color: var(--text-color, #262730);
        border: none;
    }
    
    .header-card h3 {
        margin: 0;
        color: inherit;
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    .content-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        background-color: var(--content-bg-color, #ffffff);
        color: var(--text-color, #262730);
    }
    
    /* Code block custom styling */
    .stCodeBlock {
        margin-bottom: 0.5rem;
    }
    
    .stCodeBlock pre {
        background-color: var(--code-bg-color, #f8f9fa);
        border-radius: 0.25rem;
        border: none !important;
    }
    
    .content-card .description {
        font-weight: normal;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-color, #e0e0e0);
        color: inherit;
        background-color: inherit;
    }
    
    .desc-label {
        font-weight: bold;
        color: inherit;
    }
    
    .content-card .reply {
        padding: 0.5rem 0;
        margin: 0.25rem 0;
    }
    
    /* Responsive container */
    @media (max-width: 640px) {
        .main > div {
            padding: 0;
        }
        .stTextArea > div > textarea {
            font-size: 16px; /* Prevent zoom on mobile */
        }
    }
    
    /* Custom container for results */
    .results-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 1rem;
    }
    
    /* Caption container styles with dark mode support */
    .caption-container {
        border-radius: 6px;
        padding: 8px 12px;
        margin: 4px 0;
        transition: background-color 0.2s;
        background-color: var(--code-bg-color, #f8f9fa);
    }
    
    .caption-container:hover {
        background-color: var(--code-hover-color, #f0f2f6);
    }
    
    /* Copy button styles */
    div[data-testid="stButton"] > button {
        background-color: var(--content-bg-color) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    div[data-testid="stButton"] > button:hover {
        border-color: #888888 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    
    div[data-testid="stButton"] > button:active {
        transform: translateY(0px);
    }
    
    /* Horizontal rule styling */
    hr {
        border-color: var(--border-color) !important;
    }
    
    .caption-row {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        border-radius: 4px;
        margin: 4px 0;
        cursor: pointer;
        transition: background-color 0.2s;
        background-color: var(--code-bg-color, #f8f9fa);
    }
    
    .caption-row:hover {
        background-color: var(--code-hover-color, #e9ecef);
    }
    
    .caption-text {
        flex-grow: 1;
        margin-right: 8px;
    }
    
    /* Hide the text input but keep it accessible */
    .hidden-input {
        position: absolute;
        left: -9999px;
    }
    
    /* Text area custom styling */
    .stTextArea textarea {
        min-height: 70px !important;
        padding: 8px !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        resize: none !important;
        overflow: hidden !important;
    }
    
    /* Center the clipboard icon */
    .clipboard-icon {
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    
    /* General styling for all themes */
    :root {
        --background-color: #f0f2f6;
        --content-bg-color: #ffffff;
        --text-color: #262730;
        --border-color: #e0e0e0;
        --code-bg-color: #f5f5f5;
        --code-hover-color: #e6e6e6;
    }
    
    /* Dark mode vars */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0e1117;
            --content-bg-color: #161a1d;
            --text-color: #ffffff;
            --border-color: #363636;
            --code-bg-color: #161a1d;
            --code-hover-color: #232323;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        /* Override Streamlit's code block styling for dark mode */
        .stCodeBlock pre {
            background-color: var(--code-bg-color, #161a1d) !important;
            color: #e6e6e6 !important;
        }
        
        /* Title text color */
        .title-container h1 {
            color: #ffffff !important;
        }
        
        /* Ensure the bullet numbers are visible in dark mode */
        .stCodeBlock::before {
            background-color: var(--code-bg-color, #161a1d) !important;
            color: #e6e6e6 !important;
        }
        
        /* Content card styling for dark mode */
        .content-card {
            background-color: var(--content-bg-color, #161a1d) !important;
            border: none !important;
            color: var(--text-color, #ffffff) !important;
        }
        
        /* Description styling for dark mode */
        .content-card .description {
            color: var(--text-color, #ffffff) !important;
            border-bottom-color: var(--border-color, #363636) !important;
            background-color: inherit !important;
        }
        
        /* Make all Streamlit elements follow dark theme */
        .stTextInput label, .stTextArea label {
            color: var(--text-color) !important;
        }
        
        hr {
            border-color: var(--border-color) !important;
        }
        
        /* Header card for dark mode */
        .header-card {
            background-color: #161a1d;
            color: #ffffff;
        }
        
        /* Override Streamlit's default background for dark mode */
        .stApp {
            background-color: #0e1117 !important;
        }
    }
    
    /* Light mode specific styles */
    @media (prefers-color-scheme: light) {
        .header-card {
            background-color: #f7f7f7;
            color: #262730;
        }
        
        .content-card {
            background-color: #ffffff !important;
        }
        
        .content-card .description {
            color: #262730 !important;
            border-bottom-color: #e0e0e0 !important;
            background-color: inherit !important;
        }
        
        /* Ensure buttons look good in light mode too */
        div[data-testid="stButton"] > button {
            background-color: #f0f2f6 !important;
            color: #262730 !important;
            border: 1px solid #e0e0e0 !important;
        }
        
        div[data-testid="stButton"] > button:hover {
            background-color: #e6e6e6 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Load service account credentials
with open('authentication_creds.json') as f:
    credentials_dict = json.load(f)

# Create credentials object
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# Generation config for Vertex AI
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

# Initialize Vertex AI with credentials
vertexai.init(
    project="groovy-legacy-438407-u5",
    location="us-central1",
    credentials=credentials
)

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
st.markdown('<div class="title-container"><h1>Bump Gen AI</h1></div>', unsafe_allow_html=True)

# Create a container with custom width for the form
form_container = st.container()
with form_container:
    # Responsive columns - adjust ratios for different screen sizes
    if st.session_state.get('mobile_view', False):
        form_col = st.columns([1])[0]  # Full width on mobile
    else:
        _, form_col, _ = st.columns([1, 2, 1])  # Centered on desktop
    
    with form_col:
        st.text("Enter image URLs (one per line or separated by commas) and provide a prompt for reply generation")

        # Single textbox for multiple URLs
        urls_input = st.text_area("Image URLs", 
                                help="Enter multiple image URLs (one per line or separated by commas). Maximum 8 images allowed.")

        # Text input for prompt
        user_prompt = st.text_area("Enter your prompt here", "")
        
        # Submit button
        generate_button = st.button("Generate Replies")

# Process URLs
urls = []
if urls_input:
    # Split by both newlines and commas, then clean up
    raw_urls = [url.strip() for url in urls_input.replace(',', '\n').split('\n')]
    urls = [url for url in raw_urls if url]  # Remove empty strings

# Limit to 8 URLs
if len(urls) > 8:
    st.warning("Maximum 8 images allowed. Only the first 8 will be processed.")
    urls = urls[:8]

# Placeholder for image inputs
image_inputs = []
temp_file_paths = []
images = []  # Store PIL images for reuse

if urls:
    # Process images without preview
    for idx, url in enumerate(urls):
        try:
            # Download image from URL
            response = requests.get(url)
            if response.status_code == 200:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name
                    temp_file_paths.append(temp_file_path)
                    
                    # Process image without displaying
                    image = PILImage.open(io.BytesIO(response.content))
                    images.append(image.copy())  # Store a copy of the image
                    
                    # Convert image to base64
                    if image.mode in ("RGBA", "LA"):
                        image = image.convert("RGB")
                    image.thumbnail((300, 300))  # Resize to reduce size
                    buffer = io.BytesIO()
                    image.save(buffer, format="JPEG", quality=50)  # Compress and save as JPEG
                    buffer.seek(0)
                    encoded_image = base64.b64encode(buffer.read()).decode("utf-8")
                    image_inputs.append(Part.from_image(Image.load_from_file(temp_file_path)))
            else:
                st.error(f"Failed to load image from URL {idx + 1}")
        except Exception as e:
            st.error(f"Error processing image {idx + 1}: {str(e)}")

# Submit button
if generate_button:
    if user_prompt or image_inputs:  # Allow generation with either prompt or images
        try:
            # Initialize Vertex AI generative model
            model = GenerativeModel(
                "gemini-1.5-flash-002",
            )
            
            # Process images in groups of 3 (or 1 on mobile)
            group_size = 1 if st.session_state.get('mobile_view', False) else 3  # Changed back to 3
            for i in range(0, len(image_inputs), group_size):
                # Create columns for displaying results
                result_cols = st.columns(group_size)
                
                # Process images in the current group
                for j in range(group_size):
                    if i + j < len(image_inputs):
                        with result_cols[j]:
                            idx = i + j
                            st.markdown(
                                f"<div class='header-card'><h3>Generated Reply for Image {idx + 1}</h3></div>",
                                unsafe_allow_html=True
                            )
                            
                            # Display the image with responsive width
                            st.image(images[idx], use_container_width=True)
                            
                            chat = model.start_chat()
                            
                            # Prepare inputs
                            inputs = []
                            inputs.append("""Analyze the image and generate replies in the following format:
1. First line should be a brief description of the image
2. Then generate exactly 10 witty, flirty, and suggestive one-liner captions
3. Each caption should include at least one emoji
4. Format the output exactly like this:
Description: [brief image description]
1️⃣ [first caption]
2️⃣ [second caption]
3️⃣ [third caption]
4️⃣ [fourth caption]
5️⃣ [fifth caption]
6️⃣ [sixth caption]
7️⃣ [seventh caption]
8️⃣ [eighth caption]
9️⃣ [ninth caption]
🔟 [tenth caption]""")
                            inputs.append(image_inputs[idx])
                            if user_prompt:
                                inputs.append(user_prompt)

                            # Send the inputs to the model
                            response = chat.send_message(
                                inputs,
                                generation_config=generation_config,
                                safety_settings=safety_settings,
                            )

                            # Format the response with proper HTML structure
                            response_lines = response.text.strip().split('\n')
                            formatted_html = []
                            
                            for line in response_lines:
                                line = line.strip()
                                if line.startswith('Description:'):
                                    description_parts = line.split(':', 1)
                                    label = description_parts[0]
                                    desc_content = description_parts[1].strip() if len(description_parts) > 1 else ""
                                    formatted_html.append(f'<div class="description"><span class="desc-label">{label}:</span> {desc_content}</div>')
                                elif any(line.startswith(str(i)) for i in range(1, 10)) or line.startswith('10') or line.startswith('🔟'):
                                    # Extract just the caption text without number emoji
                                    if any(line.startswith(emoji) for emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']):
                                        # These are usually followed by a space
                                        parts = line.split(' ', 1)
                                        bullet = parts[0]
                                        if len(parts) > 1:
                                            caption_text = parts[1]
                                        else:
                                            caption_text = ""
                                    elif line[0].isdigit():
                                        # For regular numbers, find where number ends
                                        match = re.search(r"^(\d+[\.:]?\s+)", line)
                                        if match:
                                            bullet = match.group(1).strip()
                                            caption_text = line[match.end():]
                                        else:
                                            bullet = ""
                                            caption_text = line
                                    else:
                                        bullet = ""
                                        caption_text = line
                                    
                                    # Display just the caption text (what will be copied)
                                    st.code(caption_text, language=None)
                                    
                                    # Add CSS to display the number before the code block
                                    element_id = f"caption_{hash(line)}"
                                    st.markdown(f"""
                                        <style>
                                        .stCodeBlock:last-of-type::before {{
                                            content: "{bullet} ";
                                            font-family: monospace;
                                            position: absolute;
                                            left: 6px;
                                            z-index: 1;
                                            background-color: inherit;
                                            color: inherit;
                                            padding: 0 4px;
                                        }}
                                        </style>
                                    """, unsafe_allow_html=True)

                            formatted_response = '\n'.join(formatted_html)
                            
                            # Add global script to modify clipboard behavior when copying
                            st.markdown("""
                            <script>
                            document.addEventListener('copy', function(e) {
                                const selection = window.getSelection();
                                const text = selection.toString();
                                
                                // Check if the text starts with a number or emoji number
                                if (/^[0-9️⃣🔟]/.test(text)) {
                                    // Remove the number prefix
                                    const modifiedText = text.replace(/^[0-9️⃣🔟]+[\s\.]+/, '');
                                    
                                    // Set the modified text in the clipboard
                                    e.clipboardData.setData('text/plain', modifiedText);
                                    e.preventDefault();
                                }
                            });
                            </script>
                            """, unsafe_allow_html=True)

                            # Display the formatted response
                            st.markdown(
                                f"<div class='content-card'>{formatted_response}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)

            # Clean up temporary files
            for temp_file_path in temp_file_paths:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt or provide image URLs before generating replies.")