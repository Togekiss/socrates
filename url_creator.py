import datetime
import json
from res import constants as c

def url_creator():
    # Open the JSON file
    with open('out/scene_ends.json', 'r', encoding="utf-8") as file:
        data = json.load(file)

    # Sort the objects by chronological order based on the "timestamp" field
    sorted_objects = sorted(data['scenes'], key=lambda obj: obj['timestamp'])

    with open('out/output.txt', 'w',encoding="utf-8") as output_file:
        for obj in sorted_objects:
            if obj['status'] == c.STATUS or c.STATUS == "all":
                try:
                    obj_date = datetime.datetime.strptime(obj['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z')
                except ValueError as ve:
                    obj_date = datetime.datetime.strptime(obj['timestamp'], '%Y-%m-%dT%H:%M:%S%z')
                
                output_file.write(f"{obj['category']} - {obj['channel']} - {obj_date.strftime('%B %d, %Y')}\n{obj['link']}\n\n")

    print("scene ends output file created: out/output.txt")

if __name__ == "__main__":
    url_creator()