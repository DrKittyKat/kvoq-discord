#!/usr/bin/env python3
import discord
import datetime
import asyncio
import random
import string
import json
import urllib
import os
import enum
# from discord_slash import SlashCommand
from dotenv import load_dotenv

class CommandType(enum.Enum):
    slash = 1
    text = 2
class DiscordCommand:
    def __init__(self, cmdtype: CommandType, context):
        self.cmdtype = cmdtype
        self.context = context
    
    def get_cmd_ctx(self):
        if (self.cmdtype == CommandType.slash):
            return self.context.author
        elif (self.cmdtype == CommandType.text):
            return self.context.author

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
# slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.
msg_prefix = "nya-"
guild_ids = [int(x) for x in os.environ.get("GUILD_IDS").split(" ")] # Parses and adds all the server ids from .env to a list of servers for each slash command to work

print("loading opus")
if not discord.opus.is_loaded():
    discord.opus.load_opus('/home/container/lib/libopus.so') # This is a linux specific solution; change this to the path of the libopus library (can be download from https://opus-codec.org/downloads/ or built from source) if working in windows
if discord.opus.is_loaded():
    print("Opus loaded successfully!")
else:
    print("Opus did not properly load. Should still be able to play in non-opus VCs.") # This should be fine. There is sometimes an issue with joining a vc

@client.event
async def on_ready():
    print(f'{client.user} successfully connected!')
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    text_command = DiscordCommand(CommandType.text, message)
    
    if message.content == msg_prefix + "ping":
        await bot_ping(text_command)

    if message.content == msg_prefix + "indie":
        await bot_indie(text_command)
    
    if message.content == msg_prefix + "nowplaying":
        await bot_nowplaying(text_command)
    
    if message.content == msg_prefix + "disconnect":
        await bot_disconnect(text_command)

'''
@slash.slash(name="ping", guild_ids=guild_ids)
async def _ping(ctx_ping): 
    slash_command = DiscordCommand(CommandType.slash, ctx_ping)
    await bot_ping(slash_command)
    await ctx_ping.send("")

@slash.slash(name="indie", guild_ids=guild_ids)
async def _indie(ctx_indie):
    slash_command = DiscordCommand(CommandType.slash, ctx_indie)
    await bot_indie(slash_command)
    await ctx_indie.send(" ")

@slash.slash(name="nowplaying", guild_ids=guild_ids)
async def _nowplaying(ctx_nowplaying):
    slash_command = DiscordCommand(CommandType.slash, ctx_nowplaying)
    await bot_nowplaying(slash_command)
    await ctx_nowplaying.send(" ")

    
@slash.slash(name="disconnect", guild_ids=guild_ids)
async def _disconnect(ctx_disconnect):
    slash_command = DiscordCommand(CommandType.slash, ctx_disconnect)
    await bot_disconnect(slash_command)
    await ctx_disconnect.send(" ")
'''
async def bot_ping(CommandClass : DiscordCommand):
    '''
    Simple ping command to see if the latency and if the bot is dead
    '''
    print("Ping command recieved")
    await CommandClass.context.channel.send(f"Pong! ({client.latency*1000}ms)")

async def bot_indie(CommandClass : DiscordCommand):
    '''
    Have Dr_KittyKat II join VC and start playing Indie 102.3
    '''
    if CommandClass.context.author.voice and CommandClass.context.author.voice.channel:
        channel = CommandClass.context.author.voice.channel
        vc = await channel.connect()
        audio_source = discord.FFmpegPCMAudio(source='http://stream1.cprnetwork.org/cpr3_lo')
        vc.play(audio_source)
        msgembed = discord.Embed(title="You are listening to KVOQ, indie 102.3", thumbnail="/home/kitty/Desktop/kvoq-bot/indie1023-2-Clr-Circle-Logo-Print-201907.png", description=get_track_info(), color=0xF887D7)
        await CommandClass.context.channel.send(embed=msgembed)
        while not len(channel.members) <= 1:
            await asyncio.sleep(30)
        await vc.disconnect()
    else:
        msgembed = discord.Embed(description="You are not connected to any voice channel...", color=0xF887D7)
        await CommandClass.context.channel.send(embed=msgembed)

async def bot_nowplaying(CommandClass : DiscordCommand):
    '''
    Get the current playing song, artist, and DJ
    '''
    msgembed = discord.Embed(title="Now Playing on KVOQ, indie 102.3", description=get_track_info(), color=0xF887D7)
    urlThumbnail = "https://pbs.twimg.com/profile_images/1145771354244993024/rEN4VY4L_400x400.png"
    msgembed.set_thumbnail(url=urlThumbnail)
    await CommandClass.context.channel.send(embed=msgembed)

async def bot_disconnect(CommandClass : DiscordCommand):
    '''
    Have Dr_KittyKat II disconnect from the VC
    '''
    for x in client.voice_clients:
        if(x.guild == CommandClass.context.guild):
            x.stop()
            await x.disconnect()
            msgembed = discord.Embed(description="Disconnected!", color=0xF887D7)
            return await CommandClass.context.channel.send(embed=msgembed)
    
    msgembed = discord.Embed(description="I'm not connected to any voice channel!", color=0xF887D7)
    return await CommandClass.context.channel.send(embed=msgembed)

def get_track_info():
    '''
    Command to make 2 lines of info for /indie and /nowplaying in the format:
    
    [Title] by [Artist]
    DJ [dj name]
    
    This can be easily expanded by finding your own info from the exposed json file at https://playlist.cprnetwork.org/won_plus3/KVOQ.json
    '''
    with urllib.request.urlopen("https://playlist.cprnetwork.org/won_plus3/KVOQ.json") as track_info_json_url:
        track_info_json = json.loads(track_info_json_url.read().decode())
        track_info = track_info_json[0]["title"] + " by " + track_info_json[0]["artist"] + "\n" + "DJ " + track_info_json[0]["line_2"]
    return track_info

client.run(os.environ["TOKEN"])
# permissions: 2150697984