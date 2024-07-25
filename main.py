import requests
import uvicorn
import json
from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.get("/")
async def grt_root():
     return('This server is only for use with the shortcut!')

@app.post("/")
async def main(file: UploadFile):
     status = 0
     
     return {"status": status}