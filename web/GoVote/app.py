from flask import (
    Flask,
    render_template,
    flash,
    request,
    redirect,
    session,
    Response,
    jsonify,
)
from services.services import (
    get_nik,
    get_count,
    set_vote,
    hash,
    get_status,
    get_all,
    insert,
    delete,
    preprocess_image,
)
import base64
import cv2
import os

# Initialize flask app
app = Flask(__name__)
app.secret_key = "COMEGOVOTE"

UPLOAD_FOLDER = "static/img/temp"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Camera
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

        yield (b"--frame\r\n" b" Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


# Set Session
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = 600


@app.route("/camera")
def camera_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/capture_image")
def capture_image():
    # Read a single frame from the camera
    success, frame = camera.read()

    if success:
        # Encode the image to base64
        _, buffer = cv2.imencode(".jpg", frame)
        image_data = base64.b64encode(buffer).decode("utf-8")

        # Save the image to the upload folder
        image_filename = "captured_image.jpg"
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        cv2.imwrite(image_path, frame)
        
        label, distance = preprocess_image(image_path)
        if label is None :
            print(label)
            return jsonify({"image_data": image_data, "message": "Please make sure you are in place in proper lightning and your full face showing on the camera"})
        else:
            print(label) 
            print(distance)

            if session["nama_lengkap"] == label and distance < 20:
                return redirect("/vote")
            return jsonify({"image_data": image_data, "message": "Invalid face credential"})


@app.get("/")
def homepage():
    return render_template("public/homepage.html")


# Login
@app.get("/login")
def home():
    return render_template("public/index.html")


# Admin Login
@app.get("/login/admin")
def getloginadmin():
    return render_template("/admin/login_admin.html")


# Post for Login
@app.post("/login")
def postlogin():
    # Get data from Form
    nama_lengkap = request.form["nama_lengkap"].strip().title()
    nik = hash(request.form["nik"])
    nama_ibu_kandung = request.form["nama_ibu_kandung"].strip().title()

    # Get nik from SQL in services.py
    res = get_nik(nik)

    # Check
    if res and res[1] == nama_lengkap and res[2] == nama_ibu_kandung:
        session.clear()
        session["nik"] = nik
        session["nik_ori"] = request.form["nik"]
        session["nama_lengkap"] = nama_lengkap
        session["nama_ibu_kandung"] = nama_ibu_kandung
        return redirect("/profile")
    flash("Penduduk tidak ditemukan")
    return redirect("/login")


# Post for Login
@app.post("/login/admin")
def postloginadmin():
    # Get data from Form
    id = request.form["id"]
    username = request.form["username"].strip()
    password = request.form["password"].strip()

    # Check
    res = get_nik(id)
    if res and res[1] == username and res[2] == password:
        session.clear()
        session["admin"] = "ADMIN"
        return redirect("/admin")


@app.get("/admin")
def getadmin():
    data = get_all()
    if session.get("admin"):
        return render_template("admin/admin.html", data=data)
    return redirect("/login/admin")


@app.post("/admin")
def postadmin():
    nama_lengkap = request.form["nama_lengkap"].strip().title()
    nik = hash(request.form["nik"])
    nama_ibu_kandung = request.form["nama_ibu_kandung"].strip().title()
    insert(nik, nama_lengkap, nama_ibu_kandung)
    return redirect("/admin")


@app.post("/deletes/<string:nik>")
def deletes(nik):
    delete(nik)
    return redirect("/admin")


# Syarat dan Ketentuan
@app.get("/profile")
def getProfile():
    # Check session
    if get_status(session):
        return render_template("/user/profile.html")
    return redirect("/preview")


# Syarat dan Ketentuan
@app.get("/syarat")
def getsyarat():
    # Check session
    if get_status(session):
        return render_template("/user/syarat.html")
    return redirect("/preview")


# Face Recognition
@app.get("/verify")
def verif():
    if get_status(session):
        return render_template("/user/verify.html")
    return redirect("/preview")


# Coblos
@app.get("/vote")
def getcoblos():
    if get_status(session):
        return render_template("/user/vote.html")
    return redirect("/preview")


# Post for Coblos
@app.post("/vote")
def postcoblos():
    if get_status(session):
        vote = request.form["vote"]
        set_vote(int(vote), session["nik"])
    return redirect("/preview")


# Preview
@app.get("/preview")
def preview():
    res = get_count()
    count = sum(res)
    for x in range(len(res)):
        if res[x] != 0:
            res[x] = round(res[x] / count * 100, 1)
    return render_template("/user/preview.html", res=res)


# Logout
@app.get("/logout")
def logout():
    session.clear()
    return redirect("/login")


# Run the app when files execute
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
