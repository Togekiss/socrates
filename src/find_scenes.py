import json
import os
import re
import time
import unicodedata
import tricks as t
t.set_path()
from res import constants as c
from output_scene_list import output_scene_list

################ File summary #################

"""

This module finds all th scenes involving the main character in the server backup.

Main function: find_scenes()

    This function loads the character IDs from a file, finds the main character's ID, and creates an empty list to store scenes.

    Then it iterates over all JSON files in the server backup to find scenes involving the main character.
    For each, it stores its start and end messages.
    
    To finish, it saves the scene starts and ends to a JSON file, and calls the output_scene_list module to create a text file with scene names and URLs.

"""

################# Functions #################


"""
    This regex pattern is used to detect the end of a scene.

    It searches for messages that contain common end of scene markers, such as "end", "closed", "moved to", etc,
    particularly in code blocks near the end of the message. 

    It also accounts for tag mentions after the end of scene marker.

    Although I have tried to be as inclusive as possible, some false positives or false negatives might occur.

"""
pattern = r"(?i)(?:`|```).*\n*.*\b(?:end|hold|close|dropped|offline|moved|moving|continu)\w*.{0,10}\n*(?:`|```)\n*(?:$|@.*|\W*)"
pattern2 = r"(?i).*\n*(?:moved to #|moving to #|continued in #|DM END|END DM|\[end\]|\[read\])\w*.{0,20}\n*"

"""
message_info(message, channel, i):
    Creates a JSON object with information about a message.

    Args:
        message (dict): Message info in JSON format
        channel (dict): Channel info in JSON format
        i (int): Index of the message in the channel
    Returns:
        dict: Message info in JSON format
"""

def message_info(message, channel, i):

    msg = {
        "id": message['id'],
        "index": i,        
        "timestamp": message['timestamp'],
        "authorID": message['author']['id'],        
        "content": message['content'],
        "link": f"https://discord.com/channels/{channel['guild']['id']}/{channel['channel']['id']}/{message['id']}"
    }

    return msg


"""
scene_info(start_message, end_message, scene_id, channel, status, characters=[]):

    Creates a JSON object with information about a scene.

    Args:
        start_message (dict): Start message info in JSON format
        end_message (dict): End message info in JSON format
        scene_id (int): Scene ID
        channel (dict): Channel info in JSON format
        status (str): Scene status
        characters (list): List of characters IDs in the scene
    Returns:
        dict: Scene info in JSON format
"""
def scene_info(start_message, end_message, scene_id, channel, status, characters=[]):

    scene = {
        "sceneId": scene_id,
        "category": channel['channel']['category'],
        "channel": channel['channel']['name'],
        "type": "channel" if channel['channel']['type'] == "GuildTextChat" else "thread",
        "status": status,
        "characters": characters,
        "channelId": channel['channel']['id'],        
        "start": start_message,
        "end": end_message
    }

    return scene


"""
find_real_start(messages, scene_start):

    Function to find the real start of a scene, in the case the main character was not the character of the first message.

    It starts analyzing the found start message, and iterates backwards to find the end of the previous scene (or the start of the channel).

    Args:
        channel (dict): The channel.
        scene_start (dict): The found scene start message info.

    Returns:
        int: The index of the real start of the scene.
 """
def find_real_start(channel, found_scene):

    messages = channel["messages"]
    t.log("debug", "\t    Looking for the real start of the scene...")

    # first, we assume the found start is the real start
    index = found_scene["start"]["index"]
    found = False

    characters = found_scene["characters"]

    t.log("debug", f"\t\tCurrent real start is at index {index} with characters {characters}")

    while not found:
        # if the current message is a SOF, the found start is the real start
        if messages[index] == messages[0]:
            found = True
            t.log("debug", f"\t\tReached the beginning of the channel. The real start is at index {index}")
            found_scene["start"] = message_info(messages[index], channel, index)
            return index

        # if the previous message has an END tag, the found start is the real start
        message_content = unicodedata.normalize("NFKD", messages[index-1]["content"])
        if re.search(pattern, message_content, flags=re.I) or re.search(pattern2, message_content, flags=re.I):
            found = True
            t.log("debug",f"\t\tFound 'End' tag in the previous message. The real start is at index {index}")
            found_scene["start"] = message_info(messages[index], channel, index)
            return index
            
        # if the previous message has an character not found in 'characters', the found start is the real start
        if int(messages[index-1]["author"]["id"]) not in characters:
            found = True
            t.log("debug", f"\t\tFound a new character in the previous message. The real start is at index {index}")
            found_scene["start"] = message_info(messages[index], channel, index)
            return index
        
        # if the previous message has an character found in 'characters', index-1 and repeat
        if int(messages[index-1]["author"]["id"]) in characters:
            t.log("debug", "\t\tFound a known character in the previous message. Looking for the real start...")
            index = index-1
 
    # this should not trigger, but just in case
    index = 0
    t.log("debug", f"\t\t{t.YELLOW}Could not find the real start of the scene. Searched until index {index}")
    return index

"""
find_scenes_in_channel(channel, main_character, scene_id)

    Function to find all the scenes of a target character in a channel.

    If the channel is a thread, we can assume it only contains one scene,
    so the function will only check if the main character is in the first 5 messages, and if so, save the scene and the status.

    If the channel is not a thread, we have to check all the messages in the channel, as it can contain multiple scenes.
    If it encounters the main character, it will mark the start of a scene.
    Then, it will keep reading the messages until it finds the scene has ended, either by detecting an "end of scene" marker,
    by reaching the end of the channel, or if the main character does not appear for several messages.

    Args:
        channel (dict): The channel.
        main_character (int): The ID of the target character.
        scene_id (int): The ID of the scene to be searched.

    Returns:
        list: A list of scene starts and ends in the channel, in the format of a JSON object.
        int: The updated scene ID.
"""
def find_scenes_in_channel(channel, main_character, scene_id):

    # create arrays, in case there is more than one scene in a channel
    scenes = []

    # set flags and counters
    active_scene = False
    main_missing_counter = 0

    # check if it's a thread; then it will only contain one scene so there's no need to check it all
    if channel["channel"]["type"] != "GuildTextChat":
        
        characters= []

        #look at the first 5 messages 
        for message in channel["messages"][:5]:
            
            character = int(message["author"]["id"])

            #save the other characters
            if character != main_character and character not in characters:
                characters.append(character)

            # if it contains the main character, we'll get the whole channel
            if not active_scene and character == main_character:

                characters.append(character)
                active_scene = True
                scene_id = scene_id + 1

                t.log("info", f"\tFound a scene in the thread [{channel['channel']['category']} - {channel['channel']['name']}]")

                # get the last message and check if the thread is open or closed
                last_message = channel["messages"][-1]
                normalized_content = unicodedata.normalize("NFKD", last_message["content"])
                
                if re.search(pattern, normalized_content, flags=re.I) or re.search(pattern2, normalized_content, flags=re.I):
                    status = 'closed'
                    t.log("info", f"\t  This scene is {t.GREEN}closed")
                else:
                    status = 'open'
                    t.log("info", f"\t  This scene is still {t.GREEN}open")


        # save the start and the end of the thread
        if active_scene:
            start_msg = message_info(channel["messages"][0], channel, 0)
            end_msg = message_info(channel["messages"][-1], channel, len(channel["messages"]))

            scenes.append(scene_info(start_msg, end_msg, scene_id, channel, status, characters))
            

    # if it's a channel, we will have to check the entirety of it
    else:

        for i, message in enumerate(channel["messages"]):
            
            character = int(message["author"]["id"])
            
            # if we have no scene and we see our character, we mark it as a start of a scene
            if not active_scene and character == main_character:
                
                active_scene = True
                characters = [character]
                main_missing_counter = 0
                chara_search_counter = 0
                scene_id = scene_id + 1

                t.log("info", f"\tFound a scene in the channel [{channel['channel']['category']} - {channel['channel']['name']}]")

                found_msg = message_info(message, channel, i)
                found_scene = scene_info(found_msg, "", scene_id, channel, 'open', characters)

            # if we're already in an active scene, look for the end
            if active_scene: 

                # if our character appears, we consider this scene active
                if main_character == character:
                    main_missing_counter = 0
                
                else:
                    # we write down other characters too- but only at the start,
                    # to prevent adding authors of the next scene if this one timed out
                    if character not in characters and chara_search_counter < 10:
                        characters.append(character)

                    # if our character doesn't appear, we worry the thread might have ended
                    main_missing_counter += 1

                chara_search_counter += 1

                # Convert the message content to normalized form
                normalized_content = unicodedata.normalize("NFKD", message["content"])

                # if there's any END or similar tag
                if re.search(pattern, normalized_content, flags=re.I) or re.search(pattern2, normalized_content, flags=re.I):
                    
                    # tag the scene as closed
                    active_scene = False
                    found_scene["status"] = 'closed'
                    found_scene["characters"] = characters

                    found_scene["end"] = message_info(message, channel, i)
                    find_real_start(channel, found_scene)
                    scenes.append(found_scene)

                    t.log("info", f"\t  This scene is {t.GREEN}closed")

                
                # if it's been too many messages without the main character
                if main_missing_counter > len(characters)*5 and character not in characters:

                    # tag the scene as timed out
                    active_scene = False
                    found_scene["status"] = 'timeout'

                    found_scene["end"] = message_info(message, channel, i)
                    find_real_start(channel, found_scene)
                    scenes.append(found_scene)

                    t.log("info", f"\t  This scene has {t.YELLOW}timed out")

                # if it reaches the end of a channel while the scene is active
                if message == channel["messages"][-1]:
                    active_scene = False
                    found_scene["characters"] = characters

                    found_scene["end"] = message_info(message, channel, i)
                    find_real_start(channel, found_scene)
                    scenes.append(found_scene)

                    t.log("info", f"\t  This scene is still {t.GREEN}open")
                    

    return scenes, scene_id


################ Main function #################

def find_scenes():
    
    start_time = time.time()

    # Get the path of the "scenes" folder from the config file
    folder_path = c.SEARCH_FOLDER

    # Load character IDs
    with open(c.CHARACTER_IDS, "r", encoding="utf-8") as file:
        chara_id_mapping = json.load(file)

    # Find main character ID
    character = chara_id_mapping[c.CHARACTER]

    t.log("base", f"\n## Finding scenes for {c.CHARACTER} with ID {character} in {folder_path}... ##\n")

    # Create an empty list to store scene starts and ends
    all_scenes = []
    scene_id = -1

    # Iterate over all JSON files in the server folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".json"):
                
                file_path = os.path.join(root, filename)
                t.log("log", f"\tAnalysing {file_path}...")

                # Load JSON channel from file
                with open(file_path, "r", encoding="utf-8") as file:
                    json_data = json.load(file)

                    # Find scene starts and ends involving character
                    scenes, scene_id = find_scenes_in_channel(json_data, character, scene_id)

                    # Add the messages to the respective lists, can be more than one per channel
                    all_scenes.extend(scenes)

    t.save_to_json(all_scenes, c.OUTPUT_SCENES)

    t.log("info", f"\n\tScene output file created: {c.OUTPUT_SCENES}")

    # Uses the created JSONs to create a list of links to each scene start
    output_scene_list()

    t.log("base", f"\n## Scene finding finished --- {time.time() - start_time:.2f} seconds --- ##\n")

if __name__ == "__main__":
    find_scenes()
    