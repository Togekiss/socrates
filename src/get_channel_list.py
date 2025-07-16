import subprocess
import json
import datetime
from tricks import set_path
set_path()
from res import constants as c

############### File summary #################

"""

This module gets or updates the list of channels from the server.

Main function: get_channel_list()

    This function calls the DiscordChatExporter CLI tool to get the list of all the server's channels.
    It processes the output and saves it as a JSON.

    Then it reads the list of categories from the scene_categories_cull.txt and dm_categories_keep.txt files,
    and removes the entries from the JSON data that have matching categories.

    Finally, the function groups the threads by category and saves the grouped data to the thread_channel_list.json file.

    The function does not return any value, but it saves the data to the specified JSON files.

"""

############### Functions #################

"""
group_threads(parsed_threads)
    Groups the parsed threads by category. I don't know why we need to do it like this.

    Args:
        parsed_threads (list): The list of parsed thread channels from the DiscordChatExporter CLI tool.

    Returns:
        list: organized thread data in JSON format
"""
def group_threads(parsed_threads):
    
    grouped_data = {}

    # Iterate through the JSON objects and group them by 'category'
    for obj in parsed_threads:
        category = obj['category']

        obj.pop('category')
        
        if category in grouped_data:
            grouped_data[category]['channels'].append(obj)
        else:
            grouped_data[category] = {'category': category, 'channels': [obj]}

    # Convert the grouped data to a list
    result = list(grouped_data.values())

    return result

"""
parse_output(output)

    Parses the output of the DiscordChatExporter CLI tool and returns two lists of channel data.

    The first list contains all non-thread channels, and the second list contains all thread channels.

    Args:
        output (str): The output of the DiscordChatExporter CLI tool.

    Returns:
        tuple: A tuple containing two lists of channel data in JSON format.
"""
def parse_output(output):

    parsed_channels = []
    parsed_threads = []
    lines = output.strip().split("\n")
    exported_at = datetime.datetime.now().isoformat(sep='T', timespec='microseconds')
    
    # Saving the 'parent channel' in case we encounter threads  
    parent_channel = None
    for line in lines:
        parts = line.split(" | ")
        
        # If it's a channel
        if len(parts) == 2:
            entry = {
                "id": parts[0].strip(),
                "category": parts[1].split(" / ")[0].strip(),
                "channel": parts[1].split(" / ")[1].strip(),
                "thread": False,
                "threadName": "",
                "exportedAt": exported_at
            }
            parsed_channels.append(entry)
            parent_channel = entry
        
        # If it's a thread
        if len(parts) == 3:
            entry = {
                "id": parts[0].replace('*', '').strip(),
                "category": parent_channel["category"],
                "channel": parent_channel["channel"],
                "thread": True,
                "threadName": parts[1].split(" / ")[1].strip(),
                "exportedAt": exported_at
            }
            parsed_threads.append(entry)

    return parsed_channels, parsed_threads

"""
save_to_json(data, file_path), read_categories_from_txt(file_path)

    Functions to write and read from files.

"""
def save_to_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def read_categories_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return {category.strip() for category in file}
"""
cull_json_remove(json_data, categories_to_remove), cull_json_keep(json_data, categories_to_keep)

    Functions to clean up the channel list.

"""
def cull_json_remove(json_data, categories_to_remove):
    return [entry for entry in json_data if entry["category"] not in categories_to_remove]

def cull_json_keep(json_data, categories_to_keep):
    return [entry for entry in json_data if entry["category"] in categories_to_keep]


################# Main function #################


def get_channel_list():

    # Call the CLI command and capture its output
    cli_command = f"dotnet DCE/DiscordChatExporter.Cli.dll channels -g {c.SERVER_ID} -t {c.BOT_TOKEN} --include-threads All"
    output = subprocess.check_output(cli_command, shell=True, text=True)

    # Process the output and create the desired JSON format
    parsed_channels, parsed_threads = parse_output(output)

    # Read the list of categories from the .txt files
    scene_categories_list = "res/scene_categories_cull.txt"
    categories_to_remove = read_categories_from_txt(scene_categories_list)
    
    dm_categories_list = "res/dm_categories_keep.txt"
    categories_to_keep = read_categories_from_txt(dm_categories_list)

    # Cull the JSON data by removing the entries with matching categories
    scene_channel_list = cull_json_remove(parsed_channels, categories_to_remove)
    thread_channel_list = cull_json_remove(parsed_threads, categories_to_remove)
    dm_channel_list = cull_json_keep(parsed_channels, categories_to_keep)
    
    grouped_threads = group_threads(thread_channel_list)
    
    # Save the culled JSON data back to the same file
    json_file_path = "res/scene_channel_list.json"
    save_to_json(scene_channel_list, json_file_path)

    json_file_path = "res/DM_channel_list.json"
    save_to_json(dm_channel_list, json_file_path)

    json_file_path = "res/thread_channel_list.json"
    save_to_json(grouped_threads, json_file_path)

if __name__ == "__main__":
    get_channel_list()
