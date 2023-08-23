import subprocess
import json

def get_bot_token():
    with open("res/bot_token.txt", "r", encoding="utf-8") as file:
        content = file.readline().strip()

    return content

def get_server_token():
    with open("res/server_token.txt", "r", encoding="utf-8") as file:
        content = file.readline().strip()

    return content

def parse_output(output):
    parsed_data = []
    lines = output.strip().split("\n")

    for line in lines:
        parts = line.split(" | ")
        if len(parts) == 2:
            entry = {
                "id": parts[0].strip(),
                "category": parts[1].split(" / ")[0].strip(),
                "channel": parts[1].split(" / ")[1].strip()
            }
            parsed_data.append(entry)

    return parsed_data

def save_to_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def read_categories_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return {category.strip() for category in file}

def cull_json_remove(json_data, categories_to_remove):
    return [entry for entry in json_data if entry["category"] not in categories_to_remove]

def cull_json_keep(json_data, categories_to_keep):
    return [entry for entry in json_data if entry["category"] in categories_to_keep]

def main():
    #get the tokens from local file
    bot = get_bot_token()
    server = get_server_token()
    
    # Call the CLI command and capture its output
    cli_command = f"dotnet DCE/DiscordChatExporter.Cli.dll channels -g {server} -t {bot}"
    output = subprocess.check_output(cli_command, shell=True, text=True)

    # Process the output and create the desired JSON format
    parsed_data = parse_output(output)

    # Read the list of categories from the .txt files
    scene_categories_list = "res/scene_categories_cull.txt"
    categories_to_remove = read_categories_from_txt(scene_categories_list)
    
    dm_categories_list = "res/dm_categories_keep.txt"
    categories_to_keep = read_categories_from_txt(dm_categories_list)

    # Cull the JSON data by removing the entries with matching categories
    scene_channel_list = cull_json_remove(parsed_data, categories_to_remove)
    dm_channel_list = cull_json_keep(parsed_data, categories_to_keep)
    
    # Save the culled JSON data back to the same file
    json_file_path = "res/scene_channel_list.json"
    save_to_json(scene_channel_list, json_file_path)

    json_file_path = "res/DM_channel_list.json"
    save_to_json(dm_channel_list, json_file_path)

if __name__ == "__main__":
    main()