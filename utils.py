import json
import os

def convert_json_to_jsonl():
    # Input and output file paths
    input_file = r"assets/training_data.json"  # Replace with the path to your JSON file
    output_file = r"assets/training_data.jsonl"  # Replace with the desired JSONL file path

    # Read the JSON file
    with open(input_file, "r") as infile:
        data = json.load(infile)  # The data should be a list of dictionaries

    # Write to the JSONL file
    with open(output_file, "w") as outfile:
        for item in data:
            json_line = json.dumps(item)  # Convert dictionary to JSON string
            outfile.write(json_line + "\n")  # Write each dictionary as a new line

def add_png_extension(folder_path):
    """
    Checks all files in the specified folder and appends '.png' to the filename
    if it doesn't already have the '.png' extension.

    :param folder_path: Path to the folder containing files.
    """
    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Skip directories and only process files
        if os.path.isfile(file_path):
            # Check if the file already has a .png extension
            if not filename.lower().endswith('.png'):
                # Append the .png extension
                new_filename = f"{filename}.png"
                new_file_path = os.path.join(folder_path, new_filename)
                
                # Rename the file
                os.rename(file_path, new_file_path)
                print(f"Renamed: {filename} -> {new_filename}")

folder_path = r'assets/extracted_images/Main Post/'
convert_json_to_jsonl()