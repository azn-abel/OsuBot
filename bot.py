import discord
from discord.ext import commands

from scraping import *
from datetime import date

import os

if os.getenv('PYCHARM_HOSTED'):
    from environment import *

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix=['>'], intents=intents)


@client.command()
async def ping(ctx):
    await ctx.reply('pong!')


@client.command(aliases=['i'])
async def info(ctx, username: str, *args: str):

    if args and args[0] in ['taiko', 'fruits', 'mania', 'catch']:
        mode = 'fruits' if args[0] == 'catch' else args[0]
        arg = 'catch' if args[0] == 'fruits' else args[0]
    else:
        mode = 'osu'
        arg = False

    try:
        user_data, play_data = get_data(username, mode)
    except:
        await ctx.reply('Invalid username.')
        return

    global_rank = user_data['statistics']['global_rank']

    try:
        most_recent_month = user_data['monthly_playcounts'][-1]
        most_played = play_data['beatmapPlaycounts'][0]
        top_play = play_data['scoresBest'][0]
    except:
        most_recent_month = {
            'start_date': '2021-05-01',
            'count': 0
        }
        most_played = None
        top_play = None
    plays_this_month = most_recent_month['count']
    month_start = f"{str(date.today())[:-2]}01"

    # START EMBED
    reply_embed = discord.Embed(
        title=f":flag_{user_data['country_code'].lower()}: {user_data['username']}'s osu!{arg if arg else ''} Profile"
    )

    reply_embed.add_field(
        name="Global Rank",
        value=f"#{global_rank:,}" if global_rank else "Unranked")
    reply_embed.add_field(
        name="pp",
        value=f"{user_data['statistics']['pp']:,}"
    )
    reply_embed.add_field(
        name='Total Play',
        value=convert_time(user_data['statistics']['play_time'])[:-3]
    )
    reply_embed.add_field(
        name='Monthly Plays',
        value=f"{plays_this_month}" if most_recent_month['start_date'] == month_start else "0"
    )
    reply_embed.add_field(
        name='Medals',
        value=str(len(user_data['user_achievements']))
    )

    try:
        beatmapset = top_play['beatmapset']
        reply_embed.add_field(
            name='Top Play',
            value=f"- **Name:** {beatmapset['title']} [{top_play['beatmap']['version']}]\n"
                  f"- **Artist:** {beatmapset['artist']}\n"
                  f"- **Mapper:** {beatmapset['creator']}\n",

            inline=False
        )
    except:
        reply_embed.add_field(
            name='Top Play',
            value="No plays",

            inline=False
        )
    try:
        beatmapset = most_played['beatmapset']
        reply_embed.add_field(
            name='Most Played Beatmap',
            value=f"- **Name:** {beatmapset['title']} [{most_played['beatmap']['version']}]\n"
                  f"- **Artist:** {beatmapset['artist']}\n"
                  f"- **Mapper:** {beatmapset['creator']}\n"
                  f"- **Plays:** {most_played['count']}" if most_played else "bruh",

            inline=False
        )
    except:
        reply_embed.add_field(
            name='Top Play',
            value="No plays",

            inline=False
        )

    if user_data['avatar_url'] == '/images/layout/avatar-guest.png':
        reply_embed.set_thumbnail(url="https://a.ppy.sh/")
    else:
        reply_embed.set_thumbnail(url=user_data['avatar_url'])
    # END EMBED

    await ctx.reply(embed=reply_embed)


@client.event
async def on_ready():
    print('Osu Rankings is online!')
    await client.change_presence(activity=discord.Game(name="osu!"))
