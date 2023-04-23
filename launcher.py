import asyncio
import math

from bot import *


prefixes = ['osu!', 'Osu!', 'OSu!', 'OSU!', 'oSU!', 'osU!', 'oSu!', 'OsU!']
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True,
                          message_content=True)

initial_num_guilds = len(get_guilds())
total_shards = math.ceil(initial_num_guilds / 1000)

bot = OsuBot(command_prefix=prefixes, intents=intents, shard_count=total_shards)


async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


async def main():
    async with bot:
        await load_extensions()
        await bot.start(DISCORD_BOT_TOKEN)


asyncio.run(main())
# bot.run(DISCORD_BOT_TOKEN)
