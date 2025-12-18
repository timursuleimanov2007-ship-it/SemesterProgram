import secrets
import hashlib
import time
import json
import datetime
import requests
import os




"""

safe        —   функция безопасного ввода строк;
number      —   функция безопасного ввода чисел;
makepassword—   функция создания и проверки пароля;
makelogin   —   функция создания и проверки логина;
new         —   функция создания нового пользователя;
takeonly    —   функция подписи токена токеном;
taketime    —   функция подписи токена хэшем токена и времени;
takerequest —   функция подписи токена хэшем токена и тела запроса;
takeall     —   функция подписи токена хэшем токена, времени и тела запроса;
take        —   функция создания токена;
data        —   функция работы с данными пользователей;
loadusertexts — функция загрузки текстов пользователя;
saveusertexts — функция сохранения текстов пользователя;
loaduserhistory — функция загрузки истории пользователя;
saveuserhistory — функция сохранения истории пользователя.

"""




class EmptyLineError(Exception):
    """Ошибка пустой строки."""
    pass

class NotEnoughSymbolsError(Exception):
    """Ошибка недостаточного количества символов."""
    pass

class NullValueError(Exception):
    """Ошибка нулевого значения."""
    pass

class LatinAlphabetError(Exception):
    """Ошибка нелатинских символов."""
    pass

class TakenLoginError(Exception):
    """Ошибка занятого логина."""
    pass




def safe(Out: str):
    Line = ""
    while True:
        try:
            Line = input(Out)
            if (not Line):
                raise EmptyLineError
            return Line
        except EmptyLineError:
            print(f"\nОшибка! Подробнее: Строка не может быть пустой!")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")




def number(Out: str):
    Number = 0
    while True:
        try:
            Line = input(Out)
            if (not Line):
                raise EmptyLineError
            Number = int(Line)
            if (Number == 0):
                raise NullValueError
            return Number
        except ValueError as amphora:
            print(f"\nОшибка! Подробнее: Неверное значение!")
        except EmptyLineError:
            print(f"\nОшибка! Подробнее: Строка не может быть пустой!")
        except NullValueError:
            print(f"\nОшибка! Подробнее: Значение не может быть нулём!")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")




def makepassword(Out: str):
    Line = ""
    while True:
        try:
            Line = input(Out)
            if (not Line):
                raise EmptyLineError
            elif (len(Line) < 10):
                raise NotEnoughSymbolsError
            elif (not all(ord(c) < 128 for c in Line)):
                raise LatinAlphabetError
            elif (not any(c.isdigit() for c in Line)):
                raise ValueError("No numbers found. Need at least one.")
            elif (not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?~" for c in Line)):
                raise ValueError("No special characters found. Need at least one.")
            return Line
        except EmptyLineError:
            print(f"\nОшибка! Подробнее: Строка не может быть пустой!")
        except NotEnoughSymbolsError:
            print(f"\nОшибка! Подробнее: Недостаточно символов!")
        except LatinAlphabetError:
            print(f"\nОшибка! Подробнее: Только латинские буквы!")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")




def makelogin(Out: str):
    Line = ""
    while True:
        try:
            Line = input(Out)
            if (not Line):
                raise EmptyLineError
            elif (not all(ord(c) < 128 for c in Line)):
                raise LatinAlphabetError
            return Line
        except EmptyLineError as elementary:
            print(f"\nОшибка! Подробнее: Строка не может быть пустой!")
        except LatinAlphabetError:
            print(f"\nОшибка! Подробнее: Только латинские буквы!")
        except TakenLoginError:
            print(f"\nОшибка! Подробнее: Логин занят!")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")




            
def takeonly(token: str):
    return token




def taketime(token: str):
    unixtime = str(int(time.time()))
    final = token + unixtime
    return hashlib.sha256(final.encode()).hexdigest()




def takerequest(token: str, body: dict):
    head = json.dumps(body, sort_keys = True)
    final = token + head
    return hashlib.sha256(final.encode()).hexdigest()




def takeall(token: str, body: dict):
    unixtime = str(int(time.time()))
    head = json.dumps(body, sort_keys = True)
    final = token + unixtime + head
    return hashlib.sha256(final.encode()).hexdigest()




def take():
    token = ""
    token = secrets.token_hex(32)
    return token




def data(action: str, current_usrlst=None, current_people=0):
    filename = "server_data.json"
    if action == "save":
        save_data = {
            "users": current_usrlst if current_usrlst is not None else {},
            "people": current_people
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        print(f"Сохранено {len(current_usrlst) if current_usrlst else 0} пользователей")
        return True
    elif action == "load":
        try:
            with open(filename, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            loaded_users = loaded.get("users", {})
            loaded_people = loaded.get("people", len(loaded_users))
            print(f"Загружено {len(loaded_users)} пользователей")
            return loaded_users, loaded_people
        except FileNotFoundError:
            print("Файл данных не найден, начинаем с чистого листа")
            return {}, 0
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return {}, 0
    return None




def loadusertexts(user_id: int):
    filename = f"texts_{user_id}.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            texts = json.load(f)
        return texts
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Ошибка загрузки текстов! Подробнее: {e}")
        return []




def saveusertexts(user_id: int, texts: list):
    filename = f"texts_{user_id}.json"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(texts, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения текстов! Подробнее: {e}")
        return False




def loaduserhistory(user_id: int):
    filename = f"history_{user_id}.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            history = json.load(f)
        return history
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Ошибка загрузки истории! Подробнее: {e}")
        return []




def saveuserhistory(user_id: int, history: list):
    filename = f"history_{user_id}.json"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения истории! Подробнее: {e}")
        return False