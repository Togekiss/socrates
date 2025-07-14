import datetime
import json
import os
import subprocess
from set_path import set_path
set_path()
from res import constants as c

def set_day_before(timestamp_str):

    # Parse the timestamp into a datetime object
    timestamp = datetime.datetime.fromisoformat(timestamp_str)
    # Subtract one day (24 hours) from the timestamp
    new_timestamp = timestamp - datetime.timedelta(days=1)
    # Format the new timestamp back into the original format
    new_timestamp_str = new_timestamp.isoformat()

    return new_timestamp_str

def set_hour_after(timestamp_str):

    # Parse the timestamp into a datetime object
    timestamp = datetime.datetime.fromisoformat(timestamp_str)
    # Subtract one day (24 hours) from the timestamp
    new_timestamp = timestamp + datetime.timedelta(hours=1)
    # Format the new timestamp back into the original format
    new_timestamp_str = new_timestamp.isoformat()

    return new_timestamp_str

def file_creator():

    # Open the JSON files
    with open('out/scene_starts.json', 'r', encoding="utf-8") as file:
        starts = json.load(file)
    
    with open('out/scene_ends.json', 'r', encoding="utf-8") as file:
        ends = json.load(file)

    folder = f"out/{c.CHARACTER}"
    os.makedirs(folder, exist_ok=True)

    # for each scene
    for scene in starts['scenes']:

        # get date
        date = set_day_before(scene['timestamp'])
        channel = scene['channelId']

        print(f"thread in {channel} started at {date}")
        
        # find if it has an end message
        id = scene['sceneId']
        end = next((e for e in ends['scenes'] if e["sceneId"] == id), None)


        if end == None:
            print(f"{id} has no end\n")
            has_end = ""
            # download channel from date

        else:

            # find end date
            end_date = set_hour_after(end['timestamp'])

            print(f"{id} has end, ended at {end_date}\n")
            has_end = f"--before {end_date}"
            # download channel from date to end_datet
        
        cli_command = f'dotnet DCE/DiscordChatExporter.Cli.dll export -c {channel} -t {c.BOT_TOKEN} -f HtmlDark -o "{folder}/%a - %C.html" --dateformat "dd/MM/yyyy HH:mm" --after {date} {has_end} --fuck-russia'
        
        try:
            output = subprocess.check_output(cli_command, shell=True, text=True)
            print(output)

        except subprocess.CalledProcessError as e:
            pass
        
if __name__ == "__main__":
    file_creator()