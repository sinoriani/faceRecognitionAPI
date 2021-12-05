import sqlite3
import json
con = sqlite3.connect('faces.db', check_same_thread=False)


def get_all_images(label):
    cur = con.cursor()
    
    cur.execute("SELECT b64 FROM data WHERE upper(name) = ?",(label.upper(),))
    result = cur.fetchall()
    res = []
    for r in result:
        res.append(r[0])
    return res