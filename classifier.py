import face_recognition
from os import listdir
from os.path import isfile, join
import numpy as np
import sqlite3
import json
con = sqlite3.connect('faces.db', check_same_thread=False)


known_face_encodings = []
known_face_names = []

def refresh_data():
    cur = con.cursor()
    global known_face_encodings
    global known_face_names
    
    cur.execute("CREATE TABLE IF NOT EXISTS data (id integer primary key AUTOINCREMENT, name varchar(100), encoding text)")

    cur.execute('SELECT name, encoding FROM data')
    res = cur.fetchall()
    
    known_face_encodings = []
    known_face_names = []
    for label, encoding in res:
        known_face_encodings.append(json.loads(encoding))
        known_face_names.append(label)



def update_listed_files(file, label):
    # onlyfiles = [f for f in listdir('images/') if isfile(join('images/', f))]

    image = face_recognition.load_image_file(file)
    encoding = face_recognition.face_encodings(image)[0]
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO data (name, encoding) VALUES (?, ?)",(label,json.dumps(list(encoding))))
    except:
        cur.execute("CREATE TABLE data (id integer primary key AUTOINCREMENT, name varchar(100), encoding text)")
        cur.execute("INSERT INTO data (name, encoding) VALUES (?, ?)",(label,json.dumps(list(encoding))))

    con.commit()

    



def compare_image(image):
    global known_face_encodings
    global known_face_names

    refresh_data()

    unknown_image = face_recognition.load_image_file(image)
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    matches = face_recognition.compare_faces(known_face_encodings, unknown_encoding)
    name = "Unknown"

    # Or instead, use the known face with the smallest distance to the new face
    if matches:
        face_distances = face_recognition.face_distance(known_face_encodings, unknown_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
    print(name)
    return name