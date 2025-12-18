import functions
import requests




class Client:
    def __init__(self, serverurl="http://localhost:8000"):
        self.serverurl = serverurl
        self.token = None
        self.userid = None
        self.login = None
    
    




    async def contact(self, endpoint: str, data: dict = None, method: str = "POST"):
        try:
            if data is None:
                data = {}
                
            headers = {"Content-Type": "application/json"}
            if self.token:
                data["token"] = self.token
            
            if method == "GET":
                response = requests.get(
                    f"{self.serverurl}{endpoint}",
                    params=data,
                    headers=headers,
                    timeout=5
                )
            elif method == "DELETE":
                response = requests.delete(
                    f"{self.serverurl}{endpoint}",
                    params=data,
                    headers=headers,
                    timeout=5
                )
            elif method == "PATCH":
                response = requests.patch(
                    f"{self.serverurl}{endpoint}",
                    json=data,
                    headers=headers,
                    timeout=5
                )
            else:
                response = requests.post(
                    f"{self.serverurl}{endpoint}",
                    json=data,
                    headers=headers,
                    timeout=5
                )
            
            if response.status_code == 200:
                result = response.json()
                if "token" in result:
                    self.token = result["token"]
                return result
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Не удалось подключиться к серверу!"}
        except requests.exceptions.Timeout:
            return {"status": "error", "message": "Таймаут соединения!"}
        except Exception as e:
            return {"status": "error", "message": f"Ошибка: {str(e)}"}
    






    async def doregister(self):
        login = functions.makelogin("Логин: ")
        password = functions.makepassword("Пароль: ")
        r = await self.contact("/registration", {"login": login, "password": password})
        match r.get("status"):
            case "success":
                self.token = r["token"]
                self.userid = r["userid"]
                self.login = r["login"]
                print(f"Успешно! ID: {self.userid}")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def dologin(self):
        login = functions.safe("Логин: ")
        password = functions.safe("Пароль: ")
        r = await self.contact("/login", {"login": login, "password": password})
        match r.get("status"):
            case "success":
                self.token = r["token"]
                self.userid = r["userid"]
                self.login = r["login"]
                print(f"Добро пожаловать, {self.login}!")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def showtexts(self):
        r = await self.contact("/texts", {}, "GET")
        match r.get("status"):
            case "success":
                texts = r.get("texts", [])
                if len(texts) == 0:
                    print("У вас нет сохранённых текстов!")
                    return None
                print("\nВаши тексты:")
                for text in texts:
                    print(f"{text['id']}. {text['text'][:50]}...")
                return texts
            case "error": 
                print(f"Ошибка: {r['message']}")
                return None
            case _: 
                print("Ошибка сервера")
                return None
    






    async def encrypt(self):
        texts = await self.showtexts()
        if not texts:
            return
            
        try:
            textid = int(functions.safe("Выберите номер текста для шифрования: "))
            found = False
            for text in texts:
                if text["id"] == textid:
                    found = True
                    break
            if not found:
                print("Текст с таким номером не найден!")
                return
        except ValueError:
            print("Некорректный номер!")
            return
            
        key = functions.number("Ключ (число столбцов): ")
        if key <= 0:
            print("Ключ должен быть > 0")
            return
            
        r = await self.contact("/encrypt", {"textid": textid, "key": key})
        match r.get("status"):
            case "success": 
                print(f"\nИсходный текст: {r['originaltext']}")
                print(f"Зашифрованный текст: {r['encryptedtext']}")
                print(f"Использован ключ: {r['keyused']}")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def decrypt(self):
        texts = await self.showtexts()
        if not texts:
            return
            
        try:
            textid = int(functions.safe("Выберите номер текста для расшифрования: "))
            found = False
            for text in texts:
                if text["id"] == textid:
                    found = True
                    break
            if not found:
                print("Текст с таким номером не найден!")
                return
        except ValueError:
            print("Некорректный номер!")
            return
            
        key = functions.number("Ключ (число столбцов): ")
        if key <= 0:
            print("Ключ должен быть > 0")
            return
            
        r = await self.contact("/decrypt", {"textid": textid, "key": key})
        match r.get("status"):
            case "success": 
                print(f"\nИсходный текст: {r['originaltext']}")
                print(f"Расшифрованный текст: {r['decryptedtext']}")
                print(f"Использован ключ: {r['keyused']}")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def gethistory(self):
        r = await self.contact("/history", {}, "GET")
        match r.get("status"):
            case "success":
                history = r.get("history", [])
                print(f"История запросов:")
                for entry in history:
                    print(f"{entry['time']} - {entry['action']}")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def deletehistory(self):
        r = await self.contact("/history", {}, "DELETE")
        match r.get("status"):
            case "success": print(r["message"])
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def changepassword(self):
        newpassword = functions.makepassword("Новый пароль: ")
        r = await self.contact("/password", {"newpassword": newpassword}, "PATCH")
        match r.get("status"):
            case "success":
                print("Пароль изменён!")
                if "newtoken" in r:
                    self.token = r["newtoken"]
                    print("Токен обновлён!")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def addtext(self):
        text = functions.safe("Текст для сохранения: ")
        r = await self.contact("/texts", {"text": text})
        match r.get("status"):
            case "success": print(f"Текст сохранён! ID: {r.get('textid', 'неизвестно')}")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def updatetext(self):
        texts = await self.showtexts()
        if not texts:
            return
            
        try:
            textid = int(functions.safe("Выберите номер текста для изменения: "))
            found = False
            for text in texts:
                if text["id"] == textid:
                    found = True
                    break
            if not found:
                print("Текст с таким номером не найден!")
                return
        except ValueError:
            print("Некорректный номер!")
            return
            
        newtext = functions.safe("Новый текст: ")
        r = await self.contact(f"/texts/{textid}", {"newtext": newtext}, "PATCH")
        match r.get("status"):
            case "success": print("Текст обновлён!")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def deletetext(self):
        texts = await self.showtexts()
        if not texts:
            return
            
        try:
            textid = int(functions.safe("Выберите номер текста для удаления: "))
            found = False
            for text in texts:
                if text["id"] == textid:
                    found = True
                    break
            if not found:
                print("Текст с таким номером не найден!")
                return
        except ValueError:
            print("Некорректный номер!")
            return
            
        r = await self.contact(f"/texts/{textid}", {}, "DELETE")
        match r.get("status"):
            case "success": print("Текст удалён!")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def gettext(self):
        texts = await self.showtexts()
        if not texts:
            return
            
        try:
            textid = int(functions.safe("Выберите номер текста: "))
            found = False
            selected_text = None
            for text in texts:
                if text["id"] == textid:
                    found = True
                    selected_text = text
                    break
            if not found:
                print("Текст с таким номером не найден!")
                return
        except ValueError:
            print("Некорректный номер!")
            return
            
        print(f"\nТекст (ID: {selected_text['id']}):")
        print(selected_text["text"])
        print(f"Создан: {selected_text.get('createdat', 'неизвестно')}")
    






    async def getalltexts(self):
        texts = await self.showtexts()
        if texts:
            print(f"\nВсего текстов: {len(texts)}")
    






    async def profile(self):
        print(f"ID: {self.userid}")
        print(f"Логин: {self.login}")
        print(f"Токен: {self.token[:20]}...")
    






    async def logout(self):
        r = await self.contact("/logout", {"token": self.token})
        match r.get("status"):
            case "success":
                print(r["message"])
                self.token = None
                self.userid = None
                self.login = None
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    






    async def mainmenu(self):
        while True:
            if self.token:
                print(f"\nПользователь: {self.login}")
                print("1. Добавить текст")
                print("2. Мои тексты")
                print("3. Зашифровать текст")
                print("4. Расшифровать текст")
                print("5. Изменить текст")
                print("6. Удалить текст")
                print("7. История запросов")
                print("8. Очистить историю")
                print("9. Изменить пароль")
                print("10. Профиль")
                print("11. Выйти")
                print("12. Выйти из программы")
            else:
                print("\nГлавное меню:")
                print("1. Регистрация")
                print("2. Авторизация")
                print("3. О программе")
                print("4. Выйти из программы")
            choice = functions.safe("\nВыбор: ")
            match choice:
                case "1" if not self.token: await self.doregister()
                case "2" if not self.token: await self.dologin()
                case "3" if not self.token:
                    print("Шифр Скитала. Курсовая работа. Сулейманов Тимур Алиевич. 744-1. 2025-2026.")
                case "4" if not self.token: break
                case "1" if self.token: await self.addtext()
                case "2" if self.token: await self.showtexts()
                case "3" if self.token: await self.encrypt()
                case "4" if self.token: await self.decrypt()
                case "5" if self.token: await self.updatetext()
                case "6" if self.token: await self.deletetext()
                case "7" if self.token: await self.gethistory()
                case "8" if self.token: await self.deletehistory()
                case "9" if self.token: await self.changepassword()
                case "10" if self.token: await self.profile()
                case "11" if self.token: await self.logout()
                case "12" if self.token: break
                case _: print("Неверный выбор!")






async def main():
    client = Client()
    await client.mainmenu()






if __name__ == "__main__":
    import asyncio
    asyncio.run(main())