from discord.ext import commands
import logging
import colorlog

from api import refresh_token
from customembeds import *

import os

if os.getenv('PYCHARM_HOSTED'):
    from environment import *

import requests

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')


def get_guilds(logger=None):
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}"
    }

    response = requests.get("https://discord.com/api/users/@me/guilds", headers=headers)

    if response.status_code == 200:
        guilds = response.json()
        return guilds

    if logger:
        logger.error(f"Failed to fetch guilds. Status code: {response.status_code}")

    return []


class OsuBot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        ))

        self.logger = logging.getLogger("OsuBot")
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

        self.custom_shard_names = ["Foo", "Bar", "Baz"]

    async def on_ready(self):
        self.logger.info(f'osu! Rankings is online in {len(get_guilds())} guilds.')
        try:
            refresh_token.start(logger=self.logger)
            self.logger.info("Started refresh_token loop.")
        except RuntimeError:
            self.logger.info("refresh_token loop already in progress - no need to restart it.")
        await self.change_presence(activity=discord.Game(name="osu!"))

    async def on_guild_join(self, guild):
        # TODO - Add the guild as a row in an SQL table somewhere
        num_guilds = len(get_guilds())
        self.logger.info(f'Joined guild "{guild.name}" ({guild.id})')
        self.logger.info(f'osu! Ranking is online in {num_guilds} guilds.')

    async def on_guild_remove(self, guild):
        # TODO - Cleanup the guild from SQL table
        num_guilds = len(get_guilds())
        self.logger.info(f'Removed from guild "{guild.name}" ({guild.id})')
        self.logger.info(f'osu! Ranking is online in {num_guilds} guilds.')

    async def on_command_error(self, ctx, error):
        self.logger.error(
            f"Error in command osu!{ctx.command if ctx.command else ''}{ctx.kwargs if ctx.kwargs else ''}: {error}"
        )
        await ctx.reply(error)

    async def on_error(self, event, *args, **kwargs):
        self.logger.error(
            f"Error in event {event}{args if args else ''}{kwargs if kwargs else ''}"
        )

    async def on_shard_ready(self, shard_id):
        self.logger.info(f'Shard ID {shard_id} "{self.custom_shard_names[shard_id]}" is ready')
