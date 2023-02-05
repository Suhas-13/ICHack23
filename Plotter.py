import matplotlib.pyplot as plt
import seaborn as sns
import time
import random
import time
import cv2
from deepface import DeepFace
#face_analysis = DeepFace.analyze(img_path="hello.png")
cap = cv2.VideoCapture(0)
database_face_image = dict()
epoc_time=0 # read from frontend
from deepface import DeepFace

hrs={}

for i in range(1000):# the heart rate has to be calculated like 200 items at a time so in a for loop.
    time.sleep(0.01)
    hrs[str(round(time.time(),5))]=random.randint(70,80)

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

def plotter( hrs):# image and hrs are of the structure {time: image_data} and (time: hr_data}
    x=list(hrs.keys())
    y=list(hrs.values())
    sns.lineplot(x=x,y=y,color='red')
    plt.xlabel("Time Elapsed (ms)")
    plt.ylabel("Heart Beat (bpm)")
    plt.savefig("plot.png")
    plt.show()

def post_processing(database_fr):
    temp = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    count = 0
    database_fr2 = dict()
    for i in database_fr: # for epoch time in database_fr , it sets frame as the value pair
        frame = database_fr[i]
        try:
            face_analysis = DeepFace.analyze(img_path=frame, actions=["emotion", "dominant_emotion"])
        except ValueError:  # catches the error when the face cannot be detected
            continue
        d_emotion = face_analysis[0]['dominant_emotion']
        temp[d_emotion] += 1
        count += 1
        if count % 5 == 0:  # takes the average of 5 frames
            dominant_emotion = max(temp, key=lambda x: temp[x])
            database_fr2[i] = [database_fr[i], dominant_emotion]
            temp = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    return (database_fr2)

def ml_plotter(database_fr2):
    data=list(database_fr2.values())
    x=list(database_fr2.keys())
    x1=x2=x3=x4=x5=x6=x7=[0]*len(data)
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
    plt.savefig("plot2.png")
    plt.show()



i=0
while i<50:
    ret, frame = cap.read()
    if frame is None:
        break
    epoc_time=time.time()
    database_face_image[epoc_time]=frame
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    i=i+1



ml_plotter(post_processing(database_face_image))
hrs=average_to_150(hrs)
plotter(hrs)

cap.release()
cv2.destroyAllWindows()