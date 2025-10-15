import pyrebase
from hashlib import sha256
from secret import X

# Initialize the firebase connection
firebase = pyrebase.initialize_app(X[0])
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

# To encode a text
def encode(var):
    return sha256(var.encode("utf-8")).hexdigest()


# To register an account
def register(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user["idToken"])
        return "Verfication link has been sent to your Email"
    except:
        return "There's an error occured"


# Retrieve reset password
def forgot(email):
    try:
        auth.send_password_reset_email(email)
        return "Reset link has been sent to your Email"
    except:
        return "Email not Found"


# Login an account
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user = auth.refresh(user["refreshToken"])
        return (
            auth.get_account_info(user["idToken"])["users"][0]["emailVerified"],
            user["idToken"],
        )
    except:
        return "Email or Password is wrong"


# Add user to database
def set_user(email, password, name):
    data = {
        "email": email,
        "password": encode(password),
        "name": name,
    }
    db.child("users").child(encode(email)).update(data)


# Get user from database
def get_user(email):
    return db.child("users").child(encode(email)).get().val()


# Update user information
def update_user(email, data: dict):
    db.child("users").child(encode(email)).update(data)


# Add a new space
def set_space(
    space_name,
    type,
    phone,
    image_filename,
    link,
    lat,
    long,
    open_hours,
    pay,
    date,
    price,
):
    data = {
        "name": space_name,
        "type": type,
        "phone": phone,
        "image": image_filename,
        "long": long,
        "lat": lat,
        "link": link,
        "hours": open_hours,
        "pay": pay,
        "price": price,
        "status": "open"
    }

    db.child("spaces").child(space_name).update(data)


# Update slot for spaces
def update_slot(space_name, date, data):
    db.child("spaces").child(space_name).child("slot").child(date).update(data)


# Remove the slot
def remove_slot(space_name, date):
    db.child("spaces").child(space_name).child("slot").child(date).remove()


# Get spaces information
def get_space():
    spaces = db.child("spaces").get().val()
    return spaces


# Get a space based on name
def get_space_name(name):
    space = db.child("spaces").child(name).get().val()
    return space


# Get amount slot of a space
def get_space_slot(name, dates):
    return db.child("spaces").child(name).child("slot").child(dates).get().val()


# Remove a space
def delete_space(name):
    db.child("spaces").child(name).remove()


# Create a booking
def make_booking(session, now, dates, space, method, tipe):
    data = {
        "dates": dates,
        "space_name": space,
        "method": method,
        "qty": session["book"],
        "tipe": tipe,
        "status": "Belum Dibayar",
        "slots": session["slot"].strip(),
    }
    if session.get("to"):
        data["jam"] = session["to"] - session["from"]
        data["from"] = session["from"]
        data["to"] = session["to"]
        data["harga"] = int(session["harga"]) * int(session["to"] - session["from"])
    else:
        data["jam"] = "flat"
        data["harga"] = int(session["harga"]) * int(session["book"])
    db.child("users").child(encode(session["email"])).child("order").child(now).set(
        data
    )


# Get booking information
def get_booking(email):
    book = (
        db.child("users")
        .child(encode(email))
        .child("order")
        .order_by_key()
        .limit_to_last(20)
        .get()
        .val()
    )
    return book


# Change booking status
def change_booking_status(email, now, status="Dibatalkan"):
    db.child("users").child(encode(email)).child("order").child(now).update(
        {"status": status}
    )


def change_spaces_status(name, status="open"):
    db.child("spaces").child(name).update({"status": status})


def get_login_admin(email: str):
    mail = email.replace(".", "-")
    return db.child("admin").child(mail).get().val()


def set_salary(name, dates, total):
    db.child("spaces").child(name).child("salary").update({dates: int(total)})


def set_admin_user(email, password, space):
    db.child("admin").child(email).update({"password": password, "spaces": space})


def get_salary(name):
    return db.child("spaces").child(name).child("salary").get().val()


def add_salary(name, dates, total):
    salary = get_salary(name)
    if salary:
        total = salary["dates"] + int(total)
    set_salary(name, dates, total)


def get_list_space(name):
    return db.child("spaces").child(name).child("list-space").get().val()


def get_list_space_detail(name, lot):
    return db.child("spaces").child(name).child("list-space").child(lot).get().val()


def update_list_slot_space(name, slot, data):
    db.child("spaces").child(name).child("list-space").child(slot).update(data)


def add_list_slot_space(name, data):
    db.child("spaces").child(name).child("list-space").update(data)
