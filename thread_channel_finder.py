import subprocess
import json

def get_token():
    with open("res/bot_token.txt", "r", encoding="utf-8") as file:
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

def cull_json(json_data, categories_to_remove):
    return [entry for entry in json_data if entry["category"] not in categories_to_remove]

def main():
    #get the bot token from local file
    token = get_token()
    
    # Call the CLI command and capture its output
    cli_command = "dotnet DCE/DiscordChatExporter.Cli.dll channels -g 857848490683269161 -t " + token
    output = subprocess.check_output(cli_command, shell=True, text=True)

    # Process the output and create the desired JSON format
    parsed_data = parse_output(output)

    # Read the list of categories from the .txt file
    categories_txt_file = "res/thread_categories_cull.txt"
    categories_to_remove = read_categories_from_txt(categories_txt_file)

    # Cull the JSON data by removing the entries with matching categories
    culled_json_data = cull_json(parsed_data, categories_to_remove)

    # Save the culled JSON data back to the same file
    json_file_path = "res/thread_channel_list.json"
    save_to_json(culled_json_data, json_file_path)

if __name__ == "__main__":
    main()
