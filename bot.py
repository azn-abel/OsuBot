import discord
from discord.ext import commands
from scraping import *
import os

if os.getenv('PYCHARM_HOSTED'):
    from environment import *

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix=['>'], intents=intents)


@client.command()
async def ping(ctx):
    await ctx.reply('pong!')


@client.command()
async def info(ctx, username: str):
    try:
        user_data = get_user_data(username)
    except:
        ctx.reply('Invalid username.')
        return

    reply_embed = discord.Embed(
        title=f"{user_data['username']}'s osu! Profile"
    )

    if user_data['avatar_url'] == '/images/layout/avatar-guest.png':
        reply_embed.set_thumbnail(url="https://a.ppy.sh/")
    else:
        reply_embed.set_thumbnail(url=user_data['avatar_url'])

    await ctx.reply(embed=reply_embed)
