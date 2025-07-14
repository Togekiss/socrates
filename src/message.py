# bot.py
import os
import random
from set_path import set_path
set_path()
from res import constants as c
import discord

################# File summary #################

"""

This module is used to test the connectivity of the bot with Discord.

Main function: on_message()

    This is the main function of the bot. It is called when a message is sent in a channel.

    If the message is sent by the bot itself, ignores it.

    If the message contains the word "happy birthday", the function sends a message to the channel.

"""

################# Functions #################

TOKEN = c.BOT_TOKEN
GUILD = 857848490683269161

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, id=GUILD)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    # trolling in the crack channel
    # await client.get_channel(867144416023543829).send("yet i see everything. i'm in elysium's walls")


@client.event
async def on_message(message):

    
    print (f"i have a message! {message.content} in {message.guild.id}")

    if message.author == client.user:
        return
    

    if 'happy birthday' in message.content.lower():
        await message.channel.send('Happy Birthday! 🎈🎉')

client.run(TOKEN)

