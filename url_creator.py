import datetime
import json

# Open the JSON file
with open('out/thread_ends.json', 'r', encoding="utf-8") as file:
    data = json.load(file)

# Sort the objects by chronological order based on the "timestamp" field
sorted_objects = sorted(data['thread_ends'], key=lambda obj: obj['timestamp'])

with open('out/output.txt', 'w') as output_file:
    for obj in sorted_objects:
        if obj['status'] == 'end':
            obj_date = datetime.datetime.strptime(obj['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
            output_file.write(f"{obj['category']} - {obj['channel']} - {obj_date.strftime('%B %d, %Y')}\n{obj['link']}\n\n")