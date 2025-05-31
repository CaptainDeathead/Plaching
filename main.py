import flask
import smtplib, ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import DatabaseManager
from datetime import date
from time import time, sleep
from typing import Tuple

app = flask.Flask(__name__)

database_manager = DatabaseManager()
active_verifys = {}

port = 465  # For SSL
with open("gmail_password.txt", "r") as f:
    password = f.read()

context = ssl.create_default_context()

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
    phone = data.get('phone').strip()
    email = data.get('email').strip()
    date = data.get('date').strip()
    
    print(f"Received: {fname=}, {lname=}, {phone=}, {email=}, {date=}")

    if fname == "": return flask.jsonify({"status", "failure"}), 400
    elif lname == "": return flask.jsonify({"status", "failure"}), 400
    elif phone == "": return flask.jsonify({"status", "failure"}), 400
    elif email == "": return flask.jsonify({"status", "failure"}), 400
    elif date == "": return flask.jsonify({"status", "failure"}), 400

    parsed_date = parse_date(date)

    active_verifys[email] = {
        "fname": fname,
        "lname": lname,
        "phone": phone,
        "email": email,
        "date": parsed_date,
        "init_time": time()
    }

    with open("emails/verify.html", "r") as f:
        html = f.read().replace("EMAIL", email)
        send_email(email, "Verify wedding", html)
    
    return flask.jsonify({"status": "success"}), 200

@app.route('/verify')
def verify() -> str:
    email = flask.request.args.get('email')

    if email in active_verifys:
        return flask.render_template("verify_success.html")
    else:
        return flask.render_template("verify_fail.html")

@app.route('/register.js')
def register_js() -> str:
    return flask.send_from_directory('scripts', 'register.js')

@app.route('/verify_success.js')
def veify_success_js() -> str:
    return flask.send_from_directory('scripts', 'verify_success.js')

@app.route('/favicon.png')
def favicon() -> str:
    return flask.send_file("favicon.png")

if __name__ == "__main__":
    app.run('0.0.0.0', 5000)