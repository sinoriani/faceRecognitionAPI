import face_recognition
from os import listdir
from os.path import isfile, join
import numpy as np
import sqlite3
import json
import base64
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

    image = face_recognition.load_image_file(file)
    encoding = face_recognition.face_encodings(image)[0]

    with open(file, 'rb') as file:
        b64 = base64.b64encode(file.read()).decode('utf-8')

    cur = con.cursor()
    try:
        cur.execute("INSERT INTO data (name, b64, encoding) VALUES (?, ?, ?)",(label,b64, json.dumps(list(encoding))))
    except:
        cur.execute("CREATE TABLE data (id integer primary key AUTOINCREMENT, name varchar(100), b64 text, encoding text)")
        cur.execute("INSERT INTO data (name, b64, encoding) VALUES (?, ?, ?)",(label,b64,json.dumps(list(encoding))))

    con.commit()

    



def compare_image(image):
    global known_face_encodings
    global known_face_names

    refresh_data()

    unknown_image = face_recognition.load_image_file(image)
    try:
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
    except:
        return "Inconnu"
    matches = face_recognition.compare_faces(known_face_encodings, unknown_encoding)
    name = "Inconnu"

    # Or instead, use the known face with the smallest distance to the new face
    if matches:
        face_distances = face_recognition.face_distance(known_face_encodings, unknown_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            
    return f"{name} {str(round((1-min(face_distances))*100,2))+'%' if name != 'Inconnu' else ''}"