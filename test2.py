import os, json
from dotenv import load_dotenv

#db = json.load(open('./data.json'))
#print(len(db['tracks']))

load_dotenv()
print(os.getenv('SPOTIPY_CLIENT_ID'))