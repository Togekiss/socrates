import datetime
import json
import time
import tricks as t
t.set_path()
from res import constants as c
from get_channel_list import get_channel_list 
from merge import merge
from id_assigner import id_assigner


################# File summary #################

"""

This module downloads a backup of all channels from the server.

Main function: export_channels()

    This script downloads all channels from the server specified in the constants.py file, either the full history or from a specified date.
    If there is no previous backup, downloads all channels from the server.
    If there is a previous backup, downloads all channels from the day before the last backup and merges them to the main files.
    Then, assigns a proper ID to each character.
    
"""


################# Functions #################

"""
get_last_exported()

    Returns the date of the last export in ISO format as a string or None if there is no previous backup.

    The date is retrieved from channel_list.json.

    Note: Backups are dated as a whole. This assumes the whole list of channels was downloaded at that time.
          If the export was interrupted, this does NOT keep track of which channels were downloaded and which weren't.
"""
def get_last_exported():
    
    date = None
    file = c.CHANNEL_LIST

    try:
        # Try to load JSON data from the file
        with open(file, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
            date = json_data["exportedAt"]

    except FileNotFoundError:
        # Handle the case when the file doesn't exist
        date = None

    return date

"""
set_day_before(timestamp_str)

    Adjusts the given timestamp by subtracting one day to ensure downloading the whole update.

    Args:
        timestamp_str (str): The original timestamp in ISO format.

    Returns:
        str: The adjusted timestamp in ISO format, representing the day before the original.
"""
def set_day_before(timestamp_str):

    # Parse the timestamp into a datetime object
    timestamp = datetime.datetime.fromisoformat(timestamp_str)

    # Subtract one day (24 hours) from the timestamp
    new_timestamp = timestamp - datetime.timedelta(days=1)

    # Format the new timestamp back into the original format
    new_timestamp_str = new_timestamp.isoformat()

    return new_timestamp_str


"""
export_category(item, after, type)

    Downloads set of channels or threads.

    For each channel, DCE is called to download the messages and store them in JSON format, either the full history or from a specified date.
    Downloads are run in parallel in groups of 3 or 5 to improve performance.

    Args:
        item (dict): The category data in JSON format.
        after (str, optional): The timestamp of the last export in ISO format. If not provided, downloads the full history.
        type (str, optional): The type of channels to download, should be "channels" or "threads". Defaults to "channels".

    Returns:
        None, but saves the downloaded messages to JSON files.
"""
def export_category(item, after, type="channels"):

    category = item["category"].replace(":", "_")
    folder = c.SERVER_NAME if after is None else "Update"
    path = f"{folder}/{item["position"]}# {category}/%C.json" if type == "channels" else f"{folder}/{item["position"]}# {category}/Threads/%C.json"
    after = "" if after is None else "--after " + after

    # Call the CLI command and capture its output

    channels = item[type]
    group_size = 3 if category == "Text and Calls" else 5
    for i in range(0, len(channels), group_size):

        group = channels[i:i + group_size]

        channel_ids = ""
        for channel in group:
            channel_ids = channel_ids + " " + channel["id"]

        cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export --parallel {group_size} -c {channel_ids} -t {c.BOT_TOKEN} -f Json -o "{path}" --locale "en-GB" {after} --fuck-russia'
        t.run_command(cli_command)

"""
export_from_list(after)

    Opens the channel list in the file channel_list.json, and downloads the channels of each category.

    Args:
        after (str, optional): The timestamp of the last export in ISO format. If not provided, downloads the full history.

    Returns:
        None, but saves the downloaded messages to JSON files.
"""
def export_from_list(after):

    with open(c.CHANNEL_LIST, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    # for each category, get channel and thread list
    for item in json_data["categories"]:

        t.debug(f"\n\tExporting channels from '{item['category']}'...\n")

        export_category(item, after, "channels")

        if len(item["threads"]) > 0:
            export_category(item, after, "threads")

################# Main function ################

def export_channels():

    print(f"\n# Exporting a backup of the server {c.SERVER_NAME}...  #\n")
    
    # check if there's already a backup
    date = get_last_exported()
    
    # if there already was a backup, only download from a day before it
    if date is not None:
        t.debug(f'\tThe last backup was downloaded at {date}')
        after = set_day_before(date)
        t.debug(f'\tWill download updates after {after}\n')
    
    # if there was none, download from scratch
    else:
        t.debug('\tNo previous backup was found. Downloading a full backup...\n')
        after = None

    # refresh the list of channels to download to find new channels
    get_channel_list()

    start_time = time.time()

    # run through channel list to download it all   
    print("\tExporting channels... This may take several minutes\n") 
     
    export_from_list(after)

    # merge the updates to the main files
    if date is not None:
        t.debug("\n\tMerging the update to the main backup...\n") 
        merge()

    # assign a proper ID to each character
    t.debug("\n\tGenerating IDs for character bots...\n") 
    id_assigner()
    
    print(f"\n# Export finished --- {time.time() - start_time:.2f} seconds --- #\n")


if __name__ == "__main__":
    export_channels()
    