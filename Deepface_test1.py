
import time
import cv2
from deepface import DeepFace
#face_analysis = DeepFace.analyze(img_path="hello.png")
cap = cv2.VideoCapture(0)
database_face_image = dict()
epoc_time=0 # read from frontend
# df = pandas.DataFrame(data=None, columns=["time", "emotion", "frame", "heartbeat"])
# while True:
#     ret, frame = cap.read()
#     if frame is None:
#         break
#     epoc_time=time.time()
#     #cv2.imshow("app", frame)
#     try:
#         face_analysis = DeepFace.analyze(img_path=frame,actions=["emotion","dominant_emotion"])
#     except ValueError : # catches the error when the face cannot be detected
#         continue
#     d_emotion = face_analysis[0]['dominant_emotion']
#     temp[d_emotion] += 1
#     count += 1
#     if count % 5 == 0: # takes the average of 5 frames
#         dominant_emotion = max(temp, key= lambda x: temp[x])
#         dom_emotions.append(dominant_emotion) # comment later
#         database_fr[epoc_time]=dominant_emotion
#         temp = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
#         print(database_fr) # remove later
#
#
#     print(face_analysis) # remove later
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

def Post_processing(database_fr):
    temp = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    count = 0
    database_fr2=dict()
    for i in database_fr:
      frame=database_fr[i]
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

print(Post_processing(database_face_image))

cap.release()
cv2.destroyAllWindows()