import asyncio
import time

import aiohttp
import os
if os.getenv('PYCHARM_HOSTED'):
    from environment import *
from discord.ext import tasks

API_ACCESS_TOKEN = ""


@tasks.loop(seconds=86000)
async def refresh_token(logger=None):
    global API_ACCESS_TOKEN

    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"client_id": os.getenv("client_id"),
            "client_secret": os.getenv("client_secret"),
            "grant_type": "client_credentials",
            "scope": "public"}

    async with aiohttp.ClientSession() as session:
        async with session.post("https://osu.ppy.sh/oauth/token", headers=headers, data=data) as resp:
            token_dict = await resp.json()

    API_ACCESS_TOKEN = token_dict['access_token']
    if logger:
        logger.info('API access token refreshed.')


async def get_user(username, mode="osu"):
    headers = {"Accept": "application/json",
               "Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"Bearer {API_ACCESS_TOKEN}"}

    async with aiohttp.ClientSession(headers=headers) as session:
        url = f"https://osu.ppy.sh/api/v2/users/{username}/{mode}?key=username"
        async with session.get(url) as response:
            data = await response.json()

    if 'error' in data.keys():
        raise Exception("Invalid username.")

    return data


async def get_scores(username, mode="osu", score_type="recent", num_scores=1):
    user = await get_user(username, mode)
    user_id = user['id']
    headers = {"Accept": "application/json",
               "Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"Bearer {API_ACCESS_TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        endpoint = f"https://osu.ppy.sh/api/v2/users/{user_id}/scores/{score_type}?mode={mode}&limit={num_scores}"
        async with session.get(endpoint) as response:
            scores = await response.json()

    return scores


async def get_beatmap(beatmap_id):
    headers = {"Accept": "application/json",
               "Content-Type": "application/x-www-form-urlencoded",
               "Authorization": f"Bearer {API_ACCESS_TOKEN}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}") as response:
            data = await response.json()
            return data


async def get_rankings(mode: str, pages: int):
    start_time = time.time()
    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "Authorization": f"Bearer {API_ACCESS_TOKEN}"}

    rtn_rankings = []

    async def fetch_ranks(page):
        nonlocal rtn_rankings
        url = f"https://osu.ppy.sh/api/v2/rankings/{mode}/performance?cursor[page]={page}&filter=all"

        async with session.get(url) as response_raw:
            response = await response_raw.json()

        if 'error' in response.keys():
            raise Exception(response['error'])
        rankings = response['ranking']
        rtn_rankings.extend([ranking for ranking in rankings])

    async with aiohttp.ClientSession(headers=headers) as session:
        todo = [asyncio.create_task(fetch_ranks(page)) for page in range(1, pages + 1)]
        await asyncio.gather(*todo)
        await session.close()

    end_time = time.time()
    print(f"Requesting data: {end_time - start_time}")
    return rtn_rankings
