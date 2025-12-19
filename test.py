import unittest
import requests

class TestScytaleAPI(unittest.TestCase):
    BASE_URL = "http://localhost:8000"
    
    def setUp(self):
        self.test_user = {
            "login": "testuser",
            "password": "Test123!@#"
        }
        self.token = None
        
    def test_01_register_user(self):
        response = requests.post(f"{self.BASE_URL}/registration", json=self.test_user)
        print(f"Регистрация: {response.status_code} - {response.text}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                self.assertIn("token", data)
                self.assertIn("userid", data)
                self.token = data["token"]
                self.userid = data["userid"]
            else:
                print(f"Ошибка регистрации: {data.get('message')}")
        
    def test_02_login_user(self):
        response = requests.post(f"{self.BASE_URL}/login", json=self.test_user)
        print(f"Авторизация: {response.status_code} - {response.text}")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                self.assertIn("token", data)
                self.token = data["token"]
            else:
                print(f"Ошибка авторизации: {data.get('message')}")
                
    def test_03_add_text(self):
        response = requests.post(f"{self.BASE_URL}/login", json=self.test_user)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data["token"]
                text_data = {"token": token, "text": "Текст для шифрования"}
                response = requests.post(f"{self.BASE_URL}/texts", json=text_data)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["status"], "success")
                self.assertIn("textid", data)
        
    def test_04_encrypt_text(self):
        response = requests.post(f"{self.BASE_URL}/login", json=self.test_user)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data["token"]
                text_data = {"token": token, "text": "Hello World"}
                response = requests.post(f"{self.BASE_URL}/texts", json=text_data)
                if response.status_code == 200:
                    textid = response.json()["textid"]
                    encrypt_data = {"token": token, "textid": textid, "key": 3}
                    response = requests.post(f"{self.BASE_URL}/encrypt", json=encrypt_data)
                    self.assertEqual(response.status_code, 200)
                    data = response.json()
                    self.assertEqual(data["status"], "success")
                    self.assertIn("encryptedtext", data)
                    self.assertIn("originaltext", data)
        
    def test_05_decrypt_text(self):
        response = requests.post(f"{self.BASE_URL}/login", json=self.test_user)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data["token"]
                text_data = {"token": token, "text": "ABCDEF"}
                response = requests.post(f"{self.BASE_URL}/texts", json=text_data)
                if response.status_code == 200:
                    textid = response.json()["textid"]
                    encrypt_data = {"token": token, "textid": textid, "key": 2}
                    response = requests.post(f"{self.BASE_URL}/encrypt", json=encrypt_data)
                    decrypt_data = {"token": token, "textid": textid, "key": 2}
                    response = requests.post(f"{self.BASE_URL}/decrypt", json=decrypt_data)
                    self.assertEqual(response.status_code, 200)
                    data = response.json()
                    self.assertEqual(data["status"], "success")
                    self.assertIn("decryptedtext", data)
        
    def test_06_invalid_encrypt_key(self):
        response = requests.post(f"{self.BASE_URL}/login", json=self.test_user)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data["token"]
                text_data = {"token": token, "text": "Test"}
                response = requests.post(f"{self.BASE_URL}/texts", json=text_data)
                if response.status_code == 200:
                    textid = response.json()["textid"]
                    encrypt_data = {"token": token, "textid": textid, "key": 0}
                    response = requests.post(f"{self.BASE_URL}/encrypt", json=encrypt_data)
                    data = response.json()
                    self.assertEqual(data["status"], "error")
                    self.assertIn("Ключ должен быть больше 0", data["message"])
        
    def test_07_get_history(self):
        response = requests.post(f"{self.BASE_URL}/login", json=self.test_user)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data["token"]
                response = requests.get(f"{self.BASE_URL}/history", params={"token": token})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["status"], "success")
                self.assertIn("history", data)
        
    def test_08_get_all_texts(self):
        response = requests.post(f"{self.BASE_URL}/login", json=self.test_user)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data["token"]
                response = requests.get(f"{self.BASE_URL}/texts", params={"token": token})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["status"], "success")
                self.assertIn("texts", data)
        
    def test_09_invalid_token(self):
        response = requests.get(f"{self.BASE_URL}/history", params={"token": "invalid_token"})
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("Недействительный токен", data["message"])
        
    def test_10_change_password(self):
        response = requests.post(f"{self.BASE_URL}/login", json=self.test_user)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data["token"]
                new_password = "NewPass123!@#"
                change_data = {"token": token, "newpassword": new_password}
                response = requests.patch(f"{self.BASE_URL}/password", json=change_data)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["status"], "success")
                self.assertIn("newtoken", data)
                response = requests.get(f"{self.BASE_URL}/history", params={"token": token})
                self.assertEqual(response.json()["status"], "error")
        
    def test_11_logout(self):
        response = requests.post(f"{self.BASE_URL}/login", json=self.test_user)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data["token"]
                logout_data = {"token": token}
                response = requests.post(f"{self.BASE_URL}/logout", json=logout_data)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["status"], "success")
                response = requests.get(f"{self.BASE_URL}/history", params={"token": token})
                self.assertEqual(response.json()["status"], "error")
        
    def test_12_duplicate_login(self):
        response1 = requests.post(f"{self.BASE_URL}/registration", json=self.test_user)
        response2 = requests.post(f"{self.BASE_URL}/registration", json=self.test_user)
        data = response2.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("Логин уже занят", data["message"])
        
    def test_13_invalid_password(self):
        invalid_user = {"login": "test_user_2", "password": "short"}
        response = requests.post(f"{self.BASE_URL}/registration", json=invalid_user)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("Пароль содержит менее 10 символов", data["message"])

if __name__ == '__main__':
    unittest.main()