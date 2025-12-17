import functions
import datetime
import json
import scytale
from fastapi import FastAPI




server = FastAPI()
loaded_data = functions.data("load")
if loaded_data:
    usrlst, people = loaded_data
else:
    usrlst = {}
    people = 0




@server.on_event("startup")
async def startup_event():
    """Загружаем данные при запуске."""
    global usrlst, people
    loaded = functions.data("load")
    if loaded:
        usrlst, people = loaded
    print(f"Сервер запущен. Пользователей: {len(usrlst)}")




async def checkloginregistration(lgn: str):
    global usrlst
    try:
        if (not lgn):
            raise functions.EmptyLineError
        elif (not all(ord(c) < 128 for c in lgn)):
            raise functions.LatinAlphabetError
        for user in usrlst.values():
            if user.get("login") == lgn:
                raise functions.TakenLoginError
        return lgn
    except functions.EmptyLineError:
        return {"status": "error", "message": "Строка пуста!"}
    except functions.LatinAlphabetError:
        return {"status": "error", "message": "Логин должен содержать только латинские буквы!"}
    except functions.TakenLoginError:
        return {"status": "error", "message": "Логин уже занят!"}
    except Exception:
        return {"status": "error", "message": "Неизвестная ошибка!"}




async def checkpasswordregistration(psswrd: str):
    try:
        if len(psswrd) < 10:
            raise functions.NotEnoughSymbolsError
        if not all(ord(c) < 128 for c in psswrd):
            raise functions.LatinAlphabetError
        if not any(c.isdigit() for c in psswrd):
            raise ValueError("Нет цифры")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?~" for c in psswrd):
            raise ValueError("Нет ни одного специального символа!")
    except functions.NotEnoughSymbolsError:
        return {"status": "error", "message": "Пароль содержит менее 10 символов!"}
    except functions.LatinAlphabetError:
        return {"status": "error", "message": "Пароль должен содержать только латинские символы!"}
    except ValueError as execution:
        return {"status": "error", "message": str(execution)}




async def new(people: int, lgn: str, psswrd: str):
    body = {
        "id": people + 1,
        "login": lgn,
        "password": psswrd
    }
    user = {
        "id": people + 1,
        "login": lgn,
        "password": psswrd,
        "token": functions.takeall(functions.take(), body)
    }
    return user, people + 1




async def log(action: str, user: dict):
    entry = {
        "time": datetime.datetime.now().isoformat(),
        "action": action,
        "id": user.get("id", 0),
        "login": user.get("login", "unknown")
    }
    try:
        try:
            with open("log.json", "r", encoding="utf-8") as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = []
        
        logs.append(entry)
        
        with open("log.json", "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка при записи лога! Подробнее: {e}")




@server.get("/")
async def home():
    return "Шифр Скитала. Сулейманов Тимур Алиевич. 744-1. 2025-2026."




@server.post("/registration")
async def register(data: dict):
    if "login" not in data or "password" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    login = data["login"]
    password = data["password"]
    loginresult = await checkloginregistration(login)
    if isinstance(loginresult, dict):
        return loginresult
    passwordresult = await checkpasswordregistration(password)
    if isinstance(passwordresult, dict):
        return passwordresult
    global people, usrlst
    user, people = await new(people, login, password)
    usrlst[login] = user
    await log("registration", user)
    return {
        "status": "success",
        "message": "Регистрация успешна!",
        "user_id": user["id"],
        "login": user["login"],
        "token": user["token"]
    }




@server.post("/login")
async def login(data: dict):
    if "login" not in data or "password" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    login = data["login"]
    password = data["password"]
    user = None
    for u in usrlst.values():
        if u["login"] == login and u["password"] == password:
            user = u
            break
    if not user:
        return {"status": "error", "message": "Неверный логин или пароль!"}
    body = {
        "id": user["id"],
        "login": user["login"],
        "action": "login"
    }
    token = functions.take()
    signedtoken = functions.takeall(token, body)
    user["token"] = signedtoken
    await log("login", user)
    return {
        "status": "success",
        "message": "Авторизация успешна!",
        "user_id": user["id"],
        "login": user["login"],
        "token": signedtoken
    }




@server.post("/logout")
async def logout(data: dict):
    """Выход из аккаунта - удаление токена."""
    if "token" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    token = data["token"]
    user_found = None
    for user in usrlst.values():
        if user.get("token") == token:
            user_found = user
            break
    if not user_found:
        return {"status": "error", "message": "Токен не найден!"}
    if "token" in user_found:
        del user_found["token"]
    
    await log("logout", user_found)
    
    return {"status": "success", "message": "Вы вышли из системы!"}




@server.post("/encrypt")
async def encrypt(data: dict):
    """Шифрование текста методом Скитала."""
    if "text" not in data or "key" not in data or "token" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    text = data["text"]
    key = data["key"]
    token = data["token"]
    user = None
    for u in usrlst.values():
        if u.get("token") == token:
            user = u
            break
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    if key <= 0:
        return {"status": "error", "message": "Ключ должен быть больше 0!"}
    try:
        encrypted = await scytale.make(text, key)
        await log("encrypt", user)
        return {
            "status": "success",
            "message": "Текст зашифрован!",
            "encrypted_text": encrypted,
            "key_used": key
        }
    except Exception as e:
        return {"status": "error", "message": f"Ошибка шифрования: {str(e)}"}




@server.post("/decrypt")
async def decrypt(data: dict):
    """Дешифрование текста методом Скитала (повторное шифрование)."""
    if "text" not in data or "key" not in data or "token" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    text = data["text"]
    key = data["key"]
    token = data["token"]
    user = None
    for u in usrlst.values():
        if u.get("token") == token:
            user = u
            break
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    if key <= 0:
        return {"status": "error", "message": "Ключ должен быть больше 0!"}
    try:
        rows = await scytale.blue(text, key)
        decrypted = await scytale.make(text, key)
        await log("decrypt", user)
        return {
            "status": "success",
            "message": "Текст расшифрован!",
            "decrypted_text": decrypted,
            "key_used": key
        }
    except Exception as e:
        return {"status": "error", "message": f"Ошибка дешифрования: {str(e)}"}




@server.on_event("shutdown")
async def shutdown_event():
    """Сохраняем данные при остановке."""
    functions.data("save", usrlst, people)
    print(f"Сервер остановлен. Сохранено пользователей: {len(usrlst)}")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:server", host="0.0.0.0", port=8000, reload=True)