from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ipo_checker import check_spacex_ipo
import os
import smtplib
from email.mime.text import MIMEText

app = FastAPI()
# prevent corsm blocking by chrome
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
already_alerted = False

def send_email(subject, body):

    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    receiver = os.environ["EMAIL_RECEIVER"]

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
# @app.get("/")
# def root():
#     return {"message": "SpaceX IPO watcher backend running"}

# @app.get("/check-ipo")
# def check_ipo():
#     return {
#         "ticker": "SPCX",
#         "shares": 100,
#         "available": False,
#         "message": "SpaceX IPO not available yet"
#     }
@app.get("/check-ipo")
def check_ipo():

    global already_alerted

    result = check_spacex_ipo()

    if result["available"] and not already_alerted:

        send_email(
            "SpaceX IPO Alert",
            "Possible SpaceX IPO signal detected."
        )

        already_alerted = True

    return result