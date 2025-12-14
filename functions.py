import secrets
import hashlib
import time
import json
import datetime




"""

safe        —   функция безопасного ввода строк;
number      —   функция безопасного ввода чисел;
cpassword   —   функция создания и проверки пароля;
clogin      —   функция создания и проверки логина;
new         —   функция создания нового пользователя;
takeonly    —   функция подписи токена токеном;
taketime    —   функция подписи токена хэшем токена и времени;
takerequest —   функция подписи токена хэшем токена и тела запроса;
takeall     —   функция подписи токена хэшем токена, времени и тела запроса;
take        —   функция проверки логина и создания токена.

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
        except EmptyLineError as elementary:
            print(f"\nОшибка! Подробнее: {elementary}")
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
            print(f"\nОшибка! Подробнее: {amphora}")
        except EmptyLineError as elementary:
            print(f"\nОшибка! Подробнее: {elementary}")
        except NullValueError as willow:
            print(f"\nОшибка! Подробнее: {willow}")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")




def cpassword(Out: str):
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
            return Line
        except EmptyLineError as elementary:
            print(f"\nОшибка! Подробнее: {elementary}")
        except NotEnoughSymbolsError as nest:
            print(f"\nОшибка! Подробнее: {nest}")
        except LatinAlphabetError as grape:
            print(f"\nОшибка! Подробнее: {grape}")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")




def clogin(Out: str):
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
            print(f"\nОшибка! Подробнее: {elementary}")
        except LatinAlphabetError as grape:
            print(f"\nОшибка! Подробнее: {grape}")
        except Exception as execution:
            print(f"\nОшибка! Подробнее: {execution}")




def new(people: int, lgn: str, psswrd: str):
    user = {"id": people + 1,
            "login": lgn,
            "password": psswrd
    }
    return user, people + 1




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




def take(lgnlst: list[str], lgn: str, psswrd: str):
    token = ""
    if lgn in lgnlst:
        raise TakenLoginError
    token = secrets.token_hex(32)
    return token




def log(action: str, id: int, ):