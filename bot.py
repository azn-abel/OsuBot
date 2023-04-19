import discord
from discord.ext import commands
from pytz import UTC

from scraping import *
from emoji import *
from api import refresh_token
from datetime import date, datetime
from customembeds import *

import os

if os.getenv('PYCHARM_HOSTED'):
    from environment import *

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True,
                          message_content=True)
client = commands.Bot(command_prefix=['>'], intents=intents)


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



    # try:
    #     user_data, play_data = get_data(username, mode)
    # except:
    #     await ctx.reply('Invalid username.')
    #     return
    #
    # global_rank = user_data['statistics']['global_rank']
    #
    # try:
    #     most_recent_month = user_data['monthly_playcounts'][-1]
    #     most_played = play_data['beatmapPlaycounts'][0]
    #     top_play = play_data['scoresBest'][0]
    # except:
    #     most_recent_month = {
    #         'start_date': '2021-05-01',
    #         'count': 0
    #     }
    #     most_played = None
    #     top_play = None
    # plays_this_month = most_recent_month['count']
    # month_start = f"{str(date.today())[:-2]}01"
    #
    # # START EMBED
    # reply_embed = discord.Embed(
    #     title=f":flag_{user_data['country_code'].lower()}: {user_data['username']}'s osu!{arg if arg else ''} Profile {mode_emoji[mode]}",
    #     colour=discord.Colour.blue()
    # )
    #
    # reply_embed.add_field(
    #     name="Global Rank",
    #     value=f"#{global_rank:,}" if global_rank else "Unranked")
    # reply_embed.add_field(
    #     name="pp",
    #     value=f"{user_data['statistics']['pp']:,}"
    # )
    # reply_embed.add_field(
    #     name='Total Play',
    #     value=convert_time(user_data['statistics']['play_time'])[:-3] if user_data['statistics'][
    #         'play_time'] else "None"
    # )
    # reply_embed.add_field(
    #     name='Monthly Plays',
    #     value=f"{plays_this_month}" if most_recent_month['start_date'] == month_start else "0"
    # )
    # reply_embed.add_field(
    #     name='Medals',
    #     value=str(len(user_data['user_achievements']))
    # )
    #
    # try:
    #     beatmapset = top_play['beatmapset']
    #     mods_string = f' +{", ".join(top_play["mods"])}'
    #
    #     reply_embed.add_field(
    #         name=f'Top Play [ {rank_emoji[top_play["rank"]]}{" FC" if top_play["perfect"] else ""}{mods_string if top_play["mods"] else ""} for {top_play["pp"]} pp ]',
    #         value=f"- **Name:** {beatmapset['title']} [{top_play['beatmap']['version']}]\n"
    #               f"- **Artist:** {beatmapset['artist']}\n"
    #               f"- **Mapper:** {beatmapset['creator']}\n",
    #
    #         inline=False
    #     )
    # except:
    #     reply_embed.add_field(
    #         name='Top Play',
    #         value="No plays",
    #
    #         inline=False
    #     )
    # try:
    #     beatmapset = most_played['beatmapset']
    #     reply_embed.add_field(
    #         name='Most Played Beatmap',
    #         value=f"- **Name:** {beatmapset['title']} [{most_played['beatmap']['version']}]\n"
    #               f"- **Artist:** {beatmapset['artist']}\n"
    #               f"- **Mapper:** {beatmapset['creator']}\n"
    #               f"- **Plays:** {most_played['count']}" if most_played else "bruh",
    #
    #         inline=False
    #     )
    # except:
    #     reply_embed.add_field(
    #         name='Most Played Beatmap',
    #         value="No plays",
    #
    #         inline=False
    #     )
    #
    # # END EMBED




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


@client.command()
async def all(ctx, username, mode="osu"):
    user_data, extra_data = get_data(username, mode)

    output_string = ""
    for x in extra_data['scoresBest']:
        output_string += f"{x['rank']}\n"
    await ctx.reply(output_string)


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
