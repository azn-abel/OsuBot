async def check_mode(mode: str):
    mode = mode.lower()
    if mode in ['taiko', 'fruits', 'mania', 'catch']:
        mode = 'fruits' if mode == 'catch' else mode
    else:
        mode = 'osu'
    return mode
