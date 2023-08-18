import json
import os
import re
import unicodedata

def find_thread_starts(data, target_author):
    pattern = r"(?i)(?:`|```).*\n*\b(?:end|hold|close|dropped|offline|moved|moving|continu)\w*.{0,10}\n*(?:`|```)\n*(?:$|@.*|\W*)"
    pattern2 = r"(?i)(?:`|```)\n*.*\b(?:moved|moving|continu)\w*.{0,15}\n*(?:`|```)\n*(?:$|@.*|\W*)"
    messages = data["messages"]
    thread_starts = []
    thread_ends = []

    active_thread = False
    message_count = 0

    for message in messages:
        author = message["author"]["name"]

        # thread begins
        if not active_thread and target_author in author:
            active_thread = True
            message_count = 0
            message["category"] = data['channel']['category']
            message["channel"] = data['channel']['name']
            message["status"] = 'active'
            message["link"] = f"https://discord.com/channels/{data['guild']['id']}/{data['channel']['id']}/{message['id']}"
            thread_starts.append(message)

        if active_thread: 

            # accounts for some leeway, resets if characters appear again
            if target_author in author:
                message_count = 0
            else:
                message_count += 1
            
            # Convert the message content and pattern to normalized form
            normalized_content = unicodedata.normalize("NFKD", message["content"])
            normalized_pattern = unicodedata.normalize("NFKD", pattern)
            
            # if there's any END or similar tag
            if re.search(normalized_pattern, normalized_content):
                active_thread = False
                message["category"] = data['channel']['category']
                message["channel"] = data['channel']['name']
                thread_starts[-1]["status"] = 'end'
                message["status"] = 'end'
                message["link"] = f"https://discord.com/channels/{data['guild']['id']}/{data['channel']['id']}/{message['id']}"
                thread_ends.append(message)
                continue
            
            # if it's clear they left
            if message_count > 15:
                active_thread = False
                message["category"] = data['channel']['category']
                message["channel"] = data['channel']['name']
                thread_starts[-1]["status"] = 'timeout'
                message["status"] = 'timeout'
                message["link"] = f"https://discord.com/channels/{data['guild']['id']}/{data['channel']['id']}/{message['id']}"
                thread_ends.append(message)
        

    return thread_starts, thread_ends


# Get the path of the "Kaminashi" folder in the same directory as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
folder_name = "Elysium/Threads"
author = "Lucien Deimos"
folder_path = os.path.join(script_dir, folder_name)

# Create an empty list to store thread starts and ends
all_thread_starts = []
all_thread_ends = []

# Iterate over all JSON files in the "Kaminashi" folder and its subfolders
for root, dirs, files in os.walk(folder_path):
    for filename in files:
        if filename.endswith(".json"):
            file_path = os.path.join(root, filename)

            # Load JSON data from file
            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)

                # Find thread starts and ends involving author
                thread_starts, thread_ends = find_thread_starts(json_data, author)

                # Add the messages to the respective lists
                all_thread_starts.extend(thread_starts)
                all_thread_ends.extend(thread_ends)

# Create output JSON file for thread starts
thread_starts_output = {
    "thread_starts": all_thread_starts
}
thread_starts_output_file = os.path.join(script_dir, "out/thread_starts.json")
with open(thread_starts_output_file, "w", encoding="utf-8") as file:
    json.dump(thread_starts_output, file, indent=4)

# Create output JSON file for thread ends
thread_ends_output = {
    "thread_ends": all_thread_ends
}
thread_ends_output_file = os.path.join(script_dir, "out/thread_ends.json")
with open(thread_ends_output_file, "w", encoding="utf-8") as file:
    json.dump(thread_ends_output, file, indent=4)

print("Thread starts output file created:", thread_starts_output_file)
print("Thread ends output file created:", thread_ends_output_file)
