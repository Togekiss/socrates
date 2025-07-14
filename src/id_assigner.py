import os
import json
import time
from set_path import set_path
set_path()

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
         
            # Update the author's ID in the message
            message["author"]["id"] = f"{id_mapping[author_name]}"


################# Main function #################

def id_assigner():

    # Get the path of the server folder in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_name = "Elysium"
    folder_path = os.path.join(script_dir, folder_name)


    # Initialize a dictionary to store author IDs
    chara_file="res/character_ids.json"
    if os.path.exists(chara_file):
        # The file exists, open and load its contents
        with open(chara_file, "r", encoding="utf-8") as file:
            author_id_mapping = json.load(file)
    else:
        # The file does not exist, initialize an empty dictionary
        author_id_mapping = {}


    # Iterate over all JSON files in the folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
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
    #sorted_dict = {key: author_id_mapping[key] for key in sorted(author_id_mapping)}
    sorted_dict = {key: author_id_mapping[key] for key in sorted(author_id_mapping, key=lambda k: author_id_mapping[k])}

    with open(chara_file, "w", encoding="utf-8") as file:
        json.dump(sorted_dict, file, indent=4)

    # Print the sorted dictionary
    for key, value in sorted_dict.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    
    start_time = time.time()
    print("ID assigning started...")
    id_assigner()
    print("ID assigning finished --- %s seconds ---" % (time.time() - start_time))