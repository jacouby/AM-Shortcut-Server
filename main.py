from collections import Counter
import requests

import os, io, json

import uuid
from dotenv import load_dotenv

import imagehash, PIL

import spotipy
from spotipy import oauth2

from PIL import Image

from fastapi import FastAPI, Response, Request, status, Header, File
from fastapi.responses import RedirectResponse, FileResponse
from pydantic import BaseModel
from typing import Annotated

from urllib.parse import urlencode

load_dotenv()

auth_uuid = ''
spotify_id=os.getenv('SPOTIPY_CLIENT_ID')
spotify_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
spotify_scope = 'playlist-modify-private,playlist-modify-public,user-read-email,user-read-private'
auth_redir = 'http://localhost:8000/auth'
db_file='./data.json'
image_folder = './images'
query_tags=  {'response_type':'code' ,'client_id': spotify_id, 'scope':spotify_scope, 'redirect_uri':auth_redir, 'state':auth_uuid  }
auth_link = f'https://accounts.spotify.com/authorize?{urlencode(query_tags)}'

sp_oauth = oauth2.SpotifyOAuth( spotify_id, spotify_secret, auth_redir ,scope=spotify_scope )
sp = spotipy.Spotify(auth_manager=sp_oauth)

app = FastAPI()

global me
me =''

class track(BaseModel):
    title: str
    artist: str
    explicit: bool
    art_hash: str


@app.get("/")
async def get_root():
     #Generate Auth State

     auth_uuid = uuid.uuid4()
     #os.remove(image_folder)
     #Check if the image_folder exists
     if not os.path.exists(image_folder):
     # Create the image_folder
          os.makedirs(image_folder)
          print(f"Dir '{image_folder}' created.")

     # Define the file path
     file_path = 'data.json'

     # Check if the DB exists
     if not os.path.exists(file_path):
     # Create DB
          with open(file_path, 'w') as file:
          # Initialize with an empty JSON object
               json.dump({}, file)

    # Open both files within a context manager
     with open('./data.json', 'r+') as current, open('./dt.json', 'r') as template:
        # Read contents of both files
        current_data = current.read()
        template_data = template.read()

        # Compare the contents
        if current_data != template_data:
            # Truncate the current file and write the template content
            current.seek(0)  # Move the file pointer to the beginning
            current.truncate()  # Truncate the file
            current.write(template_data)  # Write the template data

     return RedirectResponse(auth_link)

@app.get("/auth")
async def auth(response: Response, code: str = None, ):
     if code == None:
          response.status_code = status.HTTP_401_UNAUTHORIZED
          return 'No code given. Please Retry'
     token_info = sp_oauth.get_access_token(code)
     return FileResponse('auth_return.html')



@app.post("/")
async def main(image: Annotated[bytes, File()], artist: Annotated[str | None, Header()] = None, title: Annotated[str | None, Header()] = None, explicit: Annotated[str | None, Header()] = None, album: Annotated[str | None, Header()] = None, index: Annotated[str | None, Header()] = None, total: Annotated[str | None, Header()] = None):

     print(f"({index}/{total}) album: {album} track: {artist} - {title}")
     
     a_image_loc = f'{image_folder}/{index}a.jpeg'
     Image.open(io.BytesIO(image)).save(a_image_loc, 'JPEG')

     with open(db_file, 'r') as file:
          data = json.load(file)

     if 'tracks' not in data:
          data['tracks'] = {}

     track_data = {
          "index": index,
          "title": title,
          "artist": artist,
          "album": album,
          "explicit": explicit,
          "found_image": False,
          "spotify_uri": '' 
     }

     first_song_uris = []

     data['tracks'].append(track_data)
     
     def check_matches(search):
          for track in search['tracks']['items']:
               image_url = track['album']['images'][0]['url']
               r = requests.get(image_url)

               if r.status_code != 200:
                    print('error downloading cover')
                    continue
               
               s_image_loc = f'./{image_folder}/{index}s.jpeg'
               

               with open(s_image_loc, 'wb') as f:
                    f.write(r.content)

               s_cover = Image.open(s_image_loc)
               s_cover_hash = imagehash.phash(s_cover)

               a_cover = Image.open(a_image_loc)
               a_cover_hash = imagehash.phash(a_cover)
               hash_diff = s_cover_hash - a_cover_hash          

               if (hash_diff <= 3):
                    track_data['found_image'] = True
                    print(f'Hashes: S = {s_cover_hash}, A = {a_cover_hash}')
                    print(hash_diff)
                    print(track['uri'])
                    track_data['spotify_uri'] = track['uri']
                    break
          
               if (track_data['spotify_uri'] == ''):
                    try:
                         first_song_uris.append(search['tracks']['items'][0]['uri'])
                    except IndexError:
                         print('No Matches At All')
          
     queries = [
          f"track:{title} artist:{artist} album:{album}",
          f"track:{title} {artist} album:{album}",
          f"track:{title} artist:{artist} {album}",
          f"track:{title} {artist} {album}",
          f"{title} {artist} album:{album}",
          f"{title} artist:{artist} {album}",
          f"track:{title}",
          title,
          #f"{title} {artist} {album}",
          #f"{title} {artist}"
     ]
     for query in queries:
          if (track_data['spotify_uri'] == '' ):
               search = sp.search(query,50,0,'track')
               search_total = search['tracks']['total']

               if (search_total != 0):
                    print(search)
                    check_matches(search)
               print(search_total)

     if (track_data['spotify_uri'] == ''):
          print('Using First Option')
          data_count = Counter(first_song_uris)
          print(max(first_song_uris, key=data_count.get))
          track_data['spotify_uri'] = max(first_song_uris, key=data_count.get)
     
     # Write the updated data back to the JSON file
     with open(db_file, 'w') as file:
          json.dump(data, file, indent=4)
     
     return {"status": 'success'}

@app.get('/playlist_gen')
async def gen_playlist(pl_name: str = 'Transfered Playlist'):
     me = sp.me()['id']
     print(me)
     print('Starting Playlist Creation')
     with open(db_file, 'r') as file:
          data = json.load(file)['tracks']
     total = len(data)
     print(f'Loading {total} From data.json into memory')
     uris = []
     print(pl_name)
     for track in data:
          #print(f"""TRACK {track['index']}/{total} /n {track['artist']} - {track['title']} /n""")
          uris.append(track['spotify_uri'])

     created = sp.user_playlist_create(user=me, name=pl_name, public=False, description="Playlist Generated by https://github.com/jacouby/AM-Shortcut-Server" )
     print('Playlist Created')
     print(created)

     def add_items(uri_chunk):
          add = sp.playlist_add_items(created['id'],uri_chunk)
          print('Added Items')
          print(add)

     for i in range(0, len(uris), 100):
          section = uris[i:i + 100]
          add_items(section)
               
     