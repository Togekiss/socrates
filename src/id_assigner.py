import os
import json
import time
import tricks as t
t.set_path()
from res import constants as c

################ File summary #################

"""

This module assigns unique IDs to the Tupperbox bots in the backup of a Discord server.

Main function: id_assigner()

    This function traverses all JSON files in the specified folder and its subdirectories to assign unique 
    identifiers to each bot found within the message data. If a character ID mapping file exists, it will be 
    loaded and updated; otherwise, a new mapping will be created. The function ensures that each bot has a 
    unique ID, updates the original JSON files with these IDs, and saves the sorted mapping back to the character 
    ID file for future reference.

"""

################ Functions #################

"""
assign_unique_ids(data, id_mapping)

    Assigns unique IDs to the Tupperbox bots in the given data and updates the ID mapping accordingly.

    This function iterates through the messages in the given data and assigns a unique identifier to each bot author.
    If the author is not already assigned an ID, a new one is assigned and added to the ID mapping. The function then updates
    the author's ID in the message.

    Args:
        data (dict): The JSON data of the channel, containing a list of messages.
        id_mapping (dict): A dictionary mapping author names to their respective unique IDs.

    Returns:
        None
"""
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

                t.log("info", f"\t  Found a new Tupper: {author_name} (ID: {new_id})")
         
            # Update the author's ID in the message
            message["author"]["id"] = f"{id_mapping[author_name]}"


################# Main function #################

def id_assigner():

    t.log("base", f"\n###  Assigning unique IDs to Tupperbox bots in {c.SERVER_NAME}...  ###\n")

    start_time = time.time()

    # Get the path of the server folder in the same directory as the script
    folder_path = c.SERVER_NAME

    # Open a dictionary to store author IDs
    chara_file = c.CHARACTER_IDS

    # If the file exists, open and load its contents
    if os.path.exists(chara_file):
        with open(chara_file, "r", encoding="utf-8") as file:
            author_id_mapping = json.load(file)
    
    # If the file does not exist, initialize an empty dictionary
    else:
        author_id_mapping = {}

    t.log("debug", f"\tIterating over backup files in {folder_path}...\n")  
    # Iterate over all channel JSON files in the folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".json"):

                file_path = os.path.join(root, filename)

                t.log("debug", f"\t    Analysing {file_path}...")

                # Load channel JSON data from file
                with open(file_path, "r", encoding="utf-8") as file:
                    channel_data = json.load(file)

                    # Assign unique IDs to authors in the JSON data
                    assign_unique_ids(channel_data, author_id_mapping)

                # Save the modified JSON data back to the file
                t.save_to_json(channel_data, file_path)


    #sort and save the dictionary
    sorted_dict = {key: author_id_mapping[key] for key in sorted(author_id_mapping, key=lambda k: author_id_mapping[k])}

    t.save_to_json(sorted_dict, chara_file)

    # debug the sorted dictionary
    t.log("debug", "\tSorted dictionary:")
    for key, value in sorted_dict.items():
        t.log("debug", f"\t    {key}: {value}")

    t.log("info", f"\tSaved {len(sorted_dict)} unique IDs\n")

    t.log("base", f"### ID assigning finished --- {time.time() - start_time:.2f} seconds --- ###\n")

if __name__ == "__main__":
    id_assigner()
    