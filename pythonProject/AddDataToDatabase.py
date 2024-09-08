import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("ServiceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://realtimeattendance-cb0b4-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "0001":
        {
            "name": "Anujika Sasindi",
            "major": "CIS",
            "starting_year": 2021,
            "total_attendance": 6,
            "standing": "G",
            "year": 3,
            "last_attendance_time": "2024-09-01 00:12:56"
        },
    "0002":
        {
            "name": "Mark Zuckerburg",
            "major": "SE",
            "starting_year": 2019,
            "total_attendance": 25,
            "standing": "B",
            "year": 4,
            "last_attendance_time": "2024-09-01 00:12:56"
        },
    "0003":
        {
            "name": "Selena Gomez",
            "major": "ART",
            "starting_year": 2020,
            "total_attendance": 15,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2024-09-01 00:12:56"
        },
    "0004":
        {
            "name": "Elon Musk",
            "major": "DS",
            "starting_year": 2023,
            "total_attendance": 5,
            "standing": "G",
            "year": 1,
            "last_attendance_time": "2024-09-01 00:12:56"
        }
}

for key,value in data.items():
    ref.child(key).set(value)
