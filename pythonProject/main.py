import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("ServiceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://realtimeattendance-cb0b4-default-rtdb.firebaseio.com/",
    'storageBucket':"realtimeattendance-cb0b4.appspot.com"
})

bucket = storage.bucket()
cap = cv2.VideoCapture(0)
cap.set(3, 450)
cap.set(4, 300)

imgBackground = cv2.imread('Resources/background3.png')

# IMPORTING MODE IMAGES TO A LIST
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

imgModeList[0] = cv2.resize(imgModeList[0], (297, 475))
imgModeList[1] = cv2.resize(imgModeList[1], (297, 475))
imgModeList[2] = cv2.resize(imgModeList[2], (297, 475))
imgModeList[3] = cv2.resize(imgModeList[3], (297, 475))

# LOAD THE ENCODING FILE
print("Loading Encoded File...")
file = open('EncodeFile.p','rb')
encodeListKnownWithIDs = pickle.load(file)
file.close()
encodeListKnown, studentIDs = encodeListKnownWithIDs
# print(studentIDs)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img,(0,0),None, 0.5, 0.5)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgS)
    encodeCurrentFace = face_recognition.face_encodings(imgS,faceCurrentFrame)

    img = cv2.resize(img, (450, 300))

    imgBackground[180:180+300, 72:72+450] = img
    imgBackground[50:50+475, 630:630+297] = imgModeList[modeType]

    if faceCurrentFrame:

        for encodeFace, faceLoc in zip(encodeCurrentFace, faceCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIDs[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 2, x2 * 2, y2 * 2, x1 * 2
                bbox = x1-20, 72+y1, x2-x1-20, y2-y1-10
                imgBackground = cvzone.cornerRect(imgBackground,bbox, rt=0)
                id = studentIDs[matchIndex]
                if counter == 0:
                    # cvzone.putTextRect(imgBackground,"Loading",(200, 340))
                    # cv2.imshow("Face Attendance", imgBackground)
                    # cv2.waitKey(1)
                    counter = 1
                    modeType = 1

            if counter != 0:

                if counter == 1:
                    # get the data
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)
                    # get the image from the storage
                    blob = bucket.get_blob(f'Images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                    # update data of attendance
                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                      "%Y-%m-%d %H:%M:%S")

                    secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                    # print(secondsElapsed)
                    if secondsElapsed > 30:
                        ref = db.reference(f'Students/{id}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[50:50 + 475, 630:630 + 297] = imgModeList[modeType]

                if modeType != 3:

                    if 10<counter<20:
                        modeType = 2

                    imgBackground[50:50 + 475, 630:630 + 297] = imgModeList[modeType]

                    if counter<=10:
                        cv2.putText(imgBackground,str(studentInfo['total_attendance']),(678,113),
                                    cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),1)
                        cv2.putText(imgBackground, str(id), (780, 402),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['major']), (780, 443),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['starting_year']), (860, 497),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['standing']), (675, 497),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['year']), (775, 497),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w, h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                        offset = (336-w)//2
                        cv2.putText(imgBackground, str(studentInfo['name']), (635+offset, 370),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.8, (50, 50, 50), 1)

                        imgBackground[130:130+216, 673:673+216] = imgStudent

                    counter += 1

                    if counter>20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[50:50 + 475, 630:630 + 297] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)