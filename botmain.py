#!/usr/bin/env python3
import discord, datetime
import asyncio, random, string, json, urllib, os, dotenv
from discord_slash import SlashCommand
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()
slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

if not discord.opus.is_loaded():
    discord.opus.load_opus('/home/container/lib/libopus.so') # This is a linux specific solution; change this to the path of the libopus library (can be download from https://opus-codec.org/downloads/ or built from source) if working in windows
if discord.opus.is_loaded():
    print("Opus loaded successfully!")
else:
    print("Opus did not properly load. Should still be able to play in non-opus VCs.") # This should be fine. There is sometimes an issue with joining a vc

@client.event
async def on_ready():
    print(f'{client.user} successfully connected!')

guild_ids = [int(x) for x in os.environ.get("GUILD_IDS").split(" ")] # Parses and adds all the server ids from .env to a list of servers for each slash command to work

@slash.slash(name="ping", guild_ids=guild_ids)
async def _ping(ctx_ping): 
    '''
    Simple ping command to see if the latency and if the bot is dead
    '''
    print("Ping command recieved")
    await ctx_ping.send(f"Pong! ({client.latency*1000}ms)")


@slash.slash(name="indie", guild_ids=guild_ids)
async def _indie(ctx_indie):
    '''
    Have Dr_KittyKat II join VC and start playing Indie 102.3
    '''
    if ctx_indie.author.voice and ctx_indie.author.voice.channel:
        channel = ctx_indie.author.voice.channel
        vc = await channel.connect()
        audio_source = discord.FFmpegPCMAudio(source='http://stream1.cprnetwork.org/cpr3_lo')
        vc.play(audio_source)
        msgembed = discord.Embed(title="You are listening to KVOQ, indie 102.3", thumbnail="/home/kitty/Desktop/kvoq-bot/indie1023-2-Clr-Circle-Logo-Print-201907.png", description=get_track_info(), color=0xF887D7)
        await ctx_indie.send(embed=msgembed)
        while not len(channel.members) <= 1:
            await asyncio.sleep(30)
        #vc.stop()
        await vc.disconnect()
    else:
        msgembed = discord.Embed(description="You are not connected to any voice channel...", color=0xF887D7)
        await ctx_indie.send(embed=msgembed)


@slash.slash(name="now playing", guild_ids=guild_ids)
async def _nowplaying(ctx_nowplaying):
    '''
    Get the current playing song, artist, and DJ
    '''
    msgembed = discord.Embed(title="Now Playing on KVOQ, indie 102.3", thumbnail="/home/kitty/Desktop/kvoq-bot/indie1023-2-Clr-Circle-Logo-Print-201907.png", description=get_track_info(), color=0xF887D7)
    await ctx_nowplaying.send(embed=msgembed)


@slash.slash(name="disconnect", guild_ids=guild_ids)
async def _disconnect(ctx_disconnect):
    '''
    Have Dr_KittyKat II disconnect from the VC
    '''
    for x in client.voice_clients:
        if(x.guild == ctx_disconnect.guild):
            x.stop()
            await x.disconnect()
            msgembed = discord.Embed(description="Disconnected!", color=0xF887D7)
            return await ctx_disconnect.send(embed=msgembed)
    
    msgembed = discord.Embed(description="I'm not connected to any voice channel!", color=0xF887D7)
    return await ctx_disconnect.send(embed=msgembed)


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