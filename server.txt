import functions
import datetime
import json
import scytale
from fastapi import FastAPI




server = FastAPI()
loadeddata = functions.data("load")
if loadeddata:
    usrlst, people = loadeddata
else:
    usrlst = {}
    people = 0




@server.on_event("startup")
async def startup_event():
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




async def log(userid: int, login: str, action: str, details: dict = None):
    entry = {
        "time": datetime.datetime.now().isoformat(),
        "action": action,
        "userid": userid,
        "login": login,
        "details": details if details else {}
    }
    try:
        history = functions.loaduserhistory(userid)
        history.append(entry)
        functions.saveuserhistory(userid, history)
    except Exception as e:
        print(f"Ошибка при записи лога! Подробнее: {e}")




async def getuserbytoken(token: str):
    for u in usrlst.values():
        if u.get("token") == token:
            return u
    return None




async def updatetoken(user: dict):
    body = {
        "id": user["id"],
        "login": user["login"],
        "action": "token_update"
    }
    newtoken = functions.take()
    signedtoken = functions.takeall(newtoken, body)
    user["token"] = signedtoken
    return signedtoken




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
    await log(user["id"], user["login"], "registration")
    return {
        "status": "success",
        "message": "Регистрация успешна!",
        "userid": user["id"],
        "login": user["login"],
        "token": user["token"]
    }




@server.get("/history")
async def gethistory(token: str):
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    history = functions.loaduserhistory(user["id"])
    await log(user["id"], user["login"], "gethistory")
    return {
        "status": "success",
        "userid": user["id"],
        "history": history
    }




@server.delete("/history")
async def deletehistory(token: str):
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    functions.saveuserhistory(user["id"], [])
    await log(user["id"], user["login"], "deletehistory")
    return {
        "status": "success",
        "message": "История очищена!"
    }




@server.patch("/password")
async def changepassword(data: dict):
    if "token" not in data or "newpassword" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    token = data["token"]
    newpassword = data["newpassword"]
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    passwordresult = await checkpasswordregistration(newpassword)
    if isinstance(passwordresult, dict):
        return passwordresult
    user["password"] = newpassword
    newtoken = await updatetoken(user)
    await log(user["id"], user["login"], "changepassword", {"passwordchanged": True})
    return {
        "status": "success",
        "message": "Пароль и токен обновлены!",
        "newtoken": newtoken
    }




@server.post("/texts")
async def addtext(data: dict):
    if "token" not in data or "text" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    token = data["token"]
    text = data["text"]
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    texts = functions.loadusertexts(user["id"])
    textid = len(texts) + 1
    textentry = {
        "id": textid,
        "text": text,
        "createdat": datetime.datetime.now().isoformat(),
        "updatedat": datetime.datetime.now().isoformat()
    }
    texts.append(textentry)
    functions.saveusertexts(user["id"], texts)
    await log(user["id"], user["login"], "addtext", {"textid": textid})
    return {
        "status": "success",
        "message": "Текст добавлен!",
        "textid": textid
    }




@server.patch("/texts/{textid}")
async def updatetext(textid: int, data: dict):
    if "token" not in data or "newtext" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    token = data["token"]
    newtext = data["newtext"]
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    texts = functions.loadusertexts(user["id"])
    found = False
    for textentry in texts:
        if textentry["id"] == textid:
            textentry["text"] = newtext
            textentry["updatedat"] = datetime.datetime.now().isoformat()
            found = True
            break
    if not found:
        return {"status": "error", "message": "Текст не найден!"}
    functions.saveusertexts(user["id"], texts)
    await log(user["id"], user["login"], "updatetext", {"textid": textid})
    return {
        "status": "success",
        "message": "Текст обновлён!"
    }




@server.delete("/texts/{textid}")
async def deletetext(textid: int, token: str):
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    texts = functions.loadusertexts(user["id"])
    newtexts = [t for t in texts if t["id"] != textid]
    if len(newtexts) == len(texts):
        return {"status": "error", "message": "Текст не найден!"}
    functions.saveusertexts(user["id"], newtexts)
    await log(user["id"], user["login"], "deletetext", {"textid": textid})
    return {
        "status": "success",
        "message": "Текст удалён!"
    }




@server.get("/texts/{textid}")
async def gettext(textid: int, token: str):
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    texts = functions.loadusertexts(user["id"])
    for textentry in texts:
        if textentry["id"] == textid:
            await log(user["id"], user["login"], "gettext", {"textid": textid})
            return {
                "status": "success",
                "text": textentry
            }
    return {"status": "error", "message": "Текст не найден!"}




@server.get("/texts")
async def getalltexts(token: str):
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    texts = functions.loadusertexts(user["id"])
    await log(user["id"], user["login"], "getalltexts")
    return {
        "status": "success",
        "texts": texts
    }




@server.post("/encrypt")
async def encrypttext(data: dict):
    if "token" not in data or "textid" not in data or "key" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    token = data["token"]
    textid = data["textid"]
    key = data["key"]
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    if key <= 0:
        return {"status": "error", "message": "Ключ должен быть больше 0!"}
    texts = functions.loadusertexts(user["id"])
    text = None
    for textentry in texts:
        if textentry["id"] == textid:
            text = textentry["text"]
            break
    if not text:
        return {"status": "error", "message": "Текст не найден!"}
    try:
        encrypted = await scytale.make(text, key)
        await log(user["id"], user["login"], "encrypt", {"textid": textid, "keyused": key})
        return {
            "status": "success",
            "message": "Текст зашифрован!",
            "encryptedtext": encrypted,
            "keyused": key,
            "originaltext": text,
            "textid": textid
        }
    except Exception as e:
        return {"status": "error", "message": f"Ошибка шифрования: {str(e)}"}




@server.post("/decrypt")
async def decrypttext(data: dict):
    if "token" not in data or "textid" not in data or "key" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    token = data["token"]
    textid = data["textid"]
    key = data["key"]
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Недействительный токен!"}
    if key <= 0:
        return {"status": "error", "message": "Ключ должен быть больше 0!"}
    texts = functions.loadusertexts(user["id"])
    text = None
    for textentry in texts:
        if textentry["id"] == textid:
            text = textentry["text"]
            break
    if not text:
        return {"status": "error", "message": "Текст не найден!"}
    try:
        rows = await scytale.blue(text, key)
        decrypted = await scytale.make(text, rows)
        await log(user["id"], user["login"], "decrypt", {"textid": textid, "keyused": key})
        return {
            "status": "success",
            "message": "Текст расшифрован!",
            "decryptedtext": decrypted,
            "keyused": key,
            "originaltext": text,
            "textid": textid
        }
    except Exception as e:
        return {"status": "error", "message": f"Ошибка дешифрования: {str(e)}"}




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
    await log(user["id"], user["login"], "login")
    return {
        "status": "success",
        "message": "Авторизация успешна!",
        "userid": user["id"],
        "login": user["login"],
        "token": signedtoken
    }




@server.post("/logout")
async def logout(data: dict):
    if "token" not in data:
        return {"status": "error", "message": "Пакет повреждён!"}
    token = data["token"]
    user = await getuserbytoken(token)
    if not user:
        return {"status": "error", "message": "Токен не найден!"}
    if "token" in user:
        del user["token"]
    
    await log(user["id"], user["login"], "logout")
    
    return {"status": "success", "message": "Вы вышли из системы!"}




@server.on_event("shutdown")
async def shutdown_event():
    functions.data("save", usrlst, people)
    print(f"Сервер остановлен. Сохранено пользователей: {len(usrlst)}")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:server", host="0.0.0.0", port=8000, reload=True)