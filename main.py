import flask
import smtplib, ssl
import os
import shutil

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from PIL import Image
from base64 import b64decode, b64encode
from database import DatabaseManager
from datetime import date
from time import time, sleep
from typing import Tuple

app = flask.Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024 # 50MB

database_manager = DatabaseManager()
active_verifys = {}

port = 465  # For SSL
with open("gmail_password.txt", "r") as f:
    password = f.read()

context = ssl.create_default_context()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def send_email(to: str, subject:str, html: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = "plazmacoding@gmail.com"
    message["To"] = to

    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("plazmacoding@gmail.com", password)
        server.sendmail(
            "plazmacoding@gmail.com", to, message.as_string()
        )

def parse_date(raw_date: str) -> date | None:
    try:
        year, month, day = raw_date.strip('-') 
        return date(year, month, day)
    except:
        return None

def send_failed_email(email: str) -> None:
    with open("emails/verify_failed.html", "r") as f:
        send_email(email, "Verify failed", f.read())

def check_verifys() -> None:
    while 1:
        for phone in active_verifys:
            if time() - active_verifys[phone]["init_time"] > 60 * 60 * 24:
                send_failed_email(active_verifys[phone]["email"])
                del active_verifys[phone]

        sleep(60)

@app.route('/')
def index() -> str:
    return flask.render_template("index.html")

@app.route('/register', methods = ["GET"])
def register_get() -> str:
    return flask.render_template("register.html")

@app.route('/register', methods = ["POST"])
def register_post() -> str:
    data = flask.request.get_json()
    fname = data.get('fname').strip()
    lname = data.get('lname').strip()
    pfname = data.get('pfname').strip()
    phone = data.get('phone').strip()
    email = data.get('email').strip()
    date = data.get('date').strip()
    
    print(f"Received: {fname=}, {lname=}, {pfname=}, {phone=}, {email=}, {date=}")

    if fname == "": return flask.jsonify({"status": "failure"}), 400
    elif lname == "": return flask.jsonify({"status": "failure"}), 400
    elif pfname == "": return flask.jsonify({"status": "failure"}), 400
    elif phone == "": return flask.jsonify({"status": "failure"}), 400
    elif email == "": return flask.jsonify({"status": "failure"}), 400
    elif date == "": return flask.jsonify({"status": "failure"}), 400

    if database_manager.get_wedding(email) is not None:
        return flask.jsonify({"status": "conflict"}), 409

    active_verifys[email] = {
        "fname": fname,
        "lname": lname,
        "pfname": pfname,
        "phone": phone,
        "email": email,
        "date": date,
        "init_time": time()
    }

    with open("emails/verify.html", "r") as f:
        html = f.read().replace("EMAIL", email)
        send_email(email, "Verify wedding", html)
    
    return flask.jsonify({"status": "success"}), 200

@app.route('/register_next')
def register_next() -> str:
    return flask.render_template("register_next.html")

@app.route('/weddings/<wedding_id>')
def show_wedding(wedding_id: str) -> str:
    try:
        email = b64decode(wedding_id).decode()
    except Exception as e:
        return flask.render_template("wedding_not_found.html")

    wedding = database_manager.get_wedding(email)

    if wedding is None:
        return flask.render_template("wedding_not_found.html")
    
    return flask.render_template("wedding.html")

@app.route('/weddings/<wedding_id>/photos/<photo_index>')
def get_wedding_photo(wedding_id: str, photo_index: int) -> str:
    return flask.send_file(f"weddings/{wedding_id}/photos/{photo_index}.png")

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_thumbnail(img: Image, size: int = 150) -> Image:
    img.thumbnail((size, size), Image.LANCZOS)

    width, height = img.size
    min_side = min(width, height)

    left = (width - min_side) // 2
    top = (height - min_side) // 2
    right = left + min_side
    bottom = top + min_side

    img_cropped = img.crop((left, top, right, bottom))

    return img_cropped

@app.route('/weddings/<wedding_id>/photos/upload', methods=["POST"])
def upload_wedding_photo(wedding_id: str) -> any:
    if "file" not in flask.request.files:
        return "No file!", 400

    file = flask.request.files["file"]
    if file.filename == "":
        return "No selected file!", 400

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)

        if filename == "":
            return "Bad filename", 400

        img = Image.open(file)
        img = img.convert("RGBA")
        img.save(f"weddings/{wedding_id}/photos/{len(os.listdir(f'weddings/{wedding_id}/photos'))}.png", "PNG")

        # thumbnail
        generate_thumbnail(img, 150).save(f"weddings/{wedding_id}/thumbnails/{len(os.listdir(f'weddings/{wedding_id}/thumbnails'))}.png", "PNG")

        return f"File uploaded successfully: {filename} (converted to PNG)"

    return "Invalid file", 400

@app.route('/weddings/<wedding_id>/getInfo')
def get_info(wedding_id: str) -> str:
    email = b64decode(wedding_id).decode()
    wedding = database_manager.get_wedding(email)

    return flask.jsonify({
        'fname': wedding['fname'],
        'lname': wedding['lname'],
        'pfname': wedding['pfname'],
        'numPhotos': len(os.listdir(f"weddings/{wedding_id}/photos"))
    })

@app.route('/verify')
def verify() -> str:
    email = flask.request.args.get('email')

    if email in active_verifys:
        wedding_data = active_verifys[email]
        database_manager.add_wedding(wedding_data["fname"], wedding_data["lname"], wedding_data["pfname"], wedding_data["phone"], wedding_data["email"], wedding_data["date"])
        del active_verifys[email]

        wedding_id = b64encode(email.encode()).decode()
        if os.path.exists(f"weddings/{wedding_id}"):
            shutil.rmtree(f"weddings/{wedding_id}")

        os.makedirs(f"weddings/{wedding_id}/photos")
        os.makedirs(f"weddings/{wedding_id}/thumbnails")

        with open("emails/success.html", "r") as f:
            wedding_url = f"https://plaching.plazmasoftware.com/weddings/{wedding_id}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={wedding_url}"

            html = f.read().replace("WEDDING_URL", wedding_url).replace("WEDDING_QR_IMG", qr_url)
            send_email(email, "Wedding Created!", html)

        return flask.render_template("verify_success.html")
    else:
        return flask.render_template("verify_fail.html")

@app.route('/wedding.js')
def wedding_js() -> str:
    return flask.send_from_directory('scripts', 'wedding.js')

@app.route('/register.js')
def register_js() -> str:
    return flask.send_from_directory('scripts', 'register.js')

@app.route('/verify_success.js')
def veify_success_js() -> str:
    return flask.send_from_directory('scripts', 'verify_success.js')

@app.route("/stylesheet.css")
def stylesheet() -> str:
    return flask.send_from_directory("styles", "stylesheet.css")

@app.route('/favicon.png')
@app.route('/favicon.ico')
def favicon() -> str:
    return flask.send_file("favicon.png")

if __name__ == "__main__":
    app.run('0.0.0.0', 5000)
