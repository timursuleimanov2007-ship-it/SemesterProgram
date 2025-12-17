import functions
import requests

class Client:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.token = None
        self.user_id = None
        self.login = None
    



    async def contact(self, endpoint: str, data: dict):
        try:
            if self.token:
                data["token"] = self.token
            response = requests.post(
                f"{self.server_url}{endpoint}",
                json=data,
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
                self.user_id = r["user_id"]
                self.login = r["login"]
                print(f"Успешно! ID: {self.user_id}")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    



    async def dologin(self):
        login = functions.safe("Логин: ")
        password = functions.safe("Пароль: ")
        r = await self.contact("/login", {"login": login, "password": password})
        match r.get("status"):
            case "success":
                self.token = r["token"]
                self.user_id = r["user_id"]
                self.login = r["login"]
                print(f"Добро пожаловать, {self.login}!")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    



    async def encrypt(self):
        text = functions.safe("Текст: ")
        key = functions.number("Ключ: ")
        if key <= 0:
            print("Ключ должен быть > 0")
            return
        r = await self.contact("/encrypt", {"text": text, "key": key})
        match r.get("status"):
            case "success": print(f"Зашифровано: {r['encrypted_text']}")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    



    async def decrypt(self):
        text = functions.safe("Текст: ")
        key = functions.number("Ключ: ")
        if key <= 0:
            print("Ключ должен быть > 0")
            return
        r = await self.contact("/decrypt", {"text": text, "key": key})
        match r.get("status"):
            case "success": print(f"Расшифровано: {r['decrypted_text']}")
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    



    async def profile(self):
        print(f"ID: {self.user_id}")
        print(f"Логин: {self.login}")
        print(f"Токен: {self.token[:20]}...")
    



    async def logout(self):
        r = await self.contact("/logout", {"token": self.token})
        match r.get("status"):
            case "success":
                print(r["message"])
                self.token = None
                self.user_id = None
                self.login = None
            case "error": print(f"Ошибка: {r['message']}")
            case _: print("Ошибка сервера")
    



    async def main_menu(self):
        while True:
            if self.token:
                print(f"Пользователь: {self.login}")
                print("1. Зашифровать")
                print("2. Расшифровать")
                print("3. Профиль")
                print("4. Выйти")
                print("5. Выйти из программы")
            else:
                print("1. Регистрация")
                print("2. Авторизация")
                print("3. О программе")
                print("4. Выйти")
            choice = functions.safe("Выбор: ")
            match choice:
                case "1" if not self.token: await self.doregister()
                case "2" if not self.token: await self.dologin()
                case "3" if not self.token:
                    print("Шифр Скитала. Курсовая работа.")
                case "4" if not self.token: break
                case "1" if self.token: await self.encrypt()
                case "2" if self.token: await self.decrypt()
                case "3" if self.token: await self.profile()
                case "4" if self.token: await self.logout()
                case "5" if self.token: break
                case _: print("Неверный выбор")




async def main():
    client = Client()
    await client.main_menu()




if __name__ == "__main__":
    import asyncio
    asyncio.run(main())