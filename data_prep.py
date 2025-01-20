import os
import json
from openpyxl import load_workbook
from io import BytesIO
from PIL import Image as PILImage

# Input file and output folder
input_filepath = 'assets/Tasty Twitter Reply Data.xlsx'  # Path to the Excel file
sheet_name = 'DATA'  # Sheet name containing images
output_folder = 'assets/extracted_images'  # Folder to save the extracted images
jsonl_filename = 'assets/extracted_images_data.jsonl'  # Path for the jsonl file

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load the workbook and sheet
workbook = load_workbook(input_filepath)
sheet = workbook[sheet_name]

training_data = []
# Iterate over all images in the sheet
for i, drawing in enumerate(sheet._images, start=1):  # `_images` contains all embedded images
    # Extract the image extension (if available)
    image_extension = drawing.path.split('.')[-1] if drawing.path else 'png'  # Default to 'png' if no extension

    # Get the corresponding caption
    anchor_cell = drawing.anchor
    anchor_position = anchor_cell._from  # Get the anchor's position (this is a Point object)
    image_row = anchor_position.row  # Row number
    image_col = anchor_position.col  # Column number

    # Get the caption
    if image_col == 2:  # Column C is the 3rd column (index 2)
        caption = sheet.cell(row=image_row, column=4).value  # Caption in column D
        subfolder = 'Main Post'  # Save in "Main Post" subfolder
    elif image_col == 4:  # Column E is the 5th column (index 4)
        caption = sheet.cell(row=image_row, column=6).value  # Caption in column F
        subfolder = 'Reply'  # Save in "Reply" subfolder
    else:
        subfolder = 'Uncategorized'  # Default folder for uncategorized images

    # Create subfolder if it doesn't exist
    subfolder_path = os.path.join(output_folder, subfolder)
    os.makedirs(subfolder_path, exist_ok=True)

    # Create a file name for the image
    image_name = f"image_{i}.{image_extension}"
    image_path = os.path.join(subfolder_path, image_name)  # Full path for the image file

    # Get the image as a byte stream
    image_data = drawing.ref  # BytesIO object

    # Open the image with Pillow and save it as a standard format (e.g., PNG)
    with PILImage.open(image_data) as img:
        img.save(image_path)  # Save the image in the correct format

    print(f"Saved: {image_path}")

    if caption:
        # Create the JSON object
        json_obj = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "fileData": {
                                "mimeType": f"image/{image_extension}",
                                "fileUri": f"gs://b-bucket/images/{subfolder}/{image_name}"
                            }
                        },
                        {
                            "text": f'Generate {subfolder}'
                        }
                    ]
                },
                {
                    "role": "model",
                    "parts": [
                        {
                            "text": caption
                        }
                    ]
                }
            ]
        }

        # Write the JSON object to the jsonl file
        print(f'{caption} written in JSON')
        training_data.append(json_obj)

with open('assets/training_data.json', 'w') as json_file:
    json.dump(training_data, json_file)

print("Image extraction, caption saving, and JSONL creation complete!")
