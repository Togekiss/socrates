import os
import json

# Function to assign unique IDs to authors based on their names
def assign_unique_ids(data, id_mapping):
    messages = data["messages"]

    for message in messages:

        #only do this for tuppers
        if message["author"]["isBot"]:
            author_name = message["author"]["name"]

            # If the author is not already assigned an ID, assign a new one
            if author_name not in id_mapping:
                new_id = len(id_mapping) + 1
                id_mapping[author_name] = new_id
         
            # Update the author's ID in the message
            message["author"]["id"] = f"{id_mapping[author_name]}"



# Get the path of the "Chat" folder in the same directory as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
folder_name = "Elysium"
chat_folder_path = os.path.join(script_dir, folder_name)


# Initialize a dictionary to store author IDs
chara_file="res/character_ids.json"
if os.path.exists(chara_file):
    # The file exists, open and load its contents
    with open(chara_file, "r", encoding="utf-8") as file:
        author_id_mapping = json.load(file)
else:
    # The file does not exist, initialize an empty dictionary
    author_id_mapping = {}


# Iterate over all JSON files in the "Chat" folder and its subfolders
for root, dirs, files in os.walk(chat_folder_path):
    for filename in files:
        if filename.endswith(".json"):
            file_path = os.path.join(root, filename)

            # Load JSON data from file
            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)

                # Assign unique IDs to authors in the JSON data
                assign_unique_ids(json_data, author_id_mapping)

            # Save the modified JSON data back to the file
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(json_data, file, indent=4)


#sort and save the dictionary
sorted_dict = {key: author_id_mapping[key] for key in sorted(author_id_mapping)}
with open(chara_file, "w", encoding="utf-8") as file:
    json.dump(sorted_dict, file, indent=4)

# Print the sorted dictionary
for key, value in sorted_dict.items():
    print(f"{key}: {value}")
