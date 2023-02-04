import numpy
import cv2
from deepface import DeepFace
#It is a hybrid face recognition framework wrapping model such as VGG-Face, Google FaceNet, OpenFace, Facebook DeepFace, DeepID, ArcFace, and Dlib
#face_analysis = DeepFace.analyze(img_path="hello.png")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if frame is None:
        break
    #cv2.imshow("app", frame)
    face_analysis = DeepFace.analyze(img_path=frame,actions=["emotion",])
    print(face_analysis)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#face_analysis[0]['dominant_emotion']  returns the dominant emotion
#face_analysis[0]['emotion'] dictionary of emotions
# add like a gui for like a smiley face depending on the dominant emotion in a frame
# each frame has a time associated with it and we do ( time, heart rate data, emotion to store the data)
cap.release()
cv2.destroyAllWindows()


#[[0.01, frame , emotion, heartrate],[0.02, frame , emotion]