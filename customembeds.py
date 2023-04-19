import asyncio

import discord
from datetime import date, datetime
from emoji import *
import api


async def single_score_embed(username, mode, arg, score_type):
    try:
        user_data = api.get_user(username, mode)
    except:
        raise Exception('Invalid username.')

    try:
        play_data = api.get_scores(username, mode, score_type)[0]
        beatmapset = play_data['beatmapset']
    except:
        raise Exception(f'No {score_type} plays.')

    beatmap_data = api.get_beatmap(play_data['beatmap']['id'])
    mods_string = ''
    for mod in play_data['mods']:
        mods_string += f"{mod} "
    score_embed = discord.Embed(
        description=f'Modifiers: {mods_string}' if play_data['mods'] else '',
        colour=discord.Colour.blue()
    )
    score_embed.set_author(
        name=f"{beatmapset['title']} [{play_data['beatmap']['version']}] {play_data['beatmap']['difficulty_rating']}★",
        icon_url="https://a.ppy.sh/" if user_data['avatar_url'] == '/images/layout/avatar-guest.png' else user_data[
            'avatar_url'],
        url=f"https://osu.ppy.sh/scores/osu/{play_data['best_id']}" if play_data['best_id'] else
        play_data['beatmap']['url']
    )
    score_embed.set_thumbnail(
        url=play_data['beatmapset']['covers']['list']
    )
    stats = play_data['statistics']
    score_embed.add_field(
        name=f'Rank: {rank_emoji[play_data["rank"]]} FC' if play_data[
            'perfect'] else f'Rank: {rank_emoji[play_data["rank"]]}',
        value=f"- **Accuracy:** {round(play_data['accuracy'] * 100, 2)}% "
              f"[{stats['count_300'] + stats['count_geki']}/{stats['count_100'] + stats['count_katu']}/{stats['count_50']}/{stats['count_miss']}]\n"
              f"- **Score:** {play_data['score']}\n"
              f"- **Combo:** {play_data['max_combo']}/{beatmap_data['max_combo']}\n"
              f"- **pp:** {play_data['pp'] if play_data['pp'] else 'N/A'}",

        inline=False
    )

    date_string = play_data['created_at']
    datetime_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
    formatted_date = datetime_obj.strftime('%d %B %Y %H:%M UTC')

    score_embed.set_footer(
        text=f"Recent play by {user_data['username']} on osu!{mode if arg else ''} - {formatted_date}",
        icon_url=f"https://cdn.discordapp.com/emojis/{mode_emoji[mode].split(':')[-1][:-1]}.png?v=1"
    )

    return score_embed


async def multiple_scores_embed(username, mode, arg, score_type, num_scores):
    try:
        user_data = api.get_user(username, mode)
    except:
        raise Exception('Invalid username.')

    try:
        scores_data = api.get_scores(username, mode, score_type, num_scores)
    except:
        raise Exception(f'No {score_type} plays.')

    scores_embed = discord.Embed(
        title=f":flag_{user_data['country_code'].lower()}: {user_data['username']}'s {score_type.capitalize()} Plays",
        url=f"https://osu.ppy.sh/users/{username}/{mode}",
        colour=discord.Colour.blue()
    )

    scores_embed.set_thumbnail(
        url=user_data['avatar_url']
    )

    for i, score_data in enumerate(scores_data):
        beatmap_data = api.get_beatmap(score_data['beatmap']['id'])
        stats = score_data['statistics']
        beatmapset = score_data['beatmapset']
        mods_string = '+' + ''.join(score_data['mods']) if score_data['mods'] else ''
        score_string = (
            f'- **Rank:** {rank_emoji[score_data["rank"]]} FC' if score_data[
                'perfect'] else f'Rank: {rank_emoji[score_data["rank"]]} | '
            f"**Accuracy:** {round(score_data['accuracy'] * 100, 2)}% "
            f"[{stats['count_300'] + stats['count_geki']}/{stats['count_100'] + stats['count_katu']}/{stats['count_50']}/{stats['count_miss']}]\n"
            f"- **Score:** {score_data['score']} | **Combo:** {score_data['max_combo']}/{beatmap_data['max_combo']}"
        )
        scores_embed.add_field(
            name=f"**{i + 1}. {beatmapset['title']} [{score_data['beatmap']['version']}] {score_data['beatmap']['difficulty_rating']}★ {mods_string} | {score_data['pp']}pp**",
            value=score_string,
            inline=False
        )

    scores_embed.set_footer(
        text=f"{score_type.capitalize()} plays by {user_data['username']} on osu!{mode if arg else ''}",
        icon_url=f"https://cdn.discordapp.com/emojis/{mode_emoji[mode].split(':')[-1][:-1]}.png?v=1"
    )

    return scores_embed


async def main():
    await multiple_scores_embed("mrekk", "osu", False, "best", 10)


if __name__ == "__main__":
    asyncio.run(main())
