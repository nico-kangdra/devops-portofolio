from services.db import db_con
from hashlib import sha256
import numpy as np
import cv2
import matplotlib.pyplot as plt


def hash(txt):
    return sha256(txt.encode("utf-8")).hexdigest()


def execute(sql):
    conn = db_con()
    curs = conn.cursor()
    curs.execute(sql)
    return {"con": conn, "cur": curs}


def close(item):
    for x in item.values():
        x.close()


def get_nik(nik):
    item = execute(f"SELECT * FROM users WHERE nik = '{nik}'")
    res = item["cur"].fetchone()
    close(item)
    return res


def get_count():
    item = [
        execute(f"SELECT COUNT(*) FROM users WHERE vote = 1"),
        execute(f"SELECT COUNT(*) FROM users WHERE vote = 2"),
        execute(f"SELECT COUNT(*) FROM users WHERE vote = 3"),
    ]
    res = [
        item[0]["cur"].fetchone()[0],
        item[1]["cur"].fetchone()[0],
        item[2]["cur"].fetchone()[0],
    ]
    for x in item:
        close(x)
    return res


def set_vote(x, nik):
    item = execute(f"UPDATE users SET vote = {x} WHERE nik = '{nik}'")
    item["con"].commit()
    close(item)


def get_all():
    item = execute("SELECT nik, nama_lengkap, nama_ibu_kandung FROM users")
    res = item["cur"].fetchall()
    close(item)
    return res


def insert(x, y, z):
    item = execute(
        f"INSERT INTO users (nik, nama_lengkap, nama_ibu_kandung) VALUES ('{x}','{y}','{z}')"
    )
    item["con"].commit()
    close(item)


def delete(x):
    item = execute(f"DELETE FROM users WHERE nik = '{x}'")
    item["con"].commit()
    close(item)


def get_status(session):
    if session.get("nik"):
        item = execute(f"SELECT vote FROM users WHERE nik = '{session['nik']}'")
        res = item["cur"].fetchone()[0]
        close(item)
        if res is None:
            return True
    return False


# function to detect face using OpenCV
def detect_face(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier("static\model\haarcascade_frontalface_alt.xml")

    # let's detect multiscale (some images may be closer to camera than others) images
    # result is a list of faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=3)

    # if no faces are detected then return original img
    if len(faces) == 0:
        return None

    # under the assumption that there will be only one face,
    # extract the face area
    (x, y, w, h) = faces[0]

    # return only the face part of the image
    return gray[y : y + w, x : x + h]


def preprocess_image(image_path):
    subjects = ["", "Juan Situmorang", "Dozer Napitupulu", "Nico Kangdra"]

    # Load the image from the provided path
    img = cv2.imread(image_path)
    print(img.shape)

    # Convert image to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Detect face from the image
    face = detect_face(img)
    if face is not None:
        # Load the face recognition model
        loaded_model = cv2.face.LBPHFaceRecognizer_create()
        loaded_model.read("static\model\modelx_basewaug.xml")

        # Predict the image using our face recognizer
        label = loaded_model.predict(face)

        # Get the name of the respective label returned by the face recognizer
        label_text = subjects[label[0]]
        distance_alike = label[1]

        return label_text, distance_alike
    else:
        return None, None 
