from flask import Flask, render_template, session, request, redirect, flash, url_for
from datetime import timedelta, datetime
from database import *
from pytz import timezone
import io
import pyqrcode
import re

# Initialize flask app
app = Flask(__name__)
app.secret_key = X[1]["secret"]
WIB = timezone("Asia/Jakarta")

# Set session to 2 weeks
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(weeks=2)

@app.template_filter('numerical_sort')
def numerical_sort(values):
    def key_func(item):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', item)]
    return sorted(values, key=key_func)

@app.get("/")
def home_get():
    api_key = X[0]["apiKey"]
    spaces = get_space()
    return render_template("index.html", api_key=api_key, spaces=spaces, nav="home")


@app.get("/admin/page")
def page_get():
    if session.get("roles") == "adminuser":
        dates = datetime.now().strftime("%Y%m%d")
        info = get_login_admin(session["remail"])
        space = get_space_name(info["spaces"])
        return render_template(
            "/admin/page.html", info=info, space=space, dates=dates, nav="admin"
        )
    return redirect("/login/admin")


@app.get("/admin/spaces")
def admin_court():
    if session.get("roles") == "superuser":
        spaces = get_space()
        return render_template("admin/spaces.html", spaces=spaces, nav="admin")
    return redirect("/login/admin")


@app.post("/admin/spaces")
def admin_court_post():
    name = request.form["name"]
    phone = request.form["phone"]
    location = request.form["location"]
    types = request.form["type"]
    lat = request.form["latitude"]
    long = request.form["longitude"]
    hours = request.form["hours"]
    price = request.form['price']
    pay = request.form["pay"]
    image = request.files["image"]
    hiddeninfo = request.form["info"]
    filename = name + ".png"
    if hiddeninfo == "edit":
        date = datetime.now().astimezone(WIB) + timedelta(days=1)
    else:
        date = datetime.now().astimezone(WIB)
    if image:
        storage.child("/spaces/" + filename).put(image)
        
    image_url = storage.child("/spaces/" + filename).get_url(None)
    set_space(
        name,
        types,
        phone,
        image_url,
        location,
        lat,
        long,
        hours,
        pay,
        date,
        price
    )
    return redirect("/admin/spaces")


@app.get("/admin/spaces/<name>")
def admin_spaces_get(name):
    space = get_space_name(name)
    return render_template("/admin/editspace.html", space=space, nav="admin")


@app.get("/spaces")
def courts_get():
    spaces = get_space()
    return render_template("/spaces/spaces.html", spaces=spaces, nav="spaces")


@app.get("/spaces/<name>")
def spaces_get(name):
    space = get_space_name(name)
    return render_template(
        "/spaces/viewspace.html", space=space, nav="spaces"
    )

@app.get("/booking/<name>")
def booking_get(name):
    if session.get("token"):
        space = get_space_name(name)
        slot_info = get_list_space(name)
        today = datetime.now().astimezone(WIB).strftime("%Y%m%d")
        today_name = datetime.now().astimezone(WIB).strftime("%d %B %Y")
        slot_space = get_space_slot(name, today)
        hasil = {}
        if slot_info:
            for key, val in slot_info.items():
                if val['lantai'] not in hasil:
                    hasil[val['lantai']] = []
                hasil[val['lantai']].append(key)
        return render_template("/booking/booking.html", today=today, today_name=today_name, space=space, slot_space=slot_space, slot_info=slot_info, slot=hasil)
    return redirect("/spaces")


@app.post("/booking/<name>")
def booking_post(name):
    session["slot"] = request.form["slots"].strip()
    session["book"] = request.form["books"]
    if request.form.get('fromPicker'):
        session["to"] = int(request.form["toPicker"])
        session["from"] = int(request.form["fromPicker"])
    return redirect("/payment/"+name)


@app.get("/profile")
def profile_get():
    data = get_user(session["email"])
    booking = get_booking(session["email"])
    if booking:
        booking = dict(reversed(dict(booking).items()))
        for key, val in booking.items():
            before = datetime.strptime(val["dates"], "%Y%m%d").date()
            after = datetime.now().date()
            if before < after:
                change_booking_status(session["email"], key)
        booking = dict(reversed(dict(get_booking(session["email"])).items()))
        for key, val in booking.items():
            space = val["space_name"]
            slots = val["slots"] #1A
            booking[key]["details"] = {}
            if val['jam'] != "flat":
                res = get_list_space_detail(space, slots)
                booking[key]["details"][slots] = res
            else:
                slt = slots.split(",")
                if len(slt) > 1:
                    for y in slt:
                        res = get_list_space_detail(space, y.strip())
                        booking[key]["details"][y.strip()] = dict(res)
                else:
                    res = get_list_space_detail(space, slots)
                    booking[key]["details"][slots] = res

            times = datetime.strptime(val["dates"], "%Y%m%d").date()
            booking[key]["name_date"] = times.strftime("%d %B %Y")
    return render_template("profile.html", data=data, booking=booking, nav="profile")


@app.post("/profile")
def profile_post():
    name = request.form["nameInput"]
    data = {"name": name}
    update_user(session["email"], data)
    return redirect("/profile")


@app.get("/login")
def login_get():
    if session.get("token"):
        return redirect("/profile")
    return render_template("/login/login.html", nav="login")


@app.get("/forgot")
def forgot_get():
    return render_template("/login/forgot.html")


@app.post("/forgot")
def forgot_post():
    email = request.form["email"]
    res = forgot(email)
    flash(res)
    return redirect("/forgot")


@app.post("/login")
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    log_in = login(email, password)
    if type(log_in) == str:
        flash(log_in)
    elif not log_in[0]:
        flash("Please Verify Your Account by click the link from Email")
    else:
        session["token"] = log_in[1]
        session["email"] = email
        return redirect("/")
    return redirect("/login")


@app.get("/login/admin")
def login_admin_get():
    return render_template("admin/login.html")


@app.post("/login/admin")
def login_admin_post():
    email = request.form["email"]
    password = request.form["password"]
    acc = X[1]
    if acc["email"] == email and acc["password"] == password:
        session["roles"] = "superuser"
        return redirect("/admin/spaces")
    info = get_login_admin(email)
    if info and info["password"] == encode(password):
        session["roles"] = "adminuser"
        session["remail"] = email
        return redirect("/admin/page")
    flash("Email atau Password Salah")
    return redirect("/login/admin")


@app.get("/register")
def register_get():
    return render_template("/login/register.html", nav="login")


@app.post("/register")
def register_post():
    email = request.form["email"]
    name = request.form["name"]
    password = request.form["password"]

    if get_user(email):
        flash("Email already taken")
        return redirect("/register")
    else:
        message = register(email, password)
        set_user(email, password, name)
        flash(message)
        return redirect("/login")


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.get("/QRIS/<name>")
def QRIS(name):
    return render_template("QRIS.html", name=name)


@app.get("/admin/spaces/delete/<name>")
def delete_spaces_get(name):
    delete_space(name)
    return redirect("/admin/spaces")


@app.get("/cancel/<space>/<book>")
def cancel(space, book):
    cancelation(space, book)
    return redirect("/profile")


@app.get("/paid/<book>")
def paid(book):
    qr_io = io.BytesIO()
    qr = pyqrcode.create(encode(session["email"])+"+"+book)
    qr.png(qr_io, scale=5)
    storage.child("/QR/"+session['email']+book+".png").put(qr_io.getvalue())
    qr_url = storage.child("/QR/"+session['email']+book+".png").get_url(None)
    change_booking_status(session["email"], book, "Sudah Dibayar")
    db.child("users").child(encode(session["email"])).child("order").child(book).update({'image': qr_url})
    return redirect(url_for("QRIS", name=book))


@app.get("/change/<name>/<status>")
def change(name, status):
    change_spaces_status(name, status)
    return redirect("/admin/page")


@app.get("/arrive/<book>")
def arrive(book):
    change_booking_status(session["email"], book, "Pesanan Selesai")
    return redirect("/profile")


@app.post("/setowner/<space>")
def set_owner(space):
    owner = request.form["owner" + space]
    email = request.form.get("mails" + space)
    owners = owner.replace(".", "-")
    emails = email.replace(".", "-")
    set_admin_user(emails, encode("Password12"), space)
    db.child("spaces").child(space).update({"owner": email})
    db.child("admin").child(owners).remove()
    return redirect("/admin/spaces")

@app.get("/admin/slot/<space>")
def manage_slot_get(space):
    spaces = get_list_space(space)
    return render_template("/admin/slot.html", spaces=spaces, name=space, nav="admin")

@app.post("/admin/slot/<space>")
def manage_slot_post(space):
    if session.get('roles'):
        kode = request.form["kode"]
        startno = int(request.form["nomorawal"])
        endno = int(request.form["nomorakhir"])
        lt = request.form["lantai"]
        comm = request.form["comment"]
        isi = {
            "comment": comm,
            "lantai": lt
        }
        
        space_info = get_space_name(space)
        tdy = (datetime.now().astimezone(WIB)).strftime("%Y%m%d")
        start_time, end_time = space_info['hours'].split(" - ")
        start_hour = int(start_time[:2])
        end_hour = int(end_time[:2])

        for x in range(startno, endno+1):
            datas = {kode+str(x): isi}

            if space_info['pay'] == 'perjam':
                data = {kode+str(x): {}}
                for time in range(start_hour, end_hour+1):
                    data[kode+str(x)][time] = "none"
                data[kode+str(x)]["full"] = "no"

            elif space_info['pay'] == 'flat':
                data = {kode+str(x): "none"}

            update_slot(space, tdy, data)
            add_list_slot_space(space, datas)
        
        return redirect("/admin/slot/"+space)
    return redirect("/login/admin")

@app.post("/admin/slot/<space>/<slot>")
def edit_slot_list(space, slot):
    comm = request.form["comment"+slot]
    lt = request.form["lantai"+slot]
    data = {
        "comment": comm,
        "lantai": lt
    }
    update_list_slot_space(space, slot, data)
    return redirect("/admin/slot/"+space)

@app.get("/admin/slot/<space>/<slot>")
def delete_slot_list(space, slot):
    db.child("spaces").child(space).child("list-space").child(slot).remove()
    return redirect("/admin/slot/"+space)

@app.get("/payment/<name>")
def get_payment(name):
    space = get_space_name(name)
    session['harga'] = int(session["book"]) * int(space["price"])
    return render_template("/booking/payment.html", space=space)

@app.post("/payment/<tipe>/<name>")
def post_payment(tipe, name):
    method = request.form["payment"]
    now = int(datetime.now().astimezone(WIB).timestamp())
    today = datetime.now().astimezone(WIB).strftime("%Y%m%d")
    make_booking(session, now, today, name, method, tipe)
    if session.get('to'):
        for x in range(session['from'], session['to']+1):
            db.child("spaces").child(name).child("slot").child(today).child(session['slot']).update({x: session['email']})
    else:
        slt = session['slot'].split(",")
        for x in slt:
            update_slot(name, today, {x.strip(): session['email']})
    session.pop("to", None)
    session.pop("from", None)
    session.pop("book")
    session.pop("slot")
    session.pop("harga")
    return redirect("/QRIS/"+name)

@app.get("/admin/change/<email>")
def get_change_pass(email):
    if session.get('roles') == "adminuser":
        return render_template("/admin/forgot.html", email=email)
    return redirect("/login/admin")

@app.post("/admin/change/<email>")
def post_change_pass(email):
    if session.get('roles') == "adminuser":
        oldpw = request.form["oldpw"]
        newpw = request.form["newpw"]
        conpw = request.form["conpw"]
        emails = email.replace(".", "-")
        pw = db.child("admin").child(emails).get().val()
        if pw["password"] == encode(oldpw) and newpw == conpw:
            db.child("admin").child(emails).update({"password": encode(newpw)})
        else:
            flash("Password didn't matched")
        return redirect("/admin/page")
    return redirect("/login/admin")


def cancelation(space, book):
    booking = db.child("users").child(encode(session['email'])).child("order").child(book).get().val()
    if booking["status"] == "Belum Dibayar":
        change_booking_status(session["email"], book)
        if booking.get('from'):
            for x in range(booking['from'], booking['to']+1):
                db.child("spaces").child(space).child("slot").child(booking['dates']).child(booking['slots']).update({x: "none"})
        else:
            if int(booking['qty']) > 1:
                slt = booking['slots'].split(",")
                for x in slt:
                    db.child("spaces").child(space).child("slot").child(booking['dates']).update({x.strip(): "none"})
            else:
                db.child("spaces").child(space).child("slot").child(booking['dates']).update({booking['slots']: "none"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
