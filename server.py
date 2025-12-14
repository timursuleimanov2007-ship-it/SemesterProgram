import functions
from fastapi import FastAPI




server = FastAPI()

people = 0

login_list = {}




@server.get("/")
def home():
    return "Шифр Скитала."