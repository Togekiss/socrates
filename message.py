# bot.py
import os
import random
from res import constants as c
import discord

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

