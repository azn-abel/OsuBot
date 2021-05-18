import discord
from discord.ext import commands

from scraping import *
from emoji import *
from datetime import date

import os

if os.getenv('PYCHARM_HOSTED'):
    from environment import *

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix=['>'], intents=intents)


@client.command()
async def ping(ctx):
    for emoji in client.emojis:
        print(emoji)
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
        title=f":flag_{user_data['country_code'].lower()}: {user_data['username']}'s osu!{arg if arg else ''} Profile {mode_emoji[mode]}",
        colour=discord.Colour.blue()
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
        value=convert_time(user_data['statistics']['play_time'])[:-3] if user_data['statistics']['play_time'] else "None"
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
        mods_string = f' +{", ".join(top_play["mods"])}'

        reply_embed.add_field(
            name=f'Top Play [ {rank_emoji[top_play["rank"]]}{" FC" if top_play["perfect"] else ""}{mods_string if top_play["mods"] else ""} for {top_play["pp"]} pp ]',
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
            name='Most Played Beatmap',
            value="No plays",

            inline=False
        )

    if user_data['avatar_url'] == '/images/layout/avatar-guest.png':
        reply_embed.set_thumbnail(url="https://a.ppy.sh/")
    else:
        reply_embed.set_thumbnail(url=user_data['avatar_url'])
    # END EMBED

    await ctx.reply(embed=reply_embed)


@client.command(aliases=['r', 'R'])
async def recent(ctx, username: str, *args: str):
    if args and args[0] in ['taiko', 'fruits', 'mania', 'catch']:
        mode = 'fruits' if args[0] == 'catch' else args[0]
        arg = 'catch' if args[0] == 'fruits' else args[0]
    else:
        mode = 'osu'
        arg = False

    try:
        user_data, extra_data = get_data(username, mode)
    except:
        await ctx.reply('Invalid username.')
        return

    try:
        recent_play_data = extra_data['scoresRecent'][0]
        beatmapset = recent_play_data['beatmapset']
    except:
        await ctx.reply("No recent plays.")
        return
    mods_string = ''
    for mod in recent_play_data['mods']:
        mods_string += f"{mod} "
    recent_embed = discord.Embed(
        description=f'Modifiers: {mods_string}' if recent_play_data['mods'] else '',
        colour=discord.Colour.blue()
    )
    recent_embed.set_author(
        name=f"{beatmapset['title']} [{recent_play_data['beatmap']['version']}] {recent_play_data['beatmap']['difficulty_rating']}★",
        icon_url="https://a.ppy.sh/" if user_data['avatar_url'] == '/images/layout/avatar-guest.png' else user_data[
            'avatar_url'],
        url=f"https://osu.ppy.sh/scores/osu/{recent_play_data['best_id']}" if recent_play_data['best_id'] else
        recent_play_data['beatmap']['url']
    )
    recent_embed.set_thumbnail(
        url=recent_play_data['beatmapset']['covers']['list']
    )
    stats = recent_play_data['statistics']
    recent_embed.add_field(
        name=f'Rank: {rank_emoji[recent_play_data["rank"]]} FC' if recent_play_data[
            'perfect'] else f'Rank: {rank_emoji[recent_play_data["rank"]]}',
        value=f"- **Accuracy:** {round(recent_play_data['accuracy'] * 100, 2)}% "
              f"[{stats['count_300'] + stats['count_geki']}/{stats['count_100'] + stats['count_katu']}/{stats['count_50']}/{stats['count_miss']}]\n"
              f"- **Score:** {recent_play_data['score']}\n"
              f"- **Combo:** {recent_play_data['max_combo']}\n"
              f"- **pp:** {recent_play_data['pp'] if recent_play_data['pp'] else 'N/A'}",

        inline=False
    )
    recent_embed.set_footer(
        text=f"osu!{mode if arg else ''}",
        icon_url=f"https://cdn.discordapp.com/emojis/{mode_emoji[mode].split(':')[-1][:-1]}.png?v=1"
    )

    await ctx.reply(embed=recent_embed)


@client.event
async def on_ready():
    print('osu! Rankings is online!')
    await client.change_presence(activity=discord.Game(name="osu!"))
