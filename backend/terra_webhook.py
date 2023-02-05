import os
import json
import asyncio
import websockets
import aiohttp
from datetime import datetime
from flask import Flask, jsonify, request, Request

app = Flask(__name__)
app.debug = True

hr_list = []
time_list = []
phone_uid_to_accounts = {}
sessions = {}
accounts = {}
videos = {}

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
        token = await generate_token()
        try:
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
                    if message["op"] == 2:
                        asyncio.create_task(heart_beat_after(message["d"]["heartbeat_interval"] / 1000))
                        payload = json.dumps(generate_payload(token))
                        await socket.send(payload)
                        print(payload)
                    if message["op"] == 5:
                        if message['d']['val'] <= 0.1:
                            continue
                        print(message)
                        uid = message["uid"]
                        if uid not in phone_uid_to_accounts:
                            continue
                        else:
                            for account in accounts:
                                active_session = accounts[account]['active_session']
                                if active_session is not None and active_session in sessions:
                                    if "hr" not in sessions[active_session]:
                                        sessions[active_session]['hr'] = {}
                                    epoch_time = int(datetime.strptime(message['d']['ts'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
                                    sessions[active_session]['hr'][epoch_time] = message['d']['val']

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

# end of websockets 

# start of web app

@app.route("/create_video", methods=["POST"])
def create_video():
    request_data = request.get_json()
    video_id = request_data['video_id']
    videos[video_id] = {"source_url": request_data['source_url'], "title": request_data['title']}
    return jsonify({"success": True})

@app.route("/process_image", methods=["POST"])
def process_image():
    request_data = request.get_json()
    image_data = request_data['image_data']
    epoch_time = request_data['epoch_time']
    session_id = request_data['session_id']
    account_id = request_data['account_id']
    if account_id not in accounts:
        accounts[account_id] = {"active_session": None}
    if session_id not in sessions:
        sessions[session_id] = {"images": {}, "hr": {}} # hr is heart rate
        accounts[account_id]['active_session'] = session_id
    if "images" not in sessions[session_id]:
        sessions[session_id]['images'] = {}
        sessions[session_id]['video_id'] = request_data["video_id"]
    sessions[session_id]['images'][epoch_time] = {"image_data": image_data, "video_time": request_data["video_time"]}
    return jsonify({"success": True})

@app.route("/finish_session", methods=["POST"])
def finish_session():
    request_data = request.get_json()
    for account in accounts:
        if accounts[account]['active_session'] == request_data['session_id']:
            accounts[account]['active_session'] = None
            # iterate through all images. find closest heart rate to each image
            session = sessions[request_data['session_id']]
            for image_time in session['images']:
                closest_hr = None
                closest_hr_time = None
                for hr_time in session['hr']:
                    if closest_hr is None or abs(image_time - hr_time) < abs(image_time - closest_hr_time):
                        closest_hr = session['hr'][hr_time]
                        closest_hr_time = hr_time
                session['images'][image_time]['hr'] = closest_hr
                session['images'][image_time]['hr_time'] = closest_hr_time
            del session['hr']

            # do machine learning stuff here
            
            return jsonify({"success": True})



if __name__ == "__main__":
    asyncio.run(init_ws())
    port = int(os.environ.get("PORT", 3000))
    app.run(port=port)