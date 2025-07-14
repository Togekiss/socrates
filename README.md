# Socrates, the record keeper of Elysium

## What is Socrates?

A Discord bot specifically made for Elysium, a RP server, with plans to adapt it to work on any roleplaying or collaborative writing server that uses similar tagging systems.

The main goal of this bot is to find and list all the scenes a character has participated in. 

Additionally, it serves as a history backup and chat analyser prepper.

## Current status

Socrates is in development process. Currently, the bot itself only serves as a watcher to export channels using DCE and its token. All logic and scripts have to be run manually and locally. Server structure and search parameters are hardcoded and functionality is split in several files.

The current focus of development is fine-tuning the 'end of scene' tags to, hopefully, detect most manners of closing scenes and avoid tagging them as 'timed out'.

Once this basic functionality is in working condition, the focus will shift to cleaning and organizing the code, and uploading the bot to a server to be operational 24/7 
 and invoked with Discord commands.

## How to use in local (in case you want to help or play with it!)

(Note: These instructions are for its current state of development. They will change when the code is clean and adapted to use on other servers. They're a mess, I know. Ask me for more info if you need!)

- Create a folder named 'DCE' and download the CLI version of https://github.com/Tyrrrz/DiscordChatExporter
- Copy the file in the 'res' folder named 'constants copy.py', rename it 'constants.py' and fill in the fields.
- Run 'channel_downloader.py'
- Manually double check 'character_ids.json'. Tupperbox renames (for example, "John Doe" has been renamed to "John D") and aliases (another tupper for the same character, for example, if John Doe has a tupper of his secret identity "Jon Buck") are registered as new, different characters. Manually write the same ID on both so they are treated as one single character. Save the file and run 'idAssigner.py'.
- Find the character name in 'constants.py' and type the desired character
- Find the status in 'constants.py' and type the desired status
- Run 'scene_finder.py'
- You should have the scenes list in 'out/output.txt'
  - Additionally, if you want to search for another status, just change the status in 'constants.py' and run 'url_creator.py' again

## How does it work?

Given the use of Tupperbox to send message as roleplaying characters, native Discord search is unable to look for messages from a particular one.

Every X time, Socrates will use https://github.com/Tyrrrz/DiscordChatExporter to download the specified writing channels. Then it will traverse through the exported .JSON files to detect all the unique Tupperbox-made characters and manually give each a unique ID, effectively turning them into normal users for applications such as https://github.com/mlomb/chat-analytics

When a user runs the script to find scenes with a specified character name, the bot navigates through all channels looking for the first appearence of said character to save the message link and flag it as 'start of scene'.
Then, it will keep that scene alive until it encounters an 'end' tag or similar from a specified list, an EOF, or the character doesn't appear for a specified number of messages. When it considers a scene is over, it will save the last message as 'end of scene' and its status: closed, active, or timed out.

After having gone through all channels, it will output a list of scenes, with the channel name, the date, and the link to the starting message.

## Things to implement

### Scene detection tuning
- Expand and adjust the selection of 'end of scene' tags - and account for variations or mistakes
- Detect the names of other character(s) in the scene
- Detect the true start of the scene, not the first message of the requested character
  - Trace back until you find a previous end tag or SOF to find the proper start
  - Or until its from a character not in the scene, in case last wasn't closed properly
  - Will most likely need an index attribute in the JSON to iterate back and forth
  - Once the true start of the scene is found, check if scene starts with a date tag for more accurate in-universe timeline keeping
- Work on a different set of rules to log open interactions, like chatrooms or events

### Extra search parameters
- Input two characters and find scenes with them
- Input a specific channel/category to look in
  - Load only the category folder or channel file and operate as usual
  - This will be especially useful to differenciate scenes from DMs
- Input a date range
- Input a scene status (Closed, Active, Timed out)

### Chat exporting
- Schedule a weekly/daily download of channels
  - Add a fast search option (against the last download) vs updated search option (update the library and then search)

