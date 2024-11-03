import uuid

from fastapi import APIRouter, Depends, Cookie, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Any
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models import get_db, Users
from crud import create_user, read_user_name


router = APIRouter(prefix="", tags=["auth"])
templates = Jinja2Templates("templates")

COOKIES: dict[str, dict[str, Any]] = {}
COOKIE_SESSION_ID_KEY = "web-app-session-id"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_session_id() -> str:
    return uuid.uuid4().hex

def get_session_data(session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),):
    if session_id not in COOKIES:
        return None
    return COOKIES[session_id]

@router.get("/registration")
def registration_page(request: Request, user_session_data: dict = Depends(get_session_data)):
    if not user_session_data:
        return templates.TemplateResponse("registration.html", {'request': request,
                                                                'user': None,
                                                               })
    error = "Для создания новой учетной записи - выйдите из старой."
    return templates.TemplateResponse("error.html", {'request': request,
                                                     'error': error,
                                                     'user': user_session_data})

@router.post('/registration')
def create_user_page(request: Request, username: str = Form(), email: str = Form(),
                password1: str = Form(), password2: str = Form(), db: Session = Depends(get_db),
                     user_session_data: dict = Depends(get_session_data)):
    err = False
    messages = []
    user = read_user_name(db, username)
    if user:
        messages.append("Пользователь с таким именем уже существует")
        err = True
    user = db.query(Users).filter_by(email=email).first()
    if user:
        messages.append("Пользователь с такой почтой уже существует")
        err = True
    if len(username) > 30 or len(username) < 3:
        messages.append("Имя пользователя должно быть от 3 до 30 символов")
        err = True
    if password1 != password2:
        messages.append("Пароли должны совпадать")
        err = True
    if len(password1) > 20 or len(password1) < 8:
        messages.append("Пароль должен быть от 8 до 20 символов")
        err = True
    if err:
        return templates.TemplateResponse("registration.html", {'request': request,
                                                            'user': None,
                                                            'profile': False,
                                                            "messages": messages,
                                                           })

    password = password_context.hash(password1)
    create_user(db, username, password, email)
    session_id = generate_session_id()
    user = db.query(Users).filter_by(username=username).first()
    if user:
        COOKIES[session_id] = {
            'username': user.username,
            'id': user.id,
        }
        response = RedirectResponse('/', status_code=302)
        response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)
        return response
    error = "Ошибка создания нового пользователя. Попробуйте позже."
    return templates.TemplateResponse("error.html", {'request': request,
                                                     'error': error,
                                                     'user': user_session_data})

@router.get('/logout')
def logout_user_page(session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY)):
            COOKIES.pop(session_id)
            response = RedirectResponse('/', status_code=302)
            response.set_cookie(COOKIE_SESSION_ID_KEY, "noneuser")
            return response

@router.get("/login")
def login_page(request: Request, user_session_data: dict = Depends(get_session_data)):
    if not user_session_data:
        return templates.TemplateResponse("login.html", {'request': request,
                                                         'user': None,
                                                         })
    error = "Вы уже авторизованы. Выйдите из учетной записи, чтоб переавторизоваться."
    return templates.TemplateResponse("error.html", {'request': request,
                                                     'error': error,
                                                     'user': user_session_data})

@router.post('/login')
def login_user_page(request: Request, username: str = Form(),
               password: str = Form(), db: Session = Depends(get_db),):
    user = db.query(Users).filter_by(username=username).first()
    messages = []
    if user:
        if password_context.verify(password, user.password):
            session_id = generate_session_id()
            COOKIES[session_id] = {
                'username': user.username,
                'id': user.id,
            }
            response = RedirectResponse('/', status_code=302)
            response.set_cookie(COOKIE_SESSION_ID_KEY, session_id, path='/')
            return response
        else:
            messages.append("Неверный пароль")
            return templates.TemplateResponse("login.html", {'request': request,
                                                             'user': None,
                                                             "messages": messages,
                                                             })
    else:
        messages.append("Нет пользователя с таким именем")
        return templates.TemplateResponse("login.html", {'request': request,
                                                            'user': None,
                                                            "messages": messages,
                                                           })


# @router.get("/check-cookie")
# def demo_auth_check_cookie(
#         user_session_data: dict = Depends(get_session_data),
# ):
#     if user_session_data:
#         username = user_session_data["username"]
#         return {
#             "message": f"Hello, {username}",
#             **user_session_data,
#         }
#     return {"user": "unauthorised"}
