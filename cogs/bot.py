from discord.ext import commands
from pytz import UTC
from customembeds import *
import plotting
import numpy as np
import io
import pycountry

from helpers.checks import check_mode


class Bot(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.reply('pong <:PokeSlow:788414310762283050>')

    @commands.command(aliases=['i', 'I'])
    async def info(self, ctx, username: str, mode: str = None):
        mode = await check_mode(mode)

        try:
            reply_embed = await info_embed(username, mode)
            await ctx.reply(embed=reply_embed)
        except Exception as e:
            await ctx.reply(e)

    @commands.command(aliases=['r', 'R'])
    async def recent(self, ctx, username: str, *args):
        mode = await check_mode(args[0])

        if "-d" in args or "-D" in args:
            try:
                recent_embed = await multiple_scores_embed(username, mode, 'recent', 5)
                await ctx.reply(embed=recent_embed)
            except Exception as e:
                await ctx.reply(e)
        else:
            try:
                recent_embed = await single_score_embed(username, mode, 'recent')
                await ctx.reply(embed=recent_embed)
            except Exception as e:
                await ctx.reply(e)

    @commands.command()
    async def plot(self, ctx, username, mode: str = "osu"):
        mode = await check_mode(mode)

        user = await api.get_user(username, mode)
        if 'error' in user.keys():
            await ctx.reply("Invalid username.")
            return

        scores = await api.get_scores(username, mode, "best", 100)

        # Retrieve image from plotting module
        try:
            image_bytes = await plotting.histogram_scores(scores)
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
    async def top(self, ctx, username: str, *args: str):
        mode = await check_mode(args[0])

        if "-d" in args or "-D" in args:
            try:
                top_embed = await multiple_scores_embed(username, mode, 'best', 5)
                await ctx.reply(embed=top_embed)
            except Exception as e:
                await ctx.reply(e)
        else:
            try:
                top_embed = await single_score_embed(username, mode, 'best')
                await ctx.reply(embed=top_embed)
            except Exception as e:
                await ctx.reply(e)

    @commands.command()
    async def time(self, ctx):
        time_string = datetime.now(UTC).strftime('%d %B %Y %H:%M UTC')
        embed = discord.Embed(
            title="Current Time (UTC)",
            description=time_string,
            colour=discord.Colour.blue()
        )
        await ctx.reply(embed=embed)


async def setup(client):
    await client.add_cog(Bot(client))
