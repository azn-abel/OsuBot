from discord.ext import commands
from pytz import UTC
import pycountry
import numpy as np
import io
import logging

from api import refresh_token
import plotting
from customembeds import *

import os

if os.getenv('PYCHARM_HOSTED'):
    from environment import *

import requests
import math

logger = logging.getLogger('discord')
shard_logger = logging.getLogger('discord.shard')

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True,
                          message_content=True)


def get_guilds():
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}"
    }

    response = requests.get("https://discord.com/api/users/@me/guilds", headers=headers)

    if response.status_code == 200:
        guilds = response.json()
        return guilds
    else:
        logger.error(f"Failed to fetch guilds. Status code: {response.status_code}")
        return []


initial_num_guilds = len(get_guilds())

total_shards = math.ceil(initial_num_guilds / 1000)
prefixes = ['osu!', 'Osu!', 'OSu!', 'OSU!', 'oSU!', 'osU!', 'oSu!', 'OsU!']
client = commands.AutoShardedBot(command_prefix=prefixes, intents=intents, shard_count=total_shards)


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

    user = await api.get_user(username, mode)
    if 'error' in user.keys():
        await ctx.reply("Invalid username.")
        return

    scores = await api.get_scores(username, mode, "best", 100)

    # Retrieve image from plotting module
    try:
        image_bytes = plotting.histogram_scores(scores)
    except Exception as e:
        await ctx.reply(e)
        return
    buffer = io.BytesIO(image_bytes)
    temp_file = discord.File(buffer, filename='plot.png')
    buffer.close()

    embed = discord.Embed(
        title=(f":flag_{user['country_code'].lower()}: "
               f"#{user['statistics']['global_rank']:,} "
               f"{user['username']}'s Top {len(scores)} osu!{mode if mode != 'osu' else ''} Plays"),
        colour=0xff79b8
    )

    embed.set_thumbnail(url=user['avatar_url'])

    # Add fields for statistics
    pp_values = np.array([score['pp'] for score in scores], dtype=np.float64)
    stats = {
        'Ovr PP': user['statistics']['pp'],
        'Max PP': np.max(pp_values),
        'Min PP': np.min(pp_values),
        'Med PP': np.median(pp_values),
        'Mean PP': np.mean(pp_values),
        'Std Dev': np.std(pp_values)
    }
    for key in stats.keys():
        embed.add_field(
            name=key,
            value=round(stats[key], 3),
            inline=True
        )

    embed.set_image(url="attachment://plot.png")
    await ctx.reply(file=temp_file, embed=embed)


@client.command()
async def bar(ctx, num: int = 100, mode: str = "osu"):

    if mode not in ['taiko', 'fruits', 'mania', 'osu']:
        if mode == 'catch':
            mode = 'fruits'
        else:
            mode = 'osu'

    if num > 1000:
        num = 1000

    rankings = await api.get_rankings(mode, num // 50 + 1 if num % 20 != 0 else num // 50)
    rankings = rankings[:num]
    image_bytes, top_countries_dict = plotting.bar_ranks(rankings)
    buffer = io.BytesIO(image_bytes)
    plot_image_file = discord.File(buffer, filename='bar.png')
    buffer.close()

    embed = discord.Embed(
        title=f"Top {num} osu!{mode if mode != 'osu' else ''} Players by Country",
        colour=0xff79b8
    )
    mode_image_file = discord.File(f"images/mode-{mode}.png", filename='mode.png')
    embed.set_thumbnail(url="attachment://mode.png")

    countries_represented_string = ""
    for country_code in top_countries_dict.keys():
        country_name = pycountry.countries.get(alpha_2=country_code).name.title()
        countries_represented_string += f'- **{country_name} ({country_code}):** {top_countries_dict[country_code]}\n'
    embed.add_field(
        name="**Top Countries represented:**",
        value=countries_represented_string,
        inline=False
    )
    # for country_code in top_countries_dict.keys():
    #     country_name = pycountry.countries.get(alpha_2=country_code).name.title()
    #     embed.add_field(
    #         name="",
    #         value=f'**{country_name}({country_code}):** {top_countries_dict[country_code]}',
    #         inline=True
    #     )

    embed.set_image(url="attachment://bar.png")
    await ctx.reply(files=[plot_image_file, mode_image_file], embed=embed)


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
    logger.info(f'osu! Rankings is online in {initial_num_guilds} guilds.')
    try:
        refresh_token.start(logger=logger)
        logger.info("Started refresh_token loop.")
    except RuntimeError:
        logger.info("refresh_token loop already in progress - no need to restart it.")
    await client.change_presence(activity=discord.Game(name="osu!"))


@client.event
async def on_guild_join(guild):
    num_guilds = len(get_guilds())
    logger.info(f'Joined guild "{guild.name}" ({guild.id})')
    logger.info(f'osu! Ranking is online in {num_guilds} guilds.')
