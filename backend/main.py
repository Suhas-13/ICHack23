import os
import json
import asyncio
import websockets
import aiohttp
from datetime import datetime
from flask import Flask, jsonify, request, Request, render_template, make_response, redirect, url_for
import asyncio
import io
import glob
import random, string
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
from deepface import DeepFace


app = Flask(__name__)
app.debug = True

hr_list = []
time_list = []
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

def post_processing(database_fr):
    temp = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    count = 0
    database_fr2=dict()
    for i in database_fr:
      frame=database_fr[i]['image_data']
      try:
          face_analysis = DeepFace.analyze(img_path=frame,actions=["emotion","dominant_emotion"])
      except ValueError : # catches the error when the face cannot be detected
            continue
      d_emotion = face_analysis[0]['dominant_emotion']
      temp[d_emotion] += 1
      count += 1
      if count % 5 == 0:  # takes the average of 5 frames
            dominant_emotion = max(temp, key= lambda x: temp[x])
            database_fr2[i]=[database_fr[i],dominant_emotion]
            temp = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    return(database_fr2)


@app.route("/video/<video_id>", methods=["GET"])
def video(video_id):
    if video_id in videos:
        return render_template("/show_video.html", video_id = video_id, source_url = videos[video_id]["source_url"], title = videos[video_id]["title"])
    else:
        return render_template("/show_video.html", video_id = video_id, source_url = videos[video_id]["source_url"], title = videos[video_id]["title"])
@app.route("/create_video", methods=["POST"])
def create_video():
    request_data = request.get_json()
    video_id = request_data['video_id']
    videos[video_id] = {"image_url": request_data["image_url"], "source_url": request_data['source_url'], "title": request_data['title']}
    return jsonify({"success": True})

@app.route('/')
def index():
    return render_template("/index.html")

@app.route('/register')
def register():
    return render_template("/register.html")

@app.route('/login')
def login():
    return render_template("/login.html")

@app.route('/company-login')
def company_login():
    return render_template("/company_login.html")

@app.route('/company-register')
def company_register():
    return render_template("/company_register.html")

@app.route("/user-dashboard", methods=["POST", "GET"])
def user_dashboard():
    if request.cookies.get('username') is not None:
        username = request.cookies.get('username')
        if username in accounts:
            return render_template("/user_dashboard.html", username=username, accounts=accounts, videos=videos)
        else:
            accounts[username] = {"balance": 0}
            return render_template("/user_dashboard.html", username=username, accounts=accounts, videos=videos)
    if "username" not in request.form:
        return render_template("/login.html")
    username = request.form["username"]
    password = request.form["password"]
    if username in accounts:
        resp = make_response( render_template("/user_dashboard.html", username=username, accounts=accounts, videos=videos))
    else:
        accounts[username] = {"balance": 0}
        resp = make_response( render_template("/user_dashboard.html", username=username, accounts=accounts, videos=videos))
    resp.set_cookie('username', username)
    return resp

@app.route("/add-content")
def add_content():
    return render_template("/add_film.html")

@app.route("/video-add", methods=["POST"])
def video_add():
    if request.method == "POST":
        title =request.form['title']
        image_url = request.form['image_url']
        price = request.form['price']
        random_str = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        videos[random_str] = {"title": title, "image_url": image_url, "price": price, "source_url": request.form['source_url']}
        
        return redirect(url_for("company_dashboard"))

@app.route("/company-dashboard", methods=["POST", "GET"])
def company_dashboard():
    if request.cookies.get('username') is not None:
        username = request.cookies.get('username')
        if username in accounts:
            return render_template("/company_dashboard.html", username=username, accounts=accounts, videos=videos)
        else:
            accounts[username] = {"balance": 0}
            return render_template("/company_dashboard.html", username=username, accounts=accounts, videos=videos)
    username = request.form["username"]
    password = request.form["password"]
    if username in accounts:
        resp = make_response( render_template("/company_dashboard.html", username=username, accounts=accounts, videos=videos))
    else:
        accounts[username] = {"videos": []}
        resp = make_response( render_template("/company_dashboard.html", username=username, accounts=accounts, videos=videos))
    resp.set_cookie('username', username)
    return resp

@app.route("/process_image", methods=["POST"])
def process_image():
    request_data = request.get_json()
    image_data = request_data['image_data']
    epoch_time = request_data['epoch_time']
    session_id = request_data['session_id']
    account_id = request.cookies.get('username')
    if account_id not in accounts:
        accounts[account_id] = {"active_session": None}
    if session_id not in sessions:
        sessions[session_id] = {"images": {}, "hr": {}} # hr is heart rate
        accounts[account_id]['active_session'] = session_id
    if "images" not in sessions[session_id]:
        sessions[session_id]['images'] = {}
        sessions[session_id]['video_id'] = request_data["video_id"]
    sessions[session_id]['images'][epoch_time] = {"image_data": image_data}
    return jsonify({"success": True})

@app.route("/finish_session", methods=["POST"])
def finish_session():
    request_data = request.get_json()
    for account in accounts:
        if accounts[account]['active_session'] == request_data['session_id']:
            accounts[account]['active_session'] = None
            accounts[account]["balance"] += videos[sessions[request_data['session_id']]['video_id']]["price"]
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
            del session['hr']

            ml_output = post_processing(sessions[request_data['session_id']]['images'])
            sessions[request_data['session_id']]['ml_output'] = ml_output

            return jsonify(ml_output)



if __name__ == "__main__":
    #asyncio.run(init_ws())
    port = int(os.environ.get("PORT", 3000))
    app.run(port=port)