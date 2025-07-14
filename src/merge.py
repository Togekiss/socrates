import json
import os
import shutil
import time
from set_path import set_path
set_path()

def find_index(messages, id, base=0):
    
    index = None
    for i, message in enumerate(messages[base:], start=base):
        if message['id'] == id:
            index = i
            break

    return index

def update_channel_data(old_data, update_data):
    
    # Extract messages from both JSONs
    full_messages = old_data["messages"]
    update_messages = update_data["messages"]

    # set counters
    full_index = 0
    update_index = 0

    # For each new message
    for i, new_message in enumerate(update_messages):
        
        # keep track of the message being evaluated
        update_index = i

        # Extract the ID to look for
        id = update_messages[i]["id"]

        # Look for it in the old list - only counting from last message found
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



def merge():
    # Folders
    update_folder = 'Update'
    old_folder = 'Elysium'

    for foldername, subfolders, filenames in os.walk(update_folder):
        for filename in filenames:
            update_file_path = os.path.join(foldername, filename)
            old_file_path = os.path.join(old_folder, os.path.relpath(update_file_path, start=update_folder))

            # Check if an equivalent file exists in the "Old" folder
            
            # If it does, merge the two files
            if os.path.exists(old_file_path):
                merge_channel(old_file_path, update_file_path)

            else:
                # If not, create the necessary subfolders in "Old" to maintain the same directory tree
                os.makedirs(os.path.dirname(old_file_path), exist_ok=True)

                # Copy the file from "Update" to "Old"
                shutil.copy2(update_file_path, old_file_path)
                print(f"Copied: {update_file_path} to {old_file_path}")

    
    print("All channels merged")


if __name__ == "__main__":
    
    start_time = time.time()
    print("Merging started...")
    merge()
    print("Merging finished --- %s seconds ---" % (time.time() - start_time))
