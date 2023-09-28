import json


def find_index(messages, id, base=0):
    
    index = None
    for i, message in enumerate(messages[base:], start=base):
        if message['id'] == id:
            index = i
            break

    return index

def update_channel(old_data, update_data):
    
    # Extract messages from both JSON
    full_messages = old_data["messages"]
    update_messages = update_data["messages"]

    # set counters
    full_index = 0
    update_index = 0

    # For each new message
    for i, new_message in enumerate(update_messages):
        
        # keep track of the message being evaluated
        update_index = i

        # Extract the ID to look for
        id = update_messages[i]["id"]

        # Look for it in the old list - only counting from last message found
        index = find_index(full_messages, id, full_index)
        
        # Check if the message was found
        
        # If not, exit
        if index is None:
            break

        # If found, update the message and continue
        else:
            full_index = index
            full_messages[full_index] = new_message

    # Append the rest of the messages
    full_messages.extend(update_messages[update_index:])
          
    # Update metadata and messages to the whole JSON 
    old_data['exportedAt'] = update_data['exportedAt']
    old_data['messageCount'] = len(full_messages)
    old_data['messages'] = full_messages

    return old_data


if __name__ == "__main__":
    # Folders
    # TODO change for 'for each file in Update, get its full counterpart. if it doesnt exist, copy the whole file'
    full = "Elysium/Scenes/Rosenfeld Mansion/r-garden.json"
    update = "Update/Scenes/Rosenfeld Mansion/r-garden.json"

    # Load data from full
    with open(full, "r", encoding="utf-8") as old_file:
        old_data = json.load(old_file)

    # Load data from update
    with open(update, "r", encoding="utf-8") as update_file:
        update_data = json.load(update_file)

    # Evaluate and merge new messages to old channel history
    merged_data = update_channel(old_data, update_data)

    with open("merged.json", "w", encoding="utf-8") as merged_file:
        json.dump(merged_data, merged_file, indent=4)

    print("Messages merged and saved to merged.json")



