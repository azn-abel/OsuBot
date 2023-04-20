import discord
from discord.ext import commands
from pytz import UTC

import api
from api import refresh_token
import plotting
from customembeds import *

import os

if os.getenv('PYCHARM_HOSTED'):
    from environment import *

import requests
import math

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True,
                          message_content=True)

headers = {
    "Authorization": f"Bot {DISCORD_BOT_TOKEN}"
}

response = requests.get("https://discord.com/api/users/@me/guilds", headers=headers)

if response.status_code == 200:
    guilds = response.json()
    num_guilds = len(guilds)
    print(f"The bot is in {num_guilds} guilds.")
else:
    raise Exception(f"Failed to fetch guilds. Status code: {response.status_code}")

total_shards = math.ceil(num_guilds / 1000)
client = commands.AutoShardedBot(command_prefix=['osu!'], intents=intents, shard_count=total_shards)


@client.command()
async def ping(ctx):
    await ctx.reply('pong <:PokeSlow:788414310762283050>')


@client.command(aliases=['i', 'I'])
async def info(ctx, username: str, mode: str = None):
    if mode and mode.lower() in ['taiko', 'fruits', 'mania', 'catch']:
        mode = 'fruits' if mode == 'catch' else mode
        arg = 'catch' if mode == 'fruits' else mode
    else:
        mode = 'osu'
        arg = False

    try:
        reply_embed = await info_embed(username, mode, arg)
        await ctx.reply(embed=reply_embed)
    except Exception as e:
        await ctx.reply(e)


@client.command(aliases=['r', 'R'])
async def recent(ctx, username: str, *args: str):
    if args and args[0] in ['taiko', 'fruits', 'mania', 'catch']:
        mode = 'fruits' if args[0] == 'catch' else args[0]
        arg = 'catch' if args[0] == 'fruits' else args[0]
    else:
        mode = 'osu'
        arg = False

    if "-d" in args or "-D" in args:
        try:
            recent_embed = await multiple_scores_embed(username, mode, arg, 'recent', 5)
            await ctx.reply(embed=recent_embed)
        except Exception as e:
            await ctx.reply(e)
    else:
        try:
            recent_embed = await single_score_embed(username, mode, arg, 'recent')
            await ctx.reply(embed=recent_embed)
        except Exception as e:
            await ctx.reply(e)


@client.command()
async def plot(ctx, username, mode: str = "osu"):
    if mode not in ['taiko', 'fruits', 'mania', 'osu']:
        if mode == 'catch':
            mode = 'fruits'
        else:
            mode = 'osu'

    user = api.get_user(username, mode)
    if 'error' in user.keys():
        await ctx.reply("Invalid username.")
        return

    scores = api.get_scores(username, mode, "best", 100)
    plotting.histogram_scores(scores)
    temp_file = discord.File(f"plots/temp.png", filename="plot.png")
    embed = discord.Embed(
        title=f"{user['username']}'s Top {len(scores)} Plays in osu!{mode if mode != 'osu' else ''}",
        colour=0xff79b8
    )
    embed.set_image(url="attachment://plot.png")
    await ctx.reply(file=temp_file, embed=embed)


@client.command(aliases=['t', 'T'])
async def top(ctx, username: str, *args: str):
    if args and args[0] in ['taiko', 'fruits', 'mania', 'catch']:
        mode = 'fruits' if args[0] == 'catch' else args[0]
        arg = 'catch' if args[0] == 'fruits' else args[0]
    else:
        mode = 'osu'
        arg = False

    if "-d" in args or "-D" in args:
        try:
            top_embed = await multiple_scores_embed(username, mode, arg, 'best', 5)
            await ctx.reply(embed=top_embed)
        except Exception as e:
            await ctx.reply(e)
    else:
        try:
            top_embed = await single_score_embed(username, mode, arg, 'best')
            await ctx.reply(embed=top_embed)
        except Exception as e:
            await ctx.reply(e)


# @client.command()
# async def all(ctx, username, mode="osu"):
#     user_data, extra_data = get_data(username, mode)
#
#     output_string = ""
#     for x in extra_data['scoresBest']:
#         output_string += f"{x['rank']}\n"
#     await ctx.reply(output_string)


@client.command()
async def time(ctx):
    time_string = datetime.now(UTC).strftime('%d %B %Y %H:%M UTC')
    embed = discord.Embed(
        title="Current Time (UTC)",
        description=time_string,
        colour=discord.Colour.blue()
    )
    await ctx.reply(embed=embed)


@client.event
async def on_ready():
    print('osu! Rankings is online!')
    refresh_token.start()
    await client.change_presence(activity=discord.Game(name="osu!"))
