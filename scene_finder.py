import json
import os
import re
import unicodedata
from res import constants as c
from url_creator import url_creator

def find_scene_starts(data, target_author):
    pattern = r"(?i)(?:`|```).*\n*\b(?:end|hold|close|dropped|offline|moved|moving|continu)\w*.{0,10}\n*(?:`|```)\n*(?:$|@.*|\W*)"
    pattern2 = r"(?i)(?:`|```)\n*.*\b(?:moved|moving|continu)\w*.{0,15}\n*(?:`|```)\n*(?:$|@.*|\W*)"
    messages = data["messages"]
    scene_starts = []
    scene_ends = []

    active_scene = False
    message_count = 0

    for message in messages:
        author = int(message["author"]["id"])

        # scene begins
        if not active_scene and target_author == author:
            active_scene = True
            message_count = 0
            message["category"] = data['channel']['category']
            message["channel"] = data['channel']['name']
            message["status"] = 'open'
            message["link"] = f"https://discord.com/channels/{data['guild']['id']}/{data['channel']['id']}/{message['id']}"
            scene_starts.append(message)

        if active_scene: 

            # accounts for some leeway, resets if characters appear again
            if target_author == author:
                message_count = 0
            else:
                message_count += 1
            
            # Convert the message content and pattern to normalized form
            normalized_content = unicodedata.normalize("NFKD", message["content"])
            normalized_pattern = unicodedata.normalize("NFKD", pattern)
            
            # if there's any END or similar tag
            if re.search(normalized_pattern, normalized_content):
                active_scene = False
                message["category"] = data['channel']['category']
                message["channel"] = data['channel']['name']
                scene_starts[-1]["status"] = 'end'
                message["status"] = 'end'
                message["link"] = f"https://discord.com/channels/{data['guild']['id']}/{data['channel']['id']}/{message['id']}"
                scene_ends.append(message)
                continue
            
            # if it's clear they left
            if message_count > 15:
                active_scene = False
                message["category"] = data['channel']['category']
                message["channel"] = data['channel']['name']
                scene_starts[-1]["status"] = 'timeout'
                message["status"] = 'timeout'
                message["link"] = f"https://discord.com/channels/{data['guild']['id']}/{data['channel']['id']}/{message['id']}"
                scene_ends.append(message)
        

    return scene_starts, scene_ends


# Get the path of the "scenes" folder in the same directory as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
folder_name = c.SEARCH_FOLDER
folder_path = os.path.join(script_dir, folder_name)

with open("res/character_ids.json", "r", encoding="utf-8") as file:
    author_id_mapping = json.load(file)

author = author_id_mapping[c.CHARACTER]

# Create an empty list to store scene starts and ends
all_scene_starts = []
all_scene_ends = []

# Iterate over all JSON files in the server folder and its subfolders
for root, dirs, files in os.walk(folder_path):
    for filename in files:
        if filename.endswith(".json"):
            file_path = os.path.join(root, filename)

            # Load JSON data from file
            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)

                # Find scene starts and ends involving author
                scene_starts, scene_ends = find_scene_starts(json_data, author)

                # Add the messages to the respective lists
                all_scene_starts.extend(scene_starts)
                all_scene_ends.extend(scene_ends)

# Create output JSON file for scene starts
scene_starts_output = {
    "scene_starts": all_scene_starts
}
scene_starts_output_file = os.path.join(script_dir, "out/scene_starts.json")
with open(scene_starts_output_file, "w", encoding="utf-8") as file:
    json.dump(scene_starts_output, file, indent=4)

# Create output JSON file for scene ends
scene_ends_output = {
    "scene_ends": all_scene_ends
}
scene_ends_output_file = os.path.join(script_dir, "out/scene_ends.json")
with open(scene_ends_output_file, "w", encoding="utf-8") as file:
    json.dump(scene_ends_output, file, indent=4)

print("scene starts output file created:", scene_starts_output_file)
print("scene ends output file created:", scene_ends_output_file)

url_creator()