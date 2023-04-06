""" Download matches replays from battle simulator for machine learning training. """

import requests

# 1. download matches id
#url_user = "https://replay.pokemonshowdown.com/search.json?user={}"
url_search_by_format = "https://replay.pokemonshowdown.com/search.json?format={}&page={}"
formats = ["gen9ou", "gen9uu", "gen9ru", "gen9nu", "gen9pu",
           "gen8randombattle", "gen8ou", "gen8uu", "gen8ru", "gen8nu", "gen8pu",
           "gen7randombattle", "gen7ou", "gen7uu", "gen7ru", "gen7nu", "gen7pu",
           "gen6randombattle", "gen6ou", "gen6uu", "gen6ru", "gen6nu", "gen6pu"]
cur_format = 0
matches_id = list()
request = [0] * 51
page = 1
full = int()

print(str(), file=open("randombattlesids.txt", 'w', encoding='utf-8'))

while cur_format < len(formats):
    url = url_search_by_format.format(formats[cur_format], str(page))
    request = requests.get(url)

    if isinstance(request.json(), str):  # error message, all pages downloaded
        print("Next url {} (last page: {})".format(url, page))
        cur_format += 1
        page = 1

    else:  # request.json() is a list of entries
        matches_id = [e['id'] for e in request.json()]

        print('\n'.join([str(id) for id in matches_id[(page > 1):]]), file=open("out1.txt", 'a', encoding='utf-8'))

        page += 1
        full += 1
        if not full % 50:
            print("running: {}".format(full))

# 2 from id, download turn-by-turn match replay and store on disk
url_replay = None

