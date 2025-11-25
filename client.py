import requests
import json
import re

BASE_URL = "http://localhost:8000"

def integerSafeInput(prompt="Введите число: "):
    while True:
        try:
            anyInteger = int(input(prompt))
            return anyInteger
        except Exception as e:
            print(f"Ошибка. Подробнее: {e}")

def stringSafeInput(prompt="Введите текст: "):
    while True:
        try:
            text = input(prompt).strip()
            if text:
                return text
            print("Ошибка. Поле не может быть пустым")
        except Exception as e:
            print(f"Ошибка. Подробнее: {e}")

def validate_password(password):
    """Проверка сложности пароля на клиенте."""
    errors = []
    
    if len(password) < 10:
        errors.append("Пароль должен содержать не менее 10 символов.")
    
    if not any(c.isupper() for c in password):
        errors.append("Пароль должен содержать хотя бы одну заглавную букву.")
    
    if not any(c.islower() for c in password):
        errors.append("Пароль должен содержать хотя бы одну строчную букву.")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("Пароль должен содержать хотя бы один специальный символ.")
    
    return errors

def print_response(response):
    """Красиво выводит ответ от сервера."""
    try:
        data = response.json()
        if response.status_code == 200:
            print("Выполнено.")
        else:
            print(f"Ошибка {response.status_code}.")
            if "detail" in data:
                if isinstance(data["detail"], dict):
                    for error in data["detail"].get("details", []):
                        print(f" - {error}")
                else:
                    print(f" - {data['detail']}")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except:
        print(f"Ошибка {response.status_code}.")
        print(response.text)

def register():
    print("\nРегистрация.")
    login = stringSafeInput("Логин: ")
    
    while True:
        password = stringSafeInput("Пароль: ")
        password_confirm = stringSafeInput("Подтвердите пароль: ")
        
        if password != password_confirm:
            print("Ошибка. Пароли не совпадают.")
            continue
            
        password_errors = validate_password(password)
        if password_errors:
            for error in password_errors:
                print(error)
            continue
            
        break
    
    name = stringSafeInput("Имя (необязательно): ") or ""
    
    data = {
        "login": login,
        "password": password,
        "name": name
    }
    
    response = requests.post(f"{BASE_URL}/register", json=data)
    print_response(response)
    
    if response.status_code == 201:
        token = response.json().get("token")
        return token
    return None

def login():
    print("\nВход.")
    login = stringSafeInput("Логин: ")
    password = stringSafeInput("Пароль: ")
    
    data = {
        "login": login,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/login", json=data)
    print_response(response)
    
    if response.status_code == 200:
        token = response.json().get("token")
        return token
    return None

def get_profile(token):
    print("\nПрофиль.")
    if not token:
        print("Необходима авторизация.")
        return
    
    headers = {"Authorization": token}
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    print_response(response)

def update_profile(token):
    print("\nОбновление профиля.")
    if not token:
        print("Необходима авторизация.")
        return
    
    print("Оставьте поле пустым, если изменение не требуется.")
    new_login = input("Новый логин: ").strip() or None
    new_name = input("Новое имя: ").strip() or None
    
    data = {}
    if new_login:
        data["login"] = new_login
    if new_name:
        data["name"] = new_name
    
    if not data:
        print("Хотя бы одно поле не может быть пустым.")
        return
    
    headers = {"Authorization": token}
    response = requests.put(f"{BASE_URL}/profile", json=data, headers=headers)
    print_response(response)

def logout(token):
    print("\nВыход.")
    if not token:
        print("Авторизация не выполнена.")
        return None
    
    headers = {"Authorization": token}
    response = requests.post(f"{BASE_URL}/logout", headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print("Токен удалён.")
        return None
    return token

def show_users():
    print("\nВсе пользователи.")
    response = requests.get(f"{BASE_URL}/users")
    print_response(response)

def main():
    current_token = None
    
    while True:
        print("\n")
        print("Клиент.")
        print("")
        
        if current_token:
            print(f"Токен: {current_token}")
        else:
            print("Авторизация не выполнена.")
        
        print("1. Регистрация,")
        print("2. Вход,")
        print("3. Посмотреть профиль,")
        print("4. Обновить профиль,")
        print("5. Выход,")
        print("6. Показать всех пользователей,")
        print("7. Выход из программы-клиента.")
        
        choice = integerSafeInput("\nВыберите действие (только число):")
        
        match choice:
            case 1:
                token = register()
                if token:
                    current_token = token
            case 2:
                token = login()
                if token:
                    current_token = token
            case 3:
                get_profile(current_token)
            case 4:
                update_profile(current_token)
            case 5:
                current_token = logout(current_token)
            case 6:
                show_users()
            case 7:
                print("Выход...")
                break
            case _:
                print("Вариант не найден.")

if __name__ == "__main__":
    main()