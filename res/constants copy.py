# Search parameters
SEARCH_FOLDER = "Elysium"       # Same as SERVER_NAME, or a subfolder if you want to search in a specific category
CHARACTER = "Haruki Miyoshi"

# Result filters - are applied when creating the list of links and downloading full scenes
STATUS = "all"          # closed, open, timeout, all
TYPE = "all"            # channel, thread, DM, all
MODE = "start"          # start, end

# Feedback settings
INFO = True             # True if you want to know what the script is doing
DEBUG = True            # True if you want to see an insane amount of information
CONSOLE = True          # True if you want to see the output of DCE console commands
LOG = True              # True if you want to save absolutely all the info into a log file

# Result file parameters
OUTPUT_SCENES = "out/scenes.json"
OUTPUT_LINKS = "out/scene-links.txt"
LOG_FILE = "out/log.txt"

# File parameters
CHARACTER_IDS = "res/character_ids.json"
CHANNEL_LIST = "res/channel_list.json"

# Discord parameters
SERVER_NAME = "Elysium"     # Doesn't need to be accurate, it's for file naming
SERVER_ID = "857848490683269161"
BOT_TOKEN = ""
DM_CATEGORIES = "Text and Calls"
CATEGORIES_TO_IGNORE = [
    "Staff Only",
    "Welcome!",
    "OOC",
    "RP Information",
    "RP Section",
    "EVENT",
    "Group Chats",
    "Social Media",
    "NSFW Room",
    "nsfw-events",
    "Confessional",
    "->WAITING ROOM<-"
]
