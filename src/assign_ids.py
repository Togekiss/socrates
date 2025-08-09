import os
import json
import time
import tricks as t
t.set_path()
from res import constants as c

################ File summary #################

"""

This module assigns unique IDs to the Tupperbox bots in the backup of a Discord server.

Main function: assign_ids()

    This function traverses all JSON files in the specified folder and its subdirectories to assign unique 
    identifiers to each bot found within the message data. If a character ID mapping file exists, it will be 
    loaded and updated; otherwise, a new mapping will be created. The function ensures that each bot has a 
    unique ID, updates the original JSON files with these IDs, and saves the mapping back to the character 
    ID file for future reference.

"""

################ Functions #################

"""
character_info(id, name)

    Creates a dictionary representing a character with the given ID and name.

    Args:
        id (int): The unique identifier of the character.
        name (str): The name of the character.

    Returns:
        dict: A dictionary representing a character with the given ID and name.
              Other values are left empty for posterior manual updates.
"""
def character_info(id, name):

    character = {
        "id": id,
        "names": [name],
        "writer": [],
        "tags": [],
        "other_versions": []
    }

    return character

"""
build_id_lookup_map(characters)

    Creates a dictionary mapping character names to their unique IDs.

    Args:
        characters (list): A list of JSON objects representing characters.

    Returns:
        dict: A dictionary mapping character names to their unique IDs.
"""
def build_id_lookup_map(characters):
    name_map = {}

    def register(char):
        for name in char.get("names", []):
            name_map[name] = char["id"]

    for char in characters:
        register(char)
        for alt in char.get("other_versions", []):
            register(alt)

    return name_map

"""
get_character_id(name)

    Retrieves the unique ID of a character with the given name.

    Args:
        name (str): The name of the character.

    Returns:
        int or None: The unique ID of the character, or None if not found.
"""
def get_character_id(name):

    characters_json = t.load_from_json(c.CHARACTER_IDS)

    for character in characters_json:
        if name in character["names"]:
            return character["id"]
        for alt in character.get("other_versions", []):
            if name in alt["names"]:
                return alt["id"]
    return None


"""
get_all_character_ids(name)

    Retrieves the unique IDs of all versions of a character with the given name.
    The type of versions it returns is determined by the settings in 'res/constants.py'.

    Args:
        name (str): The name of the character.

    Returns:
        list: A list of unique IDs representing all versions of the character.
"""
def get_all_character_ids(name):

    characters_json = t.load_from_json(c.CHARACTER_IDS)

    ids = []

    for character in characters_json:

        # Assume the user input the generic name, so look for main names
        if name in character["names"]:

            # Write down the main version
            ids.append(character["id"])
            
            # Write down the other versions
            for alt in character.get("other_versions", []):

                if c.INCLUDE_ALL_WRITERS and "has_other_writers" in alt["tags"]:
                    ids.append(alt["id"])
                
                if c.INCLUDE_ALTER_EGOS and "alter_ego" in alt["tags"]:
                    ids.append(alt["id"])
                
                if c.INCLUDE_FAMILIARS and "familiar" in alt["tags"]:
                    ids.append(alt["id"])
                
                if c.INCLUDE_NPCS and "npc" in alt["tags"]:
                    ids.append(alt["id"])
        
        # Adding this for compatibility, but if the user input the name of an alt, it won't get the main version
        for alt in character.get("other_versions", []):
            if name in alt["names"]:
                ids.append(alt["id"])
            
    return ids

"""
assign_unique_ids(data, characters_json, lookup_map)

    Assigns unique IDs to the Tupperbox bots in the given data and updates the ID mapping accordingly.

    This function iterates through the messages in the given data and assigns a unique identifier to each bot character.
    If the character is not already assigned an ID, a new one is assigned and added to the ID mapping. The function then updates
    the author's ID in the message.

    Args:
        data (dict): The JSON data of the channel, containing a list of messages.
        characters_json (dict): A dictionary containing character information.
        lookup_map (dict): A dictionary mapping character names to their respective unique IDs.

    Returns:
        None
"""
def assign_unique_ids(data, characters_json, lookup_map):

    messages = data["messages"]

    for message in messages:

        #only do this for tuppers
        if message["author"]["isBot"]:
            author_name = message["author"]["name"]

            # If the character is not already in the list, add it
            if author_name not in lookup_map:
                new_id = len(lookup_map) + 1
                new_character = character_info(new_id, author_name)
                characters_json.append(new_character)

                lookup_map[author_name] = new_id

                t.log("info", f"\t  Found a new Tupper: {author_name} (ID: {new_id})")
         
            # Update the author's ID in the message
            message["author"]["id"] = f"{lookup_map[author_name]}"


################# Main function #################

def assign_ids():

    t.log("base", f"\n###  Assigning unique IDs to Tupperbox bots in {c.SERVER_NAME}...  ###\n")

    start_time = time.time()

    # Get the path of the server folder in the same directory as the script
    folder_path = c.SERVER_NAME

    # Open or create a dictionary to store character IDs
    if os.path.exists(c.CHARACTER_IDS):
        characters_json = t.load_from_json(c.CHARACTER_IDS)
    
    # If the file does not exist, initialize an empty dictionary
    else:
        characters_json = []

    t.log("info", f"\tLoaded {len(characters_json)} existing characters\n")

    lookup_map = build_id_lookup_map(characters_json)

    t.log("debug", f"\t  Found {len(lookup_map)} distinct character names\n")

    t.log("debug", f"\tIterating over backup files in {folder_path}...\n")  

    # Iterate over all channel JSON files in the folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".json"):

                file_path = os.path.join(root, filename)

                t.log("debug", f"\t    Analysing {file_path}...")

                # Load channel JSON data from file
                channel_data = t.load_from_json(file_path)

                # Assign unique IDs to authors in the JSON data
                assign_unique_ids(channel_data, characters_json, lookup_map)

                # Save the modified JSON data back to the file
                t.save_to_json(channel_data, file_path)


    #save the dictionary
    t.save_to_json(characters_json, c.CHARACTER_IDS)

    # debug the dictionary
    t.log("debug", "\tFinal list of character names:")
    for key, value in lookup_map.items():
       t.log("debug", f"\t    {key}: {value}")

    t.log("info", f"\tSaved {len(lookup_map)} unique character names\n")

    t.log("base", f"### ID assigning finished --- {time.time() - start_time:.2f} seconds --- ###\n")

if __name__ == "__main__":
    assign_ids()
    