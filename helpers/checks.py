import discord


async def check_mode(mode: str):
    if not mode:
        return 'osu'
    mode = mode.lower()
    if mode in ['taiko', 'fruits', 'mania', 'catch']:
        mode = 'fruits' if mode == 'catch' else mode
    else:
        mode = 'osu'
    return mode


async def check_username_and_mode(username, mode):
    if isinstance(username, discord.Member):
        # TODO - Lookup user's Discord ID in SQL table, get username and mode.
        try:
            # Look up the user
            if not mode:
                # Look up the user's mode
                pass
            else:
                mode = await check_mode(mode)
            raise Exception()
        except Exception as e:
            raise Exception("Mentioned user has not linked their osu! account.")
    else:
        mode = await check_mode(mode)

    return username, mode
