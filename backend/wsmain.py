import os
import json
import asyncio
import websockets
import aiohttp
from datetime import datetime
from flask import Flask, jsonify, request, Request, render_template, make_response, redirect, url_for
import asyncio
import io
import base64
import io
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import random, string
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
import json


app = Flask(__name__)
app.debug = True
hr_data = {}

WS_CONNECTION = "wss://ws.tryterra.co/connect"


async def generate_token():
    async with aiohttp.ClientSession() as session:
        headers = {
            "Accept": "application/json",
            "dev-id": "test-screening-dev-hZNKTHrzFJ",
            "x-api-key": "3cb3a8b7c0321ef5e54a67ae64660eacd5bd1018fee36997921ed63d5109793f"
        }

        async with session.post("https://ws.tryterra.co/auth/developer", headers=headers) as resp:
            token = await resp.json()
            return token["token"]

async def init_ws():
    while True:
        print("ASDASDAS")
        token = await generate_token()
        try:
            print(token)
            async with websockets.connect(WS_CONNECTION) as socket:
                expecting_heart_beat_ack = False

                async def heart_beat_after(n):
                    await asyncio.sleep(n)
                    await heart_beat()
                async def heart_beat():
                    print("HEART BEAT")
                    nonlocal expecting_heart_beat_ack
                    heart_beat_payload = json.dumps({'op': 0})
                    asyncio.create_task(socket.send(heart_beat_payload))
                    expecting_heart_beat_ack = True
                

                async for message in socket:
                    message = json.loads(message)
                    print(message)
                    if message["op"] == 2:
                        asyncio.create_task(heart_beat_after(message["d"]["heartbeat_interval"] / 1000))
                        payload = json.dumps(generate_payload(token))
                        await socket.send(payload)
                        print(payload)
                    if message["op"] == 5:
                        if message['d']['val'] <= 0.1:
                            continue
                        epoch_time = int(datetime.strptime(message['d']['ts'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
                        hr_data[epoch_time] = message['d']['val']
                        json.dump(hr_data, open("hr_data.json", "w"))

        except Exception as e:
            print(e)

def generate_payload(token):
    return {
        "op": 3,
        "d": {
            "token": token,
            "type": 1
        }
    }
if __name__ == "__main__":
    asyncio.run(init_ws())