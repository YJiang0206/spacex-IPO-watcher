from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ipo_checker import check_spacex_ipo
import resend
import os

app = FastAPI()
# prevent corsm blocking by chrome
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
already_alerted = False

resend.api_key = os.environ["RESEND_API_KEY"]
def send_email(subject, body):

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "yuanjiejiang92@gmail.com",
        "subject": subject,
        "html": body
    })

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

    #if result["available"] and not already_alerted:


    send_email(
        "SpaceX IPO Alert",
        "TEST FROM RENDER"
    )

        #already_alerted = True

    return result