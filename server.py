import functions
from fastapi import FastAPI




class TakenLoginError(Exception):
    """Ошибка занятого логина."""
    pass




server = FastAPI()

people = 0

login_list = {}



pattern = {
    "id": 0,
    "login": "",
    "password": ""
}



def new(lgn: str, psswrd: str):
    user = pattern.copy()
    user["id"] = people + 1
    people += 1
    while True:
        try:
            user["login"] = lgn
            for i in range(len(login_list)):
                if (login_list[i] == user["login"]):
                    raise TakenLoginError
            break
        except TakenLoginError as tree:
            print(f"\nОшибка! Подробнее: {tree}")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")
    while True:
        try:
            user["password"] = psswrd
            break
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")
    return user




@server.get("/")
def home():
    return "Шифр Скитала."