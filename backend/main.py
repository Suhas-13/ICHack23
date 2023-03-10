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
import matplotlib
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
from deepface import DeepFace


app = Flask(__name__)
app.debug = True

hr_list = []
time_list = []
sessions = {}
accounts = {}
videos = {}

# end of websockets 

# start of web app

def ml_plotter(database_fr2):
    plt.clf()
    data=list(database_fr2.values())
    x=list(database_fr2.keys())
    x1=[0]*len(data)
    x2=[0]*len(data)
    x3=[0]*len(data)
    x4=[0]*len(data)
    x5=[0]*len(data)
    x6=[0]*len(data)
    x7=[0]*len(data)
    for i in range(len(data)):
        if data[i] == 'angry':
            x1[i]=x1[i]+1
        elif data[i] =='disgust':
            x2[i]=x2[i]+1
        elif data[i] =='fear':
            x3[i]=x2[i]+1
        elif data[i] =='happy':
            x4[i]=x2[i]+1
        elif data[i] =='sad':
            x5[i]=x2[i]+1
        elif data[i] =='surprise':
            x6[i]=x2[i]+1
        elif data[i] =='neutral':
            x7[i]=x2[i]+1

    sns.lineplot(x=x, y=x1,label='angry')
    sns.lineplot(x=x, y=x2,label='disgust')
    sns.lineplot(x=x, y=x3,label='fear')
    sns.lineplot(x=x, y=x4,label='happy')
    sns.lineplot(x=x, y=x5,label='sad')
    sns.lineplot(x=x, y=x6,label='surprise')
    sns.lineplot(x=x, y=x7,label='neutral')
    plt.xlabel("Time Elapsed (ms)")
    plt.ylabel("Emotion ")
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    plt.savefig('static/plot2.png', format='jpg')
    my_stringIObytes.seek(0)
    my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode()
    return my_base64_jpgData

def plotter( hrs):# image and hrs are of the structure {time: image_data} and (time: hr_data}
    plt.clf()
    x=list(hrs.keys())
    y=list(hrs.values())
    sns.lineplot(x=x,y=y,color='red')
    plt.xlabel("Time Elapsed (ms)")
    plt.ylabel("Heart Beat (bpm)")
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    plt.savefig('static/plot.png', format='jpg')
    my_stringIObytes.seek(0)
    my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode()
    return my_base64_jpgData

def average_to_150(dict):
    arr= list(dict.values())
    arr2=[]
    dict1={}
    for i in range(1000):
        sum=0
        for j in range(0,6):
            sum=sum+arr[i]
        sum=sum/6.0
        arr2.append(sum)

    j=0
    for i in range(0,len(dict),6):
        dict1[i]=arr2[j]
        j=j+1
    return (dict1)

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
            database_fr2[i]=dominant_emotion # if this is time it works 
            temp = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    return(database_fr2)


@app.route("/video", methods=["GET"])
def video():
    video_id = request.args.get("video_id")
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
    else:
        accounts[account_id]['active_session'] = session_id
    if session_id not in sessions:
        sessions[session_id] = {"images": {}, "hr": {}} # hr is heart rate
        accounts[account_id]['active_session'] = session_id
    if "images" not in sessions[session_id]:
        sessions[session_id]['images'] = {}
        sessions[session_id]['video_id'] = request_data["video_id"]
    sessions[session_id]['images'][epoch_time] = {"image_data": image_data}
    sessions[session_id]["video_id"] = request_data["video_id"]
    return jsonify({"success": True})

@app.route("/finish_session", methods=["POST"])
def finish_session():
    request_data = request.get_json()
    for account in accounts:
        if accounts[account].get("active_session", None) == request_data['session_id']:
            accounts[account]['active_session'] = None
            if "balance" not in accounts[account]:
                accounts[account]["balance"] = 0
            accounts[account]["balance"] += float(videos[sessions[request_data['session_id']]['video_id']]["price"])
            # iterate through all images. find closest heart rate to each image
            session = sessions[request_data['session_id']]
            hr_data = json.loads(open("hr_data.json").read())
            for image_time in session['images']:
                closest_hr = None
                closest_hr_time = None
                for hr in hr_data:
                    hr_time = float(hr)
                    if closest_hr is None or abs(image_time - hr_time) < abs(image_time - closest_hr_time):
                        closest_hr = float(hr_data[hr])
                        closest_hr_time = hr_time
                session['images'][image_time]['hr'] = closest_hr
            ml_output = post_processing(sessions[request_data['session_id']]['images'])
            img1 = ml_plotter(ml_output)
            img2 = plotter(hr_data)
            video_id = session['video_id']
            videos[video_id]["img1"] = img1
            videos[video_id]["img2"] = img2
            return jsonify({"success": True})
    return jsonify({"success": False})

if __name__ == "__main__":
    matplotlib.pyplot.switch_backend('Agg') 
    port = int(os.environ.get("PORT", 3000))
    app.run(port=port, debug=False)
    print("ASDASD")
    