import json
import os
import subprocess
from res import constants as c
from channel_list import get_channel_list 


def download_DMs():

    dm_channel_list = "res/DM_channel_list.json"
    with open(dm_channel_list, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    os.makedirs(os.path.join(c.SERVER_NAME, "DMs"), exist_ok=True)

    # Iterate through each object and download the channel
    for item in json_data:

        # Call the CLI command and capture its output
        cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export -c {item["id"]} -t {c.BOT_TOKEN} -o "{c.SERVER_NAME}/DMs/%C.json"'
        output = subprocess.check_output(cli_command, shell=True, text=True)
        print(output)



def download_channels():
    
    # get the list of channels to download
    get_channel_list()

    # run thru channel list to download it all
    download_DMs()

    
# invoke id_assigner.py

if __name__ == "__main__":
    download_channels()