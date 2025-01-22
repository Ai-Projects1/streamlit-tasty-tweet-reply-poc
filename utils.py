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
    with open(output_file, "w",encoding='utf-8') as outfile:
        for item in data:
            json_line = json.dumps(item,ensure_ascii=False)  # Convert dictionary to JSON string
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

def remove_duplicates_from_json(file_path):
    """
    Reads a JSON file and removes duplicate dictionaries based on 
    the 'main post' and 'reply' fields.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        list: A list of unique dictionaries from the JSON file.
    """
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Use a set to track unique (main post, reply) pairs
        seen = set()
        unique_data = []
        
        for item in data:
            # Create a tuple of (main post, reply) to identify duplicates
            main_post = item.get("Main caption")
            reply = item.get("Reply")
            key = (main_post, reply)
            
            # Add to unique_data if the pair hasn't been seen
            if key not in seen:
                seen.add(key)
                unique_data.append(item)
        
        return unique_data
    
    except Exception as e:
        print(f"Error reading or processing the JSON file: {e}")
        return []

# Example Usage
# Assuming the JSON file is named "data.json"


print("Duplicates removed. Unique data saved to 'unique_data.json'.")


file_path = r'assets/main_caption_reply.json'
unique_data = remove_duplicates_from_json(file_path)

# Save the cleaned data back to a file (optional)
with open('assets/unique_training_data.json', 'w', encoding='utf-8') as outfile:
    json.dump(unique_data, outfile, ensure_ascii=False, indent=4)
# convert_json_to_jsonl()