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


async def check_username_and_mode(user, mode, db=None):
    if isinstance(user, discord.Member):
        # TODO - Lookup user's Discord ID in SQL table, get username and mode.
        try:
            # If the mode isn't specified or is a command, look up the user's mode
            row = await db.fetchrow("SELECT * FROM discord_users WHERE discord_id = $1", str(user.id))
            username = row['osu_name']
            if not mode or mode[0] == "-":
                mode = row['mode']
            mode = await check_mode(mode)
        except Exception as e:
            raise Exception("Mentioned user has not linked their osu! account.")
    else:
        username = user.replace(" ", "%20")
        mode = await check_mode(mode)

    return username, mode
