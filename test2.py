import json

# Load JSON data from a file named data.json
with open('data.json', 'r') as file:
    data = json.load(file)

missing_songs = []

for x in data['tracks']:
    if (x['spotify_uri'] == ''):
        missing_songs.append(x)

print("Missing Songs:", missing_songs)
