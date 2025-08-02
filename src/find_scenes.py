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

This module finds all th scenes involving the target character in the server backup.

Main function: find_scenes()

    This function loads the character IDs from a file, finds the target character's ID, and creates two empty lists to store scene starts and ends.

    Then it iterates over all JSON files in the server backup to find scenes involving the target character.
    For each, it stores its start and end messages in the corresponding lists.
    
    To finish, it saves the scene starts and ends to JSON files, and calls the output_scene_list module to create a text file with scene names and URLs.

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
message_info(message, channel, status, scene_id, i, other_authors=[]):
    Creates a JSON object with information about a message.

    Args:
        message (dict): The message to be saved
        channel (dict): The channel channel
        status (str): The status of the scene (open, closed, timed out)
        scene_id (int): The ID of the scene
        i (int): The index of the message in the channel
        other_authors (list, optional): The IDs of other characters involved in the scene. Defaults to an empty list.

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

def scene_info(start_message, end_message, scene_id, channel, status, other_authors=[]):

    scene = {
        "sceneId": scene_id,
        "category": channel['channel']['category'],
        "channel": channel['channel']['name'],
        "type": "channel" if channel['channel']['type'] == "GuildTextChat" else "thread",
        "status": status,
        "otherAuthors": other_authors,
        "channelId": channel['channel']['id'],        
        "start": start_message,
        "end": end_message
    }

    return scene


"""
find_real_start(messages, scene_start):

    Function to find the real start of a scene, in the case the target character was not the author of the first message.

    It starts analyzing the found start message, and iterates backwards to find the end of the previous scene (or the start of the channel).

    Args:
        messages (list): The list of messages in the channel.
        scene_start (dict): The found scene start message info.

    Returns:
        int: The index of the real start of the scene.
 """
def find_real_start(messages, scene_start):

    # first, we assume the found start is the real start
    index = scene_start["index"]
    found = False

    all_authors = scene_start["otherAuthors"]
    all_authors.append(int(scene_start["authorID"]))

    t.log("debug", "\ninside real start at index ", index, " with authors ", all_authors)

    while not found:
        # if the current message is a SOF, the found start is the real start
        if messages[index] == messages[0]:
            found = True
            t.log("debug", "found SOF")
            return index

        # if the previous message has an END tag, the found start is the real start
        message_content = unicodedata.normalize("NFKD", messages[index-1]["content"])
        if re.search(pattern, message_content, flags=re.I) or re.search(pattern2, message_content, flags=re.I):
            found = True
            t.log("debug", "found END at index ", index)
            return index
            
        # if the previous message has an author not found in all_authors, the found start is the real start
        if int(messages[index-1]["author"]["id"]) not in all_authors:
            found = True
            t.log("debug", "found different author ", int(messages[index-1]["author"]["id"]) ," at index ", index)
            return index
        
        # if the previous message has an author found in all_authors, index-1 and repeat
        if int(messages[index-1]["author"]["id"]) in all_authors:
            t.log("debug", "found none, going back")
            index = index-1
    
    # this should not trigger, but just in case
    t.log("debug", "no trigger")
    return index

"""
find_scenes_in_channel(channel, target_author, scene_id)

    Function to find all the scenes of a target character in a channel.

    If the channel is a thread, we can assume it only contains one scene,
    so the function will only check if the target character is in the first 5 messages, and if so, save the scene and the status.

    If the channel is not a thread, we have to check all the messages in the channel, as it can contain multiple scenes.
    If it encounters the target character, it will mark the start of a scene.
    Then, it will keep reading the messages until it finds the scene has ended, either by detecting an "end of scene" marker,
    by reaching the end of the channel, or if the target character does not appear for several messages.

    Args:
        channel (dict): The channel channel.
        target_author (int): The ID of the target character.
        scene_id (int): The ID of the scene to be searched.

    Returns:
        list: A list of scene starts and ends in the channel, in the format of a JSON object.
        int: The updated scene ID.
"""
def find_scenes_in_channel(channel, target_author, scene_id):

    # create arrays, in case there is more than one scene in a channel
    scenes = []

    # set flags and counters
    active_scene = False
    author_missing_counter = 0

    # check if it's a thread; then it will only contain one scene so there's no need to check it all
    if channel["channel"]["type"] != "GuildTextChat":
        
        other_authors= []

        #look at the first 5 messages 
        for message in channel["messages"][:5]:
            
            author = int(message["author"]["id"])

            #save the other characters
            if author != target_author and author not in other_authors:
                other_authors.append(author)

            # if it contains the target author, we'll get the whole channel
            if not active_scene and author == target_author:

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

            scenes.append(scene_info(start_msg, end_msg, scene_id, channel, status, other_authors))
            

    # if it's a channel, we will have to check the entirety of it
    else:

        for i, message in enumerate(channel["messages"]):
            
            author = int(message["author"]["id"])
            
            # if we have no scene and we see our character, we mark it as a start of a scene
            if not active_scene and author == target_author:
                
                active_scene = True
                other_authors= []
                author_missing_counter = 0
                other_author_search = 0
                scene_id = scene_id + 1

                t.log("info", f"\tFound a scene in the channel [{channel['channel']['category']} - {channel['channel']['name']}]")

                found_msg = message_info(message, channel, i)
                found_scene = scene_info(found_msg, "", scene_id, channel, 'open', other_authors)

            # if we're already in an active scene, look for the end
            if active_scene: 

                # if our character appears, we consider this scene active
                if target_author == author:
                    author_missing_counter = 0
                
                else:
                    # we write down other characters too- but only at the start,
                    # to prevent adding authors of the next scene if this one timed out
                    if author not in other_authors and other_author_search < 10:
                        other_authors.append(author)

                    # if our character doesn't appear, we worry the thread might have ended
                    author_missing_counter += 1

                other_author_search = other_author_search + 1

                # Convert the message content to normalized form
                normalized_content = unicodedata.normalize("NFKD", message["content"])

                
                # if there's any END or similar tag
                if re.search(pattern, normalized_content, flags=re.I) or re.search(pattern2, normalized_content, flags=re.I):
                    
                    # tag the scene as closed
                    active_scene = False
                    found_scene["status"] = 'closed'
                    found_scene["otherAuthors"] = other_authors

                    msg = message_info(message, channel, i)
                    found_scene["end"] = msg
                    scenes.append(found_scene)

                    t.log("info", f"\t  This scene is {t.GREEN}closed")

                
                # if it's been too many messages without the target author
                if author_missing_counter > len(other_authors)*5 and author not in other_authors:

                    # tag the scene as timed out
                    active_scene = False
                    found_scene["status"] = 'timeout'

                    msg = message_info(message, channel, i)
                    found_scene["end"] = msg
                    scenes.append(found_scene)

                    t.log("info", f"\t  This scene has {t.YELLOW}timed out")

                # if it reaches the end of a channel while the scene is active
                if message == channel["messages"][-1]:
                    active_scene = False
                    found_scene["otherAuthors"] = other_authors
                    found_scene["end"] = message_info(message, channel, i)
                    scenes.append(found_scene)

                    t.log("info", f"\t  This scene is still {t.GREEN}open")

                """
                This does not work very well

                # if we found the end of a scene, check if the start was the real start
                if not active_scene:
                    start_index = find_real_start(channel["messages"], scene_starts[-1])
                    msg = message_info(channel["messages"][start_index],
                                       channel, scene_starts[-1]["status"],
                                       scene_id, start_index,
                                       other_authors)
                    scene_starts[-1] = msg
                """

    return scenes, scene_id


################ Main function #################

def find_scenes():
    
    start_time = time.time()

    # Get the path of the "scenes" folder from the config file
    folder_path = c.SEARCH_FOLDER

    # Load character IDs
    with open(c.CHARACTER_IDS, "r", encoding="utf-8") as file:
        author_id_mapping = json.load(file)

    # Find target character ID
    author = author_id_mapping[c.CHARACTER]

    t.log("base", f"\n## Finding scenes for {c.CHARACTER} with ID {author} in {folder_path}... ##\n")

    # Create an empty list to store scene starts and ends
    all_scenes = []
    scene_id = -1

    # Iterate over all JSON files in the server folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".json"):
                
                file_path = os.path.join(root, filename)
                t.log("debug", f"\tAnalysing {file_path}...")

                # Load JSON channel from file
                with open(file_path, "r", encoding="utf-8") as file:
                    json_data = json.load(file)

                    # Find scene starts and ends involving author
                    scenes, scene_id = find_scenes_in_channel(json_data, author, scene_id)

                    # Add the messages to the respective lists, can be more than one per channel
                    all_scenes.extend(scenes)

    t.save_to_json(all_scenes, c.OUTPUT_SCENES)

    t.log("info", f"\n\tScene output file created: {c.OUTPUT_SCENES}")

    # Uses the created JSONs to create a list of links to each scene start
    # output_scene_list()

    t.log("base", f"\n## Scene finding finished --- {time.time() - start_time:.2f} seconds --- ##\n")

if __name__ == "__main__":
    find_scenes()
    