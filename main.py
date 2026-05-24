from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ipo_checker import check_spacex_ipo

app = FastAPI()
# prevent corsm blocking by chrome
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return check_spacex_ipo()