from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, List
import random
import string
import hashlib
import time

app = FastAPI(title="Auth API", description="Простая система аутентификации")

# Модели данных
class UserRegister(BaseModel):
    login: str
    password: str
    name: Optional[str] = ""

class UserLogin(BaseModel):
    login: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    login: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    login: str
    name: str

# "База данных" в памяти
users = []
sessions = {}

# Вспомогательные функции
def generate_token():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

def get_current_user(authorization: str = Header(...)):
    if authorization not in sessions:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    user_id = sessions[authorization]
    user = next((u for u in users if u['id'] == user_id), None)
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return user

# Эндпоинты
@app.post("/register", response_model=dict)
async def register(user_data: UserRegister):
    # Проверяем логин на ASCII символы
    if not all(ord(c) < 128 for c in user_data.login):
        raise HTTPException(status_code=400, detail="Логин должен содержать только английские буквы и цифры")
    
    # Форматируем логин
    formatted_login = user_data.login.strip().replace(' ', '_')
    
    # Проверяем уникальность логина
    for user in users:
        if user['login'] == formatted_login:
            raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")
    
    # Проверка пароля
    errors = []
    
    if len(user_data.password) < 10:
        errors.append("Пароль должен содержать не менее 10 символов")
    
    if not any(c.isupper() for c in user_data.password):
        errors.append("Пароль должен содержать хотя бы одну заглавную букву")
    
    if not any(c.islower() for c in user_data.password):
        errors.append("Пароль должен содержать хотя бы одну строчную букву")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in user_data.password):
        errors.append("Пароль должен содержать хотя бы один специальный символ: !@#$%^&*()_+-=[]{}|;:,.<>?")
    
    if errors:
        raise HTTPException(status_code=400, detail={
            "error": "Неверный формат пароля",
            "details": errors
        })
    
    # Создаём пользователя
    new_user = {
        "id": len(users) + 1,
        "login": formatted_login,
        "password": user_data.password,
        "name": user_data.name
    }
    
    users.append(new_user)
    
    # Создаём сессию
    token = generate_token()
    sessions[token] = new_user['id']
    
    return {
        "message": "Пользователь зарегистрирован",
        "user": {
            "id": new_user['id'],
            "login": formatted_login,
            "name": user_data.name
        },
        "token": token
    }

@app.post("/login", response_model=dict)
async def login(user_data: UserLogin):
    # Ищем пользователя
    for user in users:
        if user['login'] == user_data.login and user['password'] == user_data.password:
            token = generate_token()
            sessions[token] = user['id']
            
            return {
                "message": "Успешный вход",
                "user": {
                    "id": user['id'],
                    "login": user['login'],
                    "name": user['name']
                },
                "token": token
            }
    
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")

@app.post("/logout", response_model=dict)
async def logout(authorization: str = Header(...)):
    if authorization in sessions:
        del sessions[authorization]
        return {"message": "Успешный выход"}
    
    raise HTTPException(status_code=401, detail="Не авторизован")

@app.get("/profile", response_model=UserResponse)
async def get_profile(user: dict = Depends(get_current_user)):
    return {
        "id": user['id'],
        "login": user['login'],
        "name": user['name']
    }

@app.put("/profile", response_model=UserResponse)
async def update_profile(update_data: UserUpdate, user: dict = Depends(get_current_user)):
    if update_data.name is not None:
        user['name'] = update_data.name
    
    if update_data.login is not None:
        formatted_login = update_data.login.strip().replace(' ', '_')
        
        # Проверяем уникальность нового логина
        for u in users:
            if u['login'] == formatted_login and u['id'] != user['id']:
                raise HTTPException(status_code=400, detail="Логин уже используется")
        
        user['login'] = formatted_login
    
    return {
        "id": user['id'],
        "login": user['login'],
        "name": user['name']
    }

@app.get("/")
async def home():
    return {"message": "Сервер работает!"}

# Дополнительные эндпоинты для отладки
@app.get("/users", response_model=List[UserResponse])
async def get_all_users():
    return [{"id": u["id"], "login": u["login"], "name": u["name"]} for u in users]

@app.get("/sessions")
async def get_sessions():
    return {"active_sessions": len(sessions)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
