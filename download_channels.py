import datetime
import json
import os
import subprocess
import time
from res import constants as c
from get_channel_list import get_channel_list 
from merge import merge
from id_assigner import id_assigner


def get_last_exported():
    date = None
    file = "res/DM_channel_list.json"

    try:
        # Try to load JSON data from the file
        with open(file, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
            date = json_data[0]["exportedAt"]

    except FileNotFoundError:
        # Handle the case when the file doesn't exist
        date = None

    return date

def set_day_before(timestamp_str):

    # Parse the timestamp into a datetime object
    timestamp = datetime.datetime.fromisoformat(timestamp_str)
    # Subtract one day (24 hours) from the timestamp
    new_timestamp = timestamp - datetime.timedelta(days=1)
    # Format the new timestamp back into the original format
    new_timestamp_str = new_timestamp.isoformat()

    return new_timestamp_str


def download_DMs(after):

    channel_list = "res/DM_channel_list.json"
    with open(channel_list, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    # Iterate through the list and download channels
    group_size = 3
    for i in range(0, len(json_data), group_size):
        group = json_data[i:i + group_size]

        channel_ids = ""
        for item in group:
            channel_ids = channel_ids + " " + item["id"]

        # Call the CLI command and capture its output

        # if there was no previous backup
        if after is None:
            cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export --parallel 3 -c {channel_ids} -t {c.BOT_TOKEN} -f Json -o "{c.SERVER_NAME}/DMs/%C.json" --dateformat "dd/MM/yyyy HH:mm" --fuck-russia'

        # If there was a previous backup
        else:
            cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export --parallel 3 -c {channel_ids} -t {c.BOT_TOKEN} -f Json -o "Update/DMs/%C.json" --dateformat "dd/MM/yyyy HH:mm" --after {after} --fuck-russia'
        
        try:
            output = subprocess.check_output(cli_command, shell=True, text=True)
            print(output)

        except subprocess.CalledProcessError as e:
            pass

def download_scenes(after):

    channel_list = "res/scene_channel_list.json"
    with open(channel_list, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    # Iterate through the list and download channels
    group_size = 5
    for i in range(0, len(json_data), group_size):
        group = json_data[i:i + group_size]

        channel_ids = ""
        for item in group:
            channel_ids = channel_ids + " " + item["id"]

        # Call the CLI command and capture its output

        # if there was no previous backup
        if after is None: 
            cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export --parallel 5 -c {channel_ids} -t {c.BOT_TOKEN} -f Json -o "{c.SERVER_NAME}/Scenes/%T/%C.json" --dateformat "dd/MM/yyyy HH:mm" --fuck-russia'
        
        # If there was a previous backup
        else:
            cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export --parallel 5 -c {channel_ids} -t {c.BOT_TOKEN} -f Json -o "Update/Scenes/%T/%C.json" --dateformat "dd/MM/yyyy HH:mm" --after {after} --fuck-russia'

        try:
            output = subprocess.check_output(cli_command, shell=True, text=True)
            print(output)

        except subprocess.CalledProcessError as e:
            pass

def download_threads(after):

    channel_list = "res/thread_channel_list.json"
    with open(channel_list, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    # Iterate through each object and download the channel
    for item in json_data:

        category = item["category"].replace(":", "_")

        # Call the CLI command and capture its output

        channels = item["channels"]
        group_size = 5
        for i in range(0, len(channels), group_size):

            group = channels[i:i + group_size]

            channel_ids = ""
            for channel in group:
                channel_ids = channel_ids + " " + channel["id"]

            # if there was no previous backup
            if after is None: 
                cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export --parallel 5 -c {channel_ids} -t {c.BOT_TOKEN} -f Json -o "{c.SERVER_NAME}/Scenes/{category}/Threads/%C.json" --dateformat "dd/MM/yyyy HH:mm" --fuck-russia'
            
            # If there was a previous backup
            else:  
                cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export --parallel 5 -c {channel_ids} -t {c.BOT_TOKEN} -f Json -o "Update/Scenes/{category}/Threads/%C.json" --dateformat "dd/MM/yyyy HH:mm" --after {after} --fuck-russia'

            try:
                output = subprocess.check_output(cli_command, shell=True, text=True)
                print(output)

            except subprocess.CalledProcessError as e:
                pass



def download_channels():
    
    # check if there's already a backup
    date = get_last_exported()
    print(f'last exported: {date}')

    # get the list of channels to download
    get_channel_list()

    # if there already was a backup, only download from a day before it
    if date is not None:
        after = set_day_before(date)
        print(f'day before: {after}')
    
    # if there was none, download from scratch
    else:
        after = None


    # run through channel list to download it all   

    print("Downloading channels...") 
     
    download_DMs(after)
    download_scenes(after)
    download_threads(after)

    # merge the updates to the main files
    if date is not None:
        print("Merging channels...") 
        merge()

    # assign a proper ID to each character
    print("Assigning IDs...") 
    id_assigner()
    
    

if __name__ == "__main__":
    
    start_time = time.time()
    print("Download starting...")
    download_channels()
    print("Download finished --- %s seconds ---" % (time.time() - start_time))