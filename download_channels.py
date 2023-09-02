import json
import subprocess
import time
from res import constants as c
from get_channel_list import get_channel_list 


def download_DMs():

    dm_channel_list = "res/DM_channel_list.json"
    with open(dm_channel_list, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    # Iterate through each object and download the channel
    for item in json_data:

        # Call the CLI command and capture its output
        cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export -c {item["id"]} -t {c.BOT_TOKEN} -f Json -o "{c.SERVER_NAME}/DMs/%C.json" --fuck-russia'
        output = subprocess.check_output(cli_command, shell=True, text=True)
        print(output)

def download_scenes():

    dm_channel_list = "res/scene_channel_list.json"
    with open(dm_channel_list, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    # Iterate through the list and download channels
    group_size = 4
    for i in range(0, len(json_data), group_size):
        group = json_data[i:i + group_size]

        channel_ids = ""
        for item in group:
            channel_ids = channel_ids + " " + item["id"]

        # Call the CLI command and capture its output
        cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export --parallel 4 -c {channel_ids} -t {c.BOT_TOKEN} -f Json -o "{c.SERVER_NAME}/Scenes/%T/%C.json" --fuck-russia'
        output = subprocess.check_output(cli_command, shell=True, text=True)
        print(output)

def download_threads():

    dm_channel_list = "res/thread_channel_list.json"
    with open(dm_channel_list, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    # Iterate through each object and download the channel
    for item in json_data:

        category = item["category"].replace(":", "_")

        # Call the CLI command and capture its output
        cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export -c {item["id"]} -t {c.BOT_TOKEN} -f Json -o "{c.SERVER_NAME}/Scenes/{category}/Threads/%C.json" --fuck-russia'
        output = subprocess.check_output(cli_command, shell=True, text=True)
        print(output)

def download_channels():
    
    # get the list of channels to download
    get_channel_list()

    # run thru channel list to download it all
    download_DMs()
    download_scenes()
    download_threads()

    
# invoke id_assigner.py

if __name__ == "__main__":
    
    start_time = time.time()
    download_channels()
    print("Process finished --- %s seconds ---" % (time.time() - start_time))