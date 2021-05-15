from bs4 import BeautifulSoup
import requests
import json


def main():
    username = "skip_2mylu" # input("Enter your osu! username: ").strip().lower()
    html_text = requests.get(f'https://osu.ppy.sh/users/{username}').text

    soup = BeautifulSoup(html_text, 'lxml')
    user_data = json.loads(soup.find_all('script')[-2].contents[0].strip())
    avatar_url = user_data['avatar_url']
    global_rank = user_data['statistics']['global_rank']
    with open("data.json", "w") as outfile:
        outfile.write(json.dumps(user_data, indent = 4))
    print(global_rank)
    print(avatar_url)


def get_user_data(username):
    user_html = requests.get(f'https://osu.ppy.sh/users/{username}').text

    user_soup = BeautifulSoup(user_html, 'lxml')
    data = json.loads(user_soup.find_all('script')[-2].contents[0].strip())
    return data


if __name__ == "__main__":
    main()
