import requests
import time
import os
import environment
from discord.ext import tasks

token = ""


@tasks.loop(seconds=86000)
async def refresh_token():
    global token

    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"client_id": os.getenv("client_id"),
            "client_secret": os.getenv("client_secret"),
            "grant_type": "client_credentials",
            "scope": "public"}

    r = requests.post("https://osu.ppy.sh/oauth/token", headers=headers, data=data)
    token_dict = r.json()
    token = token_dict['access_token']


def get_user(username, mode="osu"):
    headers = {"Accept": "application/json",
               "Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"Bearer {token}"}
    r = requests.get(f"https://osu.ppy.sh/api/v2/users/{username}/{mode}?key=username", headers=headers)
    return r.json()


def get_scores(username, mode="osu", score_type="recent"):
    user_id = get_user(username, mode)['id']
    headers = {"Accept": "application/json",
               "Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"Bearer {token}"}
    r = requests.get(f"https://osu.ppy.sh/api/v2/users/{user_id}/scores/{score_type}?mode={mode}", headers=headers)
    return r.json()


def get_beatmap(beatmap_id):
    headers = {"Accept": "application/json",
               "Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"Bearer {token}"}
    r = requests.get(f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}", headers=headers)
    return r.json()



