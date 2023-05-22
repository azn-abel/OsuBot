import asyncio
import aiohttp
import os
import environment

V1_API_KEY = os.getenv("V1_API_KEY")
ENDPOINT = "https://osu.ppy.sh/api/"


async def get_user(username, mode="osu"):

    match mode.lower():
        case 'osu':
            mode = 0
        case 'taiko':
            mode = 1
        case 'fruits':
            mode = 2
        case 'mania':
            mode = 3
        case other:
            raise Exception(f"Invalid mode: {other}.")

    async with aiohttp.ClientSession() as session:
        url = f"{ENDPOINT}/get_user?k={V1_API_KEY}&u={username}&m={mode}&type=string"
        async with session.get(url) as response:
            data = await response.json()

    if 'error' in data[0].keys():
        raise Exception("Invalid username.")

    return data[0]


async def main():
    print(await get_user("apotatoa"))


if __name__ == "__main__":
    asyncio.run(main())
