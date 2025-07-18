import os
import json
import re
import tricks as t
t.set_path()
from res import constants as c

################# File summary #################

"""

DiscordChatExporter is not able to keep track of a channel's position inside its category,
so this module renames the exported JSON files to include the position numbers saved in the channel list.

This module is meant to be run after `src/export_channels.py`. It will assume the backup folder contains the channels of the channel list.

Main function: sort_exported_files(base_folder)

    This script loads the channel list from the JSON file.

    Then, it goes through the categories, channels and threads reflected in the JSON list.
    For each channel and thread, it finds the corresponding JSON file and renames it to include the position number.

    Note: If the files were already numbered, they won't match the channel list anymore- so they won't be renamed.

    Args:
        base_folder (str): The base folder where the exported JSON files are stored.

"""

################# Functions #################

"""
super_normalize(text)

    Aggressively normalizes a string by removing non-alphanumeric characters and converting it all to lowercase.

"""
def super_normalize(text):
    return re.sub(r'[^a-zA-Z0-9-]', '', text).lower()


"""
find_channel_file(folder, target_name)

    Finds a channel file in the specified folder that matches the target name.

    Args:
        folder (str): The folder to search in.
        target_name (str): The target name to search for.

    Returns:
        str: The actual filename of the matching channel file, or None if not found.
"""
def find_channel_file(folder, target_name):

    normalized_target = super_normalize(target_name)

    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            
            file_name = os.path.splitext(filename)[0]

            if super_normalize(file_name) == normalized_target:
                return filename  # Return actual filename with full characters
            
    return None

################# Main function #################

def sort_exported_files(base_folder):

    print(f"\n###  Adding position numbers to channel files in {base_folder}...  ###\n")

    json_path = c.CHANNEL_LIST

    with open(json_path, 'r', encoding='utf-8') as f:
        channel_list = json.load(f)

    # For each category in the channel list
    for category in channel_list.get("categories", []):

        category_pos = category["position"]
        category_name = category["category"].replace(":", "_")
        category_folder = os.path.join(base_folder, f"{category_pos}# {category_name}")

        # Rename channel files
        for channel in category.get("channels", []):

            channel_name = channel["channel"]
            channel_pos = channel["position"]

            # Find the file that corresponds to the channel
            old_filename = find_channel_file(category_folder, channel_name)

            if old_filename:

                new_filename = f"{channel_pos}# {old_filename}"

                src = os.path.join(category_folder, old_filename)
                dst = os.path.join(category_folder, new_filename)
                os.rename(src, dst)

                t.debug(f"✅ Renamed channel: {old_filename} → {new_filename}")

            else:
                t.debug(f"❌ Channel file not found: {channel_name}")

        # Rename thread files
        threads_folder = os.path.join(category_folder, "Threads")

        for thread in category.get("threads", []):

            channel_name = thread["channel"]
            channel_pos = thread["position"]
            thread_title = thread["thread"]
            thread_pos = thread["threadPosition"]

            # Find the file that corresponds to the thread
            old_filename = find_channel_file(threads_folder, thread_title)

            if old_filename:

                new_filename = f"{channel_pos}-{thread_pos}# {old_filename}"

                src = os.path.join(threads_folder, old_filename)
                dst = os.path.join(threads_folder, new_filename)
                os.rename(src, dst)

                t.debug(f"✅ Renamed thread: {old_filename} → {new_filename}")

            else:
                t.debug(f"❌ Thread file not found: {thread_title}")
    
    print(f"### Finished renaming files ###\n")

if __name__ == "__main__":
    sort_exported_files(c.SERVER_NAME)
