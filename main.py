import requests
import uvicorn
import json
import os, io
from PIL import Image
from fastapi import FastAPI, UploadFile, Header, File
from pydantic import BaseModel
from typing import Annotated

image_folder = './images'

app = FastAPI()

class track(BaseModel):
    title: str
    artist: str
    explicit: bool
    art_hash: str


@app.get("/")
async def grt_root():
     current = open('./data.json')
     template = open('./dt.json')

     if (current.read() != template.read()):
          current.truncate(0)
          current.write(template.read())
     current.close()
     template.close()


     return('Server Ready')

@app.post("/")
async def main(image: Annotated[bytes, File()], artist: Annotated[str | None, Header()] = None, title: Annotated[str | None, Header()] = None, explicit: Annotated[str | None, Header()] = None, playlist: Annotated[str | None, Header()] = None, index: Annotated[str | None, Header()] = None, total: Annotated[str | None, Header()] = None):
     status = 0
     
     import os
     # Check if the image_folder exists
     if not os.path.exists(image_folder):
     # Create the image_folder
          os.makedirs(image_folder)
          print(f"Dir '{image_folder}' created.")


     print(f"Playlist: {playlist} ({index}/{total}) SONG: {artist} - {title}")
     #image.read()
     #open(f'{image_folder}/{index}a.jpeg', 'w').write(await image.read())
     Image.open(io.BytesIO(image)).save(f'{image_folder}/{index}a.jpeg', 'JPEG')
     #print(current_track)3``
     
     db = json.loads(open('./data.json').read())
     
     
     return {"status": status}