import datetime
import json
import tricks as t
t.set_path()
from res import constants as c

################ File summary #################

"""

This module creates a text file with the scene starts and ends.

Main function: url_creator()

    This function reads the scene starts and ends from the JSON files created by the scene_finder script.
    It sorts the objects by chronological order based on the "timestamp" field
    and creates a text file with the titles of each scene, its date, and the link to the first (or last) message.

"""

################# Functions #################

def resolve_type(obj):
    if obj['category'] == c.DM_CATEGORIES or obj['category'].startswith("dm-") or obj['category'].startswith("lets-call-"):
        return "DM"
    return obj['type']


################# Main function #################

def url_creator():


    t.log("base", "\n### Compilating a list of scene links... ###\n")

    # Open the JSON file
    data: list = t.load_from_json(c.OUTPUT_SCENES)

    t.log("debug", f"\tLoaded {len(data)} scenes from {c.OUTPUT_SCENES}\n")

    mode = 'end' if c.MODE == "end" else 'start'

    t.log("info", f"\tListing the {mode} of {c.STATUS}{"" if c.TYPE == "all" else " " + c.TYPE} scenes...\n")

    # Sort the objects by chronological order based on ['start'/'end']['timestamp']
    sorted_objects = sorted(data, key=lambda x: x[mode]['timestamp'])

    with open(c.OUTPUT_LINKS, 'w',encoding="utf-8") as output_file:

        for obj in sorted_objects:

            validStatus = True if obj['status'] == c.STATUS or c.STATUS == "all" else False
            validType = True if resolve_type(obj) == c.TYPE or c.TYPE == "all" else False

            if validStatus and validType:
                 
                obj_date = datetime.datetime.strptime(obj[mode]['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z')

                output_file.write(f"{obj['category']} - {obj['channel']} - {obj_date.strftime('%B %d, %Y')} - {obj['status']}\n{obj[mode]['link']}\n\n")

    t.log("info", f"\tList of scene links created in: {c.OUTPUT_LINKS}")

    t.log("base", "\n### List created! ###\n")

if __name__ == "__main__":
    url_creator()