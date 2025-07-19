import json
import os
import shutil
import time
import tricks as t
t.set_path()
from res import constants as c

################# File summary #################

"""

This module merges the channel history files from the "Update" folder to the "Old" folder.

Main function: merge()

    The "Update" folder should contain the new channel history files exported by DCE.
    The "Old" folder should contain the old channel history files to be updated.

    This function will walk through all files in the "Update" folder and its subfolders.
    For each file, it will check if an equivalent file exists in the "Old" folder.
    If it does, it will merge the two files by appending new messages to the old file.
    If not, it will create the necessary subfolders in "Old" to maintain the same directory tree
    and copy the file from "Update" to "Old".

    Finally, it will debug a message indicating that all channels have been merged.

"""

################## Functions #################

"""
find_index(messages, id, base=0)

    Find the index of a message with a specified ID in a list of messages.

    Args:
        messages (list): A list of messages in JSON format, each containing an 'id' key.
        id (str): The ID of the message to find.
        base (int, optional): The starting index to begin the search at. Defaults to 0.

    Returns:
        int or None: The index of the message with the specified ID, or None if not found.
"""
def find_index(messages, id, base=0):
    
    index = None
    for i, message in enumerate(messages[base:], start=base):
        if message['id'] == id:
            index = i
            break

    return index


"""
update_channel_data(old_data, update_data)

    Updates the old channel history by merging it with the channel history update.

    This function iterates through the channel history update's messages.
    If the message is found in the old channel history, it is updated (to account for edited content).
    If the message is not found, the rest of the update is appended to the old channel history.
    Then, the updated metadata and full message history are saved back to the main backup.

    Args:
        old_data (dict): The old channel history in JSON format.
        update_data (dict): The new channel history in JSON format.

    Returns:
        dict: The updated channel history in JSON format.
"""
def update_channel_data(old_data, update_data):
    
    # Extract messages from both JSONs

    full_messages = old_data["messages"]
    update_messages = update_data["messages"]

    # set counters
    full_index = 0
    update_index = 0

    # For each new message in the update
    for i, new_message in enumerate(update_messages):
        
        # keep track of the message being evaluated
        update_index = i

        # Extract the ID to look for
        id = update_messages[i]["id"]

        # Look for it in the old list - only counting from last message evaluated
        index = find_index(full_messages, id, full_index)
        
        # Check if the message was found
        
        # If not, exit
        if index is None:
            break

        # If found, update the message and continue
        else:
            full_index = index
            full_messages[full_index] = new_message

    # Append the rest of the messages
    full_messages.extend(update_messages[update_index:])
          
    # Update metadata and messages to the whole JSON 
    old_data['exportedAt'] = update_data['exportedAt']
    old_data['messageCount'] = len(full_messages)
    old_data['messages'] = full_messages

    return old_data


"""
merge_channel(old, update)

    Merges the channel data from an update file into an existing old file.

    This function loads JSON data from two files: `old` and `update`.
    It merges the new channel messages from the `update` file into the existing
    channel history in the `old` file. The merged data is then saved back to the
    `old` file, maintaining a complete and up-to-date channel history.

    Args:
        old (str): The file path to the existing channel history file.
        update (str): The file path to the new channel update file.

    Returns:
        None, but saves the merged data to the `old` file.
"""
def merge_channel(old, update):
    
    # Load data from old file
    with open(old, "r", encoding="utf-8") as old_file:
        old_data = json.load(old_file)

    # Load data from update file
    with open(update, "r", encoding="utf-8") as update_file:
        update_data = json.load(update_file)

    # Evaluate and merge new messages to old channel history
    merged_data = update_channel_data(old_data, update_data)

    # save merged data to json
    with open(old, "w", encoding="utf-8") as merged_file:
        json.dump(merged_data, merged_file, indent=4)


################# Main function ################

def merge():
    
    start_time = time.time()

    # Folders
    update_folder = 'Update'
    old_folder = c.SERVER_NAME

    t.log("base", f"\n### Merging files from {update_folder} into {old_folder}...  ###\n")

    for foldername, subfolders, filenames in os.walk(update_folder):
        for filename in filenames:
            update_file_path = os.path.join(foldername, filename)
            old_file_path = os.path.join(old_folder, os.path.relpath(update_file_path, start=update_folder))

            # Check if an equivalent file exists in the "Old" folder
            
            # If it does, merge the two files
            if os.path.exists(old_file_path):
                t.log("debug", f"\tMerging {update_file_path} into {old_file_path}")
                merge_channel(old_file_path, update_file_path)

            else:
                # If not, create the necessary subfolders in "Old" to maintain the same directory tree
                os.makedirs(os.path.dirname(old_file_path), exist_ok=True)

                # Copy the file from "Update" to "Old"
                shutil.copy2(update_file_path, old_file_path)
                t.log("info", f"\tFound new file: Moving {update_file_path} to {old_file_path}")

    
    t.log("base", f"### Merging finished --- {time.time() - start_time} seconds --- ###\n")

if __name__ == "__main__":
    merge()
    
