import asyncpg.exceptions
import discord.mentions
import time

from discord.ext import commands
from pytz import UTC
from customembeds import *
import plotting
import numpy as np
import io
import pycountry
from typing import Union

from helpers.checks import check_mode, check_username_and_mode


class Bot(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        s = time.time()
        await ctx.reply('pong <:PokeSlow:788414310762283050>')
        e = time.time()
        print(f"Response time: {e - s}")

    @commands.command(aliases=['i', 'I'])
    async def info(self, ctx, username: Union[discord.Member, str], mode: str = None):
        try:
            username, mode = await check_username_and_mode(username, mode, self.client.db)
            reply_embed = await info_embed(username, mode)
            await ctx.reply(embed=reply_embed)
        except Exception as e:
            await ctx.reply(e)

    @commands.command(aliases=['r', 'R'])
    async def recent(self, ctx, username: Union[discord.Member, str], *args):

        try:
            username, mode = await check_username_and_mode(username, args[0] if args else None, self.client.db)
            if "-d" in args or "-D" in args:
                recent_embed = await multiple_scores_embed(username, mode, 'recent', 5)
            else:
                recent_embed = await single_score_embed(username, mode, 'recent')
            await ctx.reply(embed=recent_embed)
        except Exception as e:
            await ctx.reply(e)

    @commands.command()
    async def plot(self, ctx, username: Union[discord.Member, str], mode: str = "osu"):
        try:
            username, mode = await check_username_and_mode(username, mode, self.client.db)
            user = await api.get_user(username, mode)
            if 'error' in user.keys():
                await ctx.reply("Invalid username.")
                return

            scores = await api.get_scores(username, mode, "best", 100)

            # Retrieve image from plotting module
            image_bytes = await plotting.histogram_scores(scores)

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
        except Exception as e:
            await ctx.reply(e)

    @commands.command()
    async def bar(self, ctx, num: int = 100, mode: str = "osu"):
        mode = await check_mode(mode)

        if num > 1000:
            num = 1000

        rankings = await api.get_rankings(mode, num // 50 + 1 if num % 20 != 0 else num // 50)
        rankings = rankings[:num]

        image_bytes, top_countries_dict = await plotting.bar_ranks(rankings)
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

        embed.set_image(url="attachment://bar.png")
        await ctx.reply(files=[plot_image_file, mode_image_file], embed=embed)

    @commands.command(aliases=['t', 'T'])
    async def top(self, ctx, username: Union[discord.Member, str], *args: str):
        try:
            username, mode = await check_username_and_mode(username, args[0] if args else None, self.client.db)
            if "-d" in args or "-D" in args:
                top_embed = await multiple_scores_embed(username, mode, 'best', 5)
            else:
                top_embed = await single_score_embed(username, mode, 'best')
            await ctx.reply(embed=top_embed)
        except Exception as e:
            await ctx.reply(e)

    @commands.command()
    async def time(self, ctx):
        time_string = "<t:" + str(round(time.time())) + ">"
        embed = discord.Embed(
            title="Current Time",
            description=time_string,
            colour=discord.Colour.blue()
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def link(self, ctx, osu_name, mode=None):
        # TODO - Add the user's Discord ID and osu! name to a SQL table somewhere
        try:
            user = await api.get_user(osu_name, 'osu')
        except Exception as e:
            await ctx.reply(e)
            return

        if user['discord'] == str(ctx.author):
            username = user['username']
            discord_id = str(ctx.author.id)
            mode = await check_mode(mode)
            try:
                await self.client.db.execute("INSERT INTO discord_users VALUES($1, $2, $3)", discord_id, username, mode)
                await ctx.reply("Successfully linked accounts!")
            except asyncpg.exceptions.UniqueViolationError:
                await self.client.db.execute("UPDATE discord_users "
                                             "SET osu_name = $1, mode = $2 "
                                             "WHERE discord_id = $3", username, mode, discord_id)
                await ctx.reply("Successfully updated information!")
        else:
            await ctx.reply("Liar, liar, pants on fire.")

    @commands.command(name='shutdown')
    @commands.is_owner()
    async def shutdown_bot(self, ctx):
        await self.client.db.close()
        self.client.logger.info("Connection pool closed.")
        self.client.logger.info("Shutting down...")
        await self.client.close()


async def setup(client):
    await client.add_cog(Bot(client))
