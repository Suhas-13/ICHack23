# import numpy
import pandas
import time
import cv2
from deepface import DeepFace
#face_analysis = DeepFace.analyze(img_path="hello.png")
dom_emotions = []
cap = cv2.VideoCapture(0)
count = 0
temp = {'angry':0, 'disgust':0, 'fear':0, 'happy':0, 'sad':0, 'surprise':0, 'neutral':0}
database_fr=dict()
epoc_time=0 # read from frontend
# df = pandas.DataFrame(data=None, columns=["time", "emotion", "frame", "heartbeat"])
while True:
    ret, frame = cap.read()
    if frame is None:
        break
    epoc_time=time.time()
    #cv2.imshow("app", frame)
    try:
        face_analysis = DeepFace.analyze(img_path=frame,actions=["emotion","dominant_emotion"])
    except ValueError : # catches the error when the face cannot be detected
        continue
    d_emotion = face_analysis[0]['dominant_emotion']
    temp[d_emotion] += 1
    count += 1
    if count % 5 == 0: # takes the average of 5 frames
        dominant_emotion = max(temp, key= lambda x: temp[x])
        dom_emotions.append(dominant_emotion) # comment later
        database_fr[epoc_time]=dominant_emotion
        temp = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
        print(database_fr) # remove later


    print(face_analysis) # remove later
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(dom_emotions)