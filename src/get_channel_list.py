import time, datetime
import tricks as t
t.set_path()
from res import constants as c

############### File summary #################

"""

This module gets or updates the list of channels from the server.

Main function: get_channel_list()

    This function calls the DiscordChatExporter CLI tool to get the list of all the server's channels.
    It processes the output and saves it as a JSON.

    Then it reads the list of categories to ignore from the config file,
    and removes the entries from the JSON data that have matching categories.

    Finally, the function saves the data to a JSON file.

    The function does not return any value, but it saves the data to the specified JSON file.

"""

############### Functions #################


"""
parse_output(output)

    Parses the output of the DiscordChatExporter CLI tool and returns a list of channel data.

    Args:
        output (str): The output of the DiscordChatExporter CLI tool.

    Returns:
        dict: A list of channel data in JSON format.
"""

def parse_output(output):

    t.debug("\tParsing the list of channels...")

    lines = output.strip().split("\n")
    exported_at = datetime.datetime.now().isoformat(sep='T', timespec='microseconds')

    # Base object
    backup_data = {
        "id": c.SERVER_ID,
        "name": c.SERVER_NAME,
        "exportedAt": exported_at,
        "categories": []
    }

    category_list = []
    
    # Saving the 'parent channel' in case we encounter threads  
    parent_channel = None
    for line in lines:

        #t.debug("\t\t Analyzing: ", line)

        parts = line.split(" | ")
        
        # If it's a channel
        if len(parts) == 2:
            entry = {
                "id": parts[0].strip(),
                "category": parts[1].split(" / ")[0].strip(),
                "channel": parts[1].split(" / ")[1].strip(),
                "isThread": False,
                "thread": "",
            }
            # save it as a reference
            parent_channel = entry
        
        # If it's a thread
        if len(parts) == 3:
            entry = {
                "id": parts[0].replace('*', '').strip(),
                "category": parent_channel["category"],
                "channel": parent_channel["channel"],
                "isThread": True,
                "thread": parts[1].split(" / ")[1].strip(),
            }

        # If we encountered a new category
        if entry["category"] not in category_list:

            # Save it in the list
            category_list.append(entry["category"])

            # Create a new category
            category_data = {
                "category": entry["category"],
                "position": len(category_list) + 1,
                "channels": [],
                "threads": []
            }

            # Add it to the data
            backup_data["categories"].append(category_data)

        channel_data = {
            "id": entry["id"],
            "channel": entry["channel"],
            "position": len(backup_data["categories"][category_list.index(entry["category"])]["channels"]) + 1
        }

        # Add the channel to the category
        if entry["isThread"]:
            channel_data["thread"] = entry["thread"]

            # calculate "threadPosition" based on how many threads in the category have the same channel
            thread_position = 1
            for thread in backup_data["categories"][category_list.index(entry["category"])]["threads"]:
                if thread["channel"] == entry["channel"]:
                    thread_position += 1
            channel_data["threadPosition"] = thread_position
            
            backup_data["categories"][category_list.index(entry["category"])]["threads"].append(channel_data)
        
        else:
            backup_data["categories"][category_list.index(entry["category"])]["channels"].append(channel_data)

    t.debug(f"\tFound {len(lines)} channels in {len(backup_data['categories'])} categories\n")

    return backup_data

"""
remove_categories(json_data, categories_to_remove), keep_categories(json_data, categories_to_keep)
    Function to clean up the channel list.
"""
def remove_categories(json_data, categories_to_remove):
    return [entry for entry in json_data if entry["category"] not in categories_to_remove]
    

def keep_categories(json_data, categories_to_keep):
    return [entry for entry in json_data if entry["category"] in categories_to_keep]


################# Main function #################


def get_channel_list():

    print(f"\n###  Getting a list of all channels from the server {c.SERVER_NAME}...  ###\n")
    print("\tThis may take a few minutes...\n")

    start_time = time.time()

    # Call the CLI command and capture its output
    cli_command = f"dotnet DCE/DiscordChatExporter.Cli.dll channels -g {c.SERVER_ID} -t {c.BOT_TOKEN} --include-threads all"
    code, output = t.run_command(cli_command)

    t.debug("\tGot a list of channels from DCE\n")

    # Process the output and create the desired JSON format
    channel_list = parse_output(output)

    t.debug("\tCleaning the list of channels...")

    channel_list["categories"] = remove_categories(channel_list["categories"], c.CATEGORIES_TO_IGNORE)

    t.debug(f"\tRemoved {len(c.CATEGORIES_TO_IGNORE)} categories")
    t.debug(f"\tKept {len(channel_list['categories'])} categories\n")

    t.save_to_json(channel_list, c.CHANNEL_LIST)
    t.debug(f"\tSaved the list of channels to {c.CHANNEL_LIST}\n")

    print(f"\n### Channel list finished --- {time.time() - start_time:.2f} seconds --- ###\n")

if __name__ == "__main__":
    get_channel_list()
