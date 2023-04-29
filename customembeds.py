import discord
from datetime import datetime
from emoji import *
from helpers.ppCalculation import computeTotalValue
import api


async def info_embed(username, mode):
    try:
        user_data = await api.get_user(username, mode)
        statistics = user_data['statistics']
        global_rank = statistics['global_rank']
        country_rank = statistics['country_rank']
    except KeyError:
        raise Exception('Invalid username.')

    reply_embed = discord.Embed(
        title=f":flag_{user_data['country_code'].lower()}: {user_data['username']}'s osu!{mode if mode != 'osu' else ''} Profile",
        colour=0xff79b8
    )

    reply_embed.add_field(
        name="",
        value=(
            f"- **Global Rank:** " + (f" #{global_rank:,}" if global_rank else "Unranked") + " | "
            f"**Country Rank:** " + (f" #{country_rank:,}" if country_rank else "Unranked") + "\n"
            f"- **PP:** {statistics['pp']} | **Accuracy:** {round(statistics['hit_accuracy'], 2)}%"
        )
    )

    if user_data['avatar_url'] == '/images/layout/avatar-guest.png':
        reply_embed.set_thumbnail(url="https://a.ppy.sh/")
    else:
        reply_embed.set_thumbnail(url=user_data['avatar_url'])

    date_string = user_data['join_date']
    datetime_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')
    formatted_date = datetime_obj.strftime('%d %B %Y')
    reply_embed.set_footer(
        text=f"{user_data['username']} joined osu!{mode if mode != 'osu' else mode} on {formatted_date}",
        icon_url=f"https://cdn.discordapp.com/emojis/{mode_emoji[mode].split(':')[-1][:-1]}.png?v=1"
    )
    return reply_embed


async def single_score_embed(username, mode, score_type):

    user_data = await api.get_user(username, mode)
    if 'error' in user_data.keys():
        raise Exception('Invalid username.')

    try:
        score = await api.get_scores(username, mode, score_type)
        score = score[0]
        beatmapset = score['beatmapset']
    except Exception:
        raise Exception(f'No {score_type} plays.')

    beatmap = await api.get_beatmap(score['beatmap']['id'])
    attributes = (await api.get_beatmap_attributes(score['beatmap']['id'], mode, mods=score['mods']))['attributes']
    possible_pp, fc_accuracy = computeTotalValue(score, beatmap, attributes)

    mods_string = ''
    for mod in score['mods']:
        mods_string += f"{mod} "
    score_embed = discord.Embed(
        description=f'Modifiers: {mods_string}' if score['mods'] else '',
        colour=0xff79b8
    )
    score_embed.set_author(
        name=f"{beatmapset['title']} [{score['beatmap']['version']}] {score['beatmap']['difficulty_rating']}★",
        icon_url="https://a.ppy.sh/" if user_data['avatar_url'] == '/images/layout/avatar-guest.png' else user_data[
            'avatar_url'],
        url=f"https://osu.ppy.sh/scores/osu/{score['best_id']}" if score['best_id'] else
        score['beatmap']['url']
    )
    score_embed.set_thumbnail(
        url=score['beatmapset']['covers']['list']
    )
    stats = score['statistics']
    score_embed.add_field(
        name=f'Rank: {rank_emoji[score["rank"]]} FC' if score[
            'perfect'] else f'Rank: {rank_emoji[score["rank"]]}',
        value=f"- **Accuracy:** {round(score['accuracy'] * 100, 2)}% "
              f"[{stats['count_300']}/{stats['count_100']}/{stats['count_50']}/{stats['count_miss']}]\n"
              f"- **Score:** {score['score']}\n"
              f"- **Combo:** {score['max_combo']}/{beatmap['max_combo']}\n"
              f"- **pp:** {score['pp'] if score['pp'] else 'N/A'} / {round(possible_pp, 3)} for {round(fc_accuracy * 100, 2)}% FC",

        inline=False
    )

    date_string = score['created_at']
    datetime_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
    formatted_date = datetime_obj.strftime('%d %B %Y %H:%M UTC')

    score_embed.set_footer(
        text=f"Play by {user_data['username']} on osu!{mode if mode != 'osu' else mode} - {formatted_date}",
        icon_url=f"https://cdn.discordapp.com/emojis/{mode_emoji[mode].split(':')[-1][:-1]}.png?v=1"
    )

    return score_embed


async def multiple_scores_embed(username, mode, score_type, num_scores):

    user_data = await api.get_user(username, mode)
    if 'error' in user_data.keys():
        raise Exception('Invalid username.')

    scores_data = await api.get_scores(username, mode, score_type, num_scores)

    scores_embed = discord.Embed(
        title=f":flag_{user_data['country_code'].lower()}: {user_data['username']}'s {score_type.capitalize()} Plays",
        url=f"https://osu.ppy.sh/users/{username}/{mode}",
        colour=0xff79b8
    )

    scores_embed.set_thumbnail(
        url=user_data['avatar_url']
    )

    if len(scores_data) == 0:
        scores_embed.description = f"No {score_type} plays."

    for i, score_data in enumerate(scores_data):
        beatmap_data = await api.get_beatmap(score_data['beatmap']['id'])
        stats = score_data['statistics']
        beatmapset = score_data['beatmapset']
        mods_string = '+' + ''.join(score_data['mods']) if score_data['mods'] else ''

        score_string = (
            (f'**Rank:** {rank_emoji[score_data["rank"]]} FC | ' if score_data[
                'perfect'] else f'**Rank:** {rank_emoji[score_data["rank"]]} | ') +
            f"**Accuracy:** {round(score_data['accuracy'] * 100, 2)}% "
            f"[{stats['count_300']}/{stats['count_100']}/{stats['count_50']}/{stats['count_miss']}]\n"
            f"**Score:** {score_data['score']} | **Combo:** {score_data['max_combo']}/{beatmap_data['max_combo']}"
        )
        score_title = f"**{i + 1}. {beatmapset['title']} [{score_data['beatmap']['version']}] "\
                      f"{score_data['beatmap']['difficulty_rating']}★ {mods_string} | {score_data['pp'] if score_data['pp'] else 'N/A'} pp**"
        score_url = f"https://osu.ppy.sh/scores/osu/{score_data['best_id']}" if score_data['best_id'] else score_data['beatmap']['url']
        scores_embed.add_field(
            name="",
            value=f"[{score_title}]({score_url}) {score_string}",
            inline=False
        )

    scores_embed.set_footer(
        text=f"{score_type.capitalize()} plays by {user_data['username']} on osu!{mode if mode != 'osu' else mode}",
        icon_url=f"https://cdn.discordapp.com/emojis/{mode_emoji[mode].split(':')[-1][:-1]}.png?v=1"
    )

    return scores_embed
