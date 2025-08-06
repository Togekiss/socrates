import datetime
import time
import os
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
set_hour(adjustment, timestamp_str)

    Adjusts the given timestamp by adding or removing one hour to ensure downloading the whole scene.

    Args:
        adjustment (str): "before" or "after".
        timestamp_str (str): The original timestamp in ISO format.

    Returns:
        str: The adjusted timestamp in ISO format.
"""
def set_hour(adjustment, timestamp_str):

    # Parse the timestamp into a datetime object
    timestamp = datetime.datetime.fromisoformat(timestamp_str)

    if adjustment == "before":
        # Substract one hour from the timestamp
        new_timestamp = timestamp - datetime.timedelta(hours=1)

    elif adjustment == "after":
        # Add one hour to the timestamp
        new_timestamp = timestamp + datetime.timedelta(hours=1)

    else:
        # Do nothing
        new_timestamp = timestamp

    # Format the new timestamp back into the original format
    new_timestamp_str = new_timestamp.isoformat()

    return new_timestamp_str


################# Main function ################

def export_scenes():

    t.log("base", f"\n##  Exporting all scenes with '{c.CHARACTER}'...  ##\n")
    t.log("base", "This may take a few minutes...\n")
    
    start_time = time.time()

    # Open the JSON files
    scenes = t.load_from_json(c.OUTPUT_SCENES)

    t.log("info", f"\tLoaded scene information for {len(scenes)} scenes\n")

    folder = f"out/{c.CHARACTER}"
    os.makedirs(folder, exist_ok=True)

    # for each scene
    for i, scene in enumerate(scenes):

        t.log("info", f"\tDownloading scene {i+1} out of {len(scenes)}...")

        # get start date
        date = set_hour("before", scene['start']['timestamp'])
        channel = scene['channelId']

        t.log("debug", f"\t  Scene in '{scene['channel']}' starts at {date}")
        
        # find if it has an end message
        end = scene.get('end', None)

        if end == None or end == "":
            t.log("debug", f"\t  Scene has no end message")
            has_end = ""

        else:
            # find end date
            end_date = set_hour("after", scene['end']['timestamp'])

            t.log("debug", f"\t  Scene ends at {end_date}")
            has_end = f"--before {end_date}"

        # download channel from date to end_date
        cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export -c {channel} -t {c.BOT_TOKEN} -f HtmlDark -o "{folder}/%a - %C.html" --locale "en-GB" --after {date} {has_end} --fuck-russia'
        t.run_command(cli_command, 2)

        t.log("debug", f"\tScene downloaded\n")
    
    t.log("base", f"\n##  Finished downloading all scenes! --- {time.time() - start_time:.2f} seconds --- ##\n")
        
if __name__ == "__main__":
    export_scenes()