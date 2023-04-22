import asyncio

import requests
import os
if os.getenv('PYCHARM_HOSTED'):
    from environment import *
from discord.ext import tasks

API_ACCESS_TOKEN = ""


@tasks.loop(seconds=86000)
async def refresh_token(logger):
    global API_ACCESS_TOKEN

    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"client_id": os.getenv("client_id"),
            "client_secret": os.getenv("client_secret"),
            "grant_type": "client_credentials",
            "scope": "public"}

    r = requests.post("https://osu.ppy.sh/oauth/token", headers=headers, data=data)
    token_dict = r.json()
    API_ACCESS_TOKEN = token_dict['access_token']
    logger.info('API access token refreshed.')


def get_user(username, mode="osu"):
    headers = {"Accept": "application/json",
               "Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"Bearer {API_ACCESS_TOKEN}"}
    r = requests.get(f"https://osu.ppy.sh/api/v2/users/{username}/{mode}?key=username", headers=headers)
    return r.json()


def get_scores(username, mode="osu", score_type="recent", num_scores=1):
    user = get_user(username, mode)
    user_id = user['id']
    headers = {"Accept": "application/json",
               "Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"Bearer {API_ACCESS_TOKEN}"}
    r = requests.get(f"https://osu.ppy.sh/api/v2/users/{user_id}/scores/{score_type}?mode={mode}&limit={num_scores}", headers=headers)
    return r.json()


def get_beatmap(beatmap_id):
    headers = {"Accept": "application/json",
               "Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"Bearer {API_ACCESS_TOKEN}"}
    r = requests.get(f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}", headers=headers)
    return r.json()


def get_rankings(mode: str, pages: int):
    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "Authorization": f"Bearer {API_ACCESS_TOKEN}"}

    rtn_rankings = []
    for i in range(1, pages + 1):
        response = requests.get(f"https://osu.ppy.sh/api/v2/rankings/{mode}/performance?cursor[page]={i}&filter=all", headers=headers).json()
        rankings = response['ranking']
        for ranking in rankings:
            rtn_rankings.append(ranking)

    return rtn_rankings


# asyncio.run(refresh_token())


if __name__ == "__main__":
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"client_id": os.getenv("client_id"),
            "client_secret": os.getenv("client_secret"),
            "grant_type": "client_credentials",
            "scope": "public"}

    r = requests.post("https://osu.ppy.sh/oauth/token", headers=headers, data=data)
    token_dict = r.json()
    API_ACCESS_TOKEN = token_dict['access_token']
    rankings = get_rankings('osu', 5)
    penis = [ranking['user']['country_code'] for ranking in rankings]
    penis.sort()
    print(penis)
    print(len(penis))
    print(list(set(penis)))
    print(len(list(set(penis))))

