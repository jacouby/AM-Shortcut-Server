import requests

import os, io, json

import uuid
from dotenv import load_dotenv

import imagehash, PIL

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from PIL import Image

from fastapi import FastAPI, UploadFile, Header, File
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Annotated

from urllib.parse import urlencode

load_dotenv()

auth_uuid = uuid.uuid4()
spotify_id=os.getenv('SPOTIPY_CLIENT_ID')
spotify_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
spotify_scope = os.getenv("SPOTIFY_SCOPE")
auth_redir = 'http://localhost:8000/auth'
db_file='./data.json'
image_folder = './images'
query_tags=  {'response_type':'code' ,'client_id': spotify_id, 'scope':spotify_scope, 'redirect_uri':auth_redir, 'state':auth_uuid  }
auth_link = f'https://accounts.spotify.com/authorize?{urlencode(query_tags)}'


app = FastAPI()

class track(BaseModel):
    title: str
    artist: str
    explicit: bool
    art_hash: str

sp = 'sp_empty'

@app.get("/")
async def get_root():
    # Check if the image_folder exists
     if not os.path.exists(image_folder):
     # Create the image_folder
          os.makedirs(image_folder)
          print(f"Dir '{image_folder}' created.")

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
async def auth():
     sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=spotify_id, client_secret=spotify_secret), retries=10)


@app.post("/")
async def main(image: Annotated[bytes, File()], artist: Annotated[str | None, Header()] = None, title: Annotated[str | None, Header()] = None, explicit: Annotated[str | None, Header()] = None, album: Annotated[str | None, Header()] = None, index: Annotated[str | None, Header()] = None, total: Annotated[str | None, Header()] = None):

     print(f"({index}/{total}) album: {album} track: {artist} - {title}")
     
     a_image_loc = f'{image_folder}/{index}a.jpeg'
     Image.open(io.BytesIO(image)).save(a_image_loc, 'JPEG')
     
     db = json.loads(open('./data.json').read())

     with open(db_file, 'r') as file:
          data = json.load(file)

     if 'tracks' not in data:
          data['tracks'] = {}

     track_data = {
          "index": index,
          "title": title,
          "artist": artist,
          "ablum": album,
          "explicit": explicit,
          "spotify_uri": '' 
     }

     data['tracks'].append(track_data)
     
     query = f"track:{title} artist:{artist} album:{album}"

     search = sp.search(query,20,0,'track')
     print(search)
     
     if (search == 0):
          search = sp.search(query,20,0,'track')

     for track in search['tracks']['items']:
          image_url = track['album']['images'][0]['url']
          r = requests.get(image_url)

          if r.status_code != 200:
               print('error downloading cover')
          
          s_image_loc = f'./{image_folder}/{index}s.jpeg'

          with open(s_image_loc, 'wb') as f:
               f.write(r.content)

          s_cover = Image.open(s_image_loc)
          s_cover_hash = imagehash.phash(s_cover)
          print(s_cover_hash)

          a_cover = Image.open(a_image_loc)
          a_cover_hash = imagehash.phash(a_cover)
          hash_diff = s_cover_hash - a_cover_hash
          print(hash_diff)

          if (hash_diff == 0):
               print(track['uri'])
               track_data['spotify_uri'] = track['uri']
               break

     # Write the updated data back to the JSON file
     with open(db_file, 'w') as file:
          json.dump(data, file, indent=4)
     
     
     return {"status": 'success'}