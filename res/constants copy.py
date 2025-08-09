# Search parameters
SEARCH_FOLDER = "Elysium"       # Same as SERVER_NAME, or a subfolder if you want to search in a specific category
CHARACTER = "Haruki"            # Character name. If looking for a canon, specify the writer i.e. "Laito Sakamaki (Meli)"
# TIP: Most of the times, using the first name or nickname is enough i.e. "Lysander" or "Lys"

INCLUDE_ALL_WRITERS = False     # True if you want to include all the versions of the character. Mostly useful for canons. Not recommended though
INCLUDE_ALTER_EGOS = True       # True if you want to include all fake names and identities of the character in the search
INCLUDE_FAMILIARS = True        # True if you want to include the familiars of the character in the search
INCLUDE_NPCS = True             # True if you want to include the NPCs of the character in the search
# TIP: If you want to look for only threads with a familiar or a NPC, just write its name in "CHARACTER" i.e. "Hissy"

# Result filters - are applied when creating the list of links and downloading full scenes
STATUS = "all"          # closed, open, timeout, all
TYPE = "all"            # channel, thread, DM, all
MODE = "start"          # start, end

# Feedback settings
INFO = True             # True if you want to know what the script is doing
DEBUG = True            # True if you want to see an insane amount of information
CONSOLE = False         # True if you want to see the output of DCE console commands
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
