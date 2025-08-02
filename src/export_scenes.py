import datetime
import json
import os
import subprocess
import tricks as t
t.set_path()
from res import constants as c
from src.export_channels import set_day_before

################# File summary #################

"""

This module downloads all the found scenes from a given character as HTML files.

Main function: export_scenes()

    This script reads the scene starts and ends from the JSON files created by the find_scenes script.
    It creates a folder for the character and downloads each scene as an HTML file, using the DiscordChatExporter.
    If the scene doesn't have an end message, it will download the whole channel from the scene's start date.
    
"""

################# Functions #################

"""
set_hour_after(timestamp_str)

    Adjusts the given timestamp by adding one hour to ensure downloading the whole scene.

    Args:
        timestamp_str (str): The original timestamp in ISO format.

    Returns:
        str: The adjusted timestamp in ISO format, one hour later.
"""
def set_hour_after(timestamp_str):

    # Parse the timestamp into a datetime object
    timestamp = datetime.datetime.fromisoformat(timestamp_str)

    # Subtract one day (24 hours) from the timestamp
    new_timestamp = timestamp + datetime.timedelta(hours=1)

    # Format the new timestamp back into the original format
    new_timestamp_str = new_timestamp.isoformat()

    return new_timestamp_str

################# Main function ################

def export_scenes():

    # Open the JSON files
    with open('out/scene_starts.json', 'r', encoding="utf-8") as file:
        starts = json.load(file)
    
    with open('out/scene_ends.json', 'r', encoding="utf-8") as file:
        ends = json.load(file)

    folder = f"out/{c.CHARACTER}"
    os.makedirs(folder, exist_ok=True)

    # for each scene
    for scene in starts['scenes']:

        # get start date
        date = set_day_before(scene['timestamp'])
        channel = scene['channelId']

        t.log("debug", f"thread in {channel} started at {date}")
        
        # find if it has an end message
        id = scene['sceneId']
        end = next((e for e in ends['scenes'] if e["sceneId"] == id), None)

        if end == None:
            t.log("debug", f"{id} has no end\n")
            has_end = ""

        else:
            # find end date
            end_date = set_hour_after(end['timestamp'])

            t.log("debug", f"{id} has end, ended at {end_date}\n")
            has_end = f"--before {end_date}"

        # download channel from date to end_date
        cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export -c {channel} -t {c.BOT_TOKEN} -f HtmlDark -o "{folder}/%a - %C.html" --locale "en-GB" --after {date} {has_end} --fuck-russia'
        t.run_command(cli_command, 2)
        
if __name__ == "__main__":
    export_scenes()