import requests
import uvicorn
import json
from fastapi import FastAPI, UploadFile, Header
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

class track(BaseModel):
    title: str
    artist: str
    explicit: bool
    art_hash: str


@app.get("/")
async def grt_root():
     return('This server is only for use with the shortcut!')

@app.post("/")
async def main(image: UploadFile, artist: Annotated[str | None, Header()] = None, title: Annotated[str | None, Header()] = None, explicit: Annotated[str | None, Header()] = None, playlist: Annotated[str | None, Header()] = None, index: Annotated[str | None, Header()] = None,):
     status = 0

     print(f"Playlist: {playlist}, {image.filename}, ({index}) songs: {artist} - {title}")
     image.read()
     #print(current_track)
     
     
     return {"status": status}