import json
import os
import re
import unicodedata
from res import constants as c
from url_creator import url_creator

# Saves the info we need to create scene lists
def message_info(message, data, status, scene_id, i, other_authors=[]):

    msg = {
        "sceneId": scene_id,
        "id": message['id'],
        "timestamp": message['timestamp'],
        "content": message['content'],
        "index": i,
        "authorID": message['author']['id'],
        "category": data['channel']['category'],
        "channel": data['channel']['name'],
        "channelId": data['channel']['id'],
        "link": f"https://discord.com/channels/{data['guild']['id']}/{data['channel']['id']}/{message['id']}",
        "status": status,
        "otherAuthors": other_authors
    }

    return msg


def find_scenes_in_channel(data, target_author, scene_id):

    # REGEX to detect the end of a scene
    pattern = r"(?i)(?:`|```).*\n*.*\b(?:end|hold|close|dropped|offline|moved|moving|continu)\w*.{0,10}\n*(?:`|```)\n*(?:$|@.*|\W*)"
    pattern2 = r"(?i).*\n*(?:moved to #|moving to #|continued in #|DM END|END DM|\[end\]|\[read\])\w*.{0,20}\n*"
    
    # create arrays, in case there is more than one scene in a channel
    scene_starts = []
    scene_ends = []

    # set flags and counters
    active_scene = False
    author_missing_counter = 0

    # check if it's a thread; then it will only contain one scene so there's no need to check it all
    if data["channel"]["type"] != "GuildTextChat":
        
        other_authors= []

        #look at the first 5 messages 
        for message in data["messages"][:5]:
            
            author = int(message["author"]["id"])

            #save the other characters
            if author != target_author and author not in other_authors:
                other_authors.append(author)

            # if it contains the target author, we'll get the whole channel
            if not active_scene and author == target_author:

                active_scene = True
                scene_id = scene_id + 1

                # get the last message and check if the thread is open or closed
                last_message = data["messages"][-1]
                normalized_content = unicodedata.normalize("NFKD", last_message["content"])
                
                if re.search(pattern, normalized_content, flags=re.I) or re.search(pattern2, normalized_content, flags=re.I):
                    status = 'closed'
                else:
                    status = 'open'

        # save the start and the end of the thread
        if active_scene:
            start_msg = message_info(data["messages"][0], data, status, scene_id, 0, other_authors)
            scene_starts.append(start_msg)
            
            end_msg = message_info(data["messages"][-1], data, status, scene_id, len(data["messages"]), other_authors)
            scene_ends.append(end_msg)
            
            

                

    # if it's a channel, we will have to check the entirety of it
    else:

        for i, message in enumerate(data["messages"]):
            
            author = int(message["author"]["id"])
            
            # if we have no scene and we see our character, we mark it as a start of a scene
            if not active_scene and author == target_author:
                
                active_scene = True
                other_authors= []
                author_missing_counter = 0
                other_author_search = 0
                scene_id = scene_id + 1

                msg = message_info(message, data, 'open', scene_id, i)
                scene_starts.append(msg)

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
                    scene_starts[-1]["status"] = 'closed'
                    scene_starts[-1]["otherAuthors"] = other_authors

                    msg = message_info(message, data, 'closed', scene_id, i, other_authors)
                    scene_ends.append(msg)

                    continue
                
                # if it's been too many messages without the target author
                if author_missing_counter > len(other_authors)*5 and author not in other_authors:

                    # tag the scene as timed out
                    active_scene = False
                    scene_starts[-1]["status"] = 'timeout'

                    msg = message_info(message, data, 'timeout', scene_id, i, other_authors)
                    scene_ends.append(msg)

                # if it reaches the end of a channel while the scene is active
                if message == data["messages"][-1]:
                    scene_starts[-1]["otherAuthors"] = other_authors
        

    return scene_starts, scene_ends, scene_id

if __name__ == "__main__":

    # Get the path of the "scenes" folder in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_name = c.SEARCH_FOLDER
    folder_path = os.path.join(script_dir, folder_name)

    # Load character IDs
    with open("res/character_ids.json", "r", encoding="utf-8") as file:
        author_id_mapping = json.load(file)

    # Find target character ID
    author = author_id_mapping[c.CHARACTER]

    # Create an empty list to store scene starts and ends
    all_scene_starts = []
    all_scene_ends = []
    scene_id = -1

    # Iterate over all JSON files in the server folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(root, filename)

                # Load JSON data from file
                with open(file_path, "r", encoding="utf-8") as file:
                    json_data = json.load(file)

                    # Find scene starts and ends involving author
                    scene_starts, scene_ends, scene_id = find_scenes_in_channel(json_data, author, scene_id)

                    # Add the messages to the respective lists, can be more than one per channel
                    all_scene_starts.extend(scene_starts)
                    all_scene_ends.extend(scene_ends)

    # Create output JSON file for scene starts
    scene_starts_output = {
        "scenes": all_scene_starts
    }
    scene_starts_output_file = os.path.join(script_dir, "out/scene_starts.json")
    with open(scene_starts_output_file, "w", encoding="utf-8") as file:
        json.dump(scene_starts_output, file, indent=4)

    # Create output JSON file for scene ends
    scene_ends_output = {
        "scenes": all_scene_ends
    }
    scene_ends_output_file = os.path.join(script_dir, "out/scene_ends.json")
    with open(scene_ends_output_file, "w", encoding="utf-8") as file:
        json.dump(scene_ends_output, file, indent=4)

    print("scene starts output file created:", scene_starts_output_file)
    print("scene ends output file created:", scene_ends_output_file)

    # Uses the created JSONs to create a list of links to each scene start
    url_creator()