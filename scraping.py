from bs4 import BeautifulSoup
import requests
import json


def main():
    username = "yenator07"  # input("Enter your osu! username: ").strip().lower()
    html_text = requests.get(f'https://osu.ppy.sh/users/{username}').text

    soup = BeautifulSoup(html_text, 'lxml')
    user_data = json.loads(soup.find_all('script')[-2].contents[0].strip())
    most_played = json.loads(soup.find_all('script')[-4].contents[0].strip())
    avatar_url = user_data['avatar_url']
    global_rank = user_data['statistics']['global_rank']
    with open("data.json", "w") as outfile:
        outfile.write(json.dumps(user_data, indent=4))
    with open("most.json", "w") as outfile:
        outfile.write(json.dumps(most_played, indent=4))
    for script in soup.find_all('script')[-6:-1]:
        with open(f"{script['id'][5:]}.json", "w") as outfile:
            outfile.write(json.dumps(json.loads(script.contents[0].strip()), indent=4))
        print(script['id'][5:])
    print(soup.find_all('script'))
    print(soup.find('script', id='json-perPage').contents[0].strip())
    print(global_rank)
    print(avatar_url)


def get_data(username, mode='osu'):
    user_html = requests.get(f'https://osu.ppy.sh/users/{username}/{mode}').text

    user_soup = BeautifulSoup(user_html, 'lxml')
    scripts = user_soup.find_all('script')
    user_data = json.loads(scripts[-2].contents[0].strip())
    play_data = json.loads(scripts[-4].contents[0].strip())
    return user_data, play_data


def get_extras_data(username, mode='osu'):
    user_html = requests.get(f'https://osu.ppy.sh/users/{username}/{mode}').text

    user_soup = BeautifulSoup(user_html, 'lxml')
    script = user_soup.find('script', id='json-extras')
    extras_data = json.loads(script.contents[0].strip())
    return extras_data


def get_beatmap_data(set_id, map_id, mode='osu'):
    set_page_html = requests.get(f'https://osu.ppy.sh/beatmapsets/{set_id}#{mode}/{map_id}').text
    set_page_soup = BeautifulSoup(set_page_html, 'lxml')
    set_data = json.loads(set_page_soup.find_all('script', id="json-beatmapset")[0].contents[0].strip())
    map_data, = [x for x in set_data['beatmaps'] if x['id'] == map_id]

    return map_data


def convert_time(seconds):
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return f"{hour}h {minutes}m {seconds}s"


if __name__ == "__main__":
    main()
