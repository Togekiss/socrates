import json
import os
import re
from tricks import set_path
set_path()

################# File summary #################

"""

This module is used to test and debug the regex pattern to detect the end of a scene.

Main function: regex()

    This script searches for messages in a folder of JSON files that match a regex pattern.
    It creates a new JSON file with the matched messages.

"""

################# Functions #################

script_dir = os.path.dirname(os.path.abspath(__file__))
folder_name = "Elysium/Scenes/Kaminashi City"
folder_path = os.path.join(script_dir, folder_name)
output_file = "regex_results.json"  # Replace with the desired output file name

regex_pattern = r"(?i)(?:`|```).*\b(?:end|hold|close)\w*.{0,5}(?:`|```)\n*(?:$|@.*)"

all_messages = []

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        
        # Load JSON file
        with open(file_path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
            
            # Extract messages that match the regex pattern
            messages = [message for message in data["messages"] if re.search(regex_pattern, message["content"], re.DOTALL)]
            all_messages.extend(messages)

# Create output JSON file with matched messages
output_data = {"messages": all_messages}
output_path = os.path.join(script_dir, output_file)
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(output_data, file, indent=4, ensure_ascii=False)

print("Output file created:", output_path)
