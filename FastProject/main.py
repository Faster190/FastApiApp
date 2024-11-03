from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from models import Base, engine, get_db
from crud import *
from routers import authorization
from routers.authorization import get_session_data

app = FastAPI()
Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")


@app.get('/')
def main_page(request: Request, db: Session = Depends(get_db), user_session_data: dict = Depends(get_session_data)):
    posts = read_posts(db)
    return templates.TemplateResponse("main_page.html", {'request': request,
                                                         'posts': posts,
                                                         'user': user_session_data,
                                                         'profile': False
                                                         })

@app.get('/post/{post_id:path}')
def post_page(post_id: int, request: Request, db: Session = Depends(get_db),
              user_session_data: dict = Depends(get_session_data)):
    post = read_post_id(db, post_id)
    if post is None:
        error = "Такой статьи нет."
        return templates.TemplateResponse("error.html", {'request': request,
                                                         'error': error,
                                                         'user': user_session_data})

    user = read_user_id(db, post.user_id)
    return templates.TemplateResponse("post_page.html", {'request': request,
                                                         'post': post,
                                                         'user': user_session_data,
                                                         'profile': False,
                                                         'author': user
                                                         })

@app.get('/create-post')
def create_post_page(request: Request, user_session_data: dict = Depends(get_session_data)):
    if not user_session_data:
        return RedirectResponse('/login', status_code=302)
    return templates.TemplateResponse("create_post.html", {'request': request,
                                                         'user': user_session_data,
                                                         'profile': False
                                                         })

@app.post('/create-post')
def create_post_page(title: str = Form(), intro: str = Form(), text: str = Form(), user_id: int = 1,
                     db: Session = Depends(get_db), user_session_data: dict = Depends(get_session_data)):
    user_id = user_session_data['id']
    create_post(db, title, intro, text, user_id)
    return RedirectResponse('/', status_code=302)


@app.get('/update/{post_id}')
def update_post(post_id: int, request: Request, db: Session = Depends(get_db),
                user_session_data: dict = Depends(get_session_data)):
    post = read_post_id(db, post_id)
    if post is None:
        error = "Такой статьи нет."
        return templates.TemplateResponse("error.html", {'request': request,
                                                         'error': error,
                                                         'user': user_session_data})
    if user_session_data['id'] == post.user_id:
        return templates.TemplateResponse("update_post.html", {'request': request,
                                                             'post': post,
                                                             'user': user_session_data,
                                                             'profile': False,
                                                             })
    return RedirectResponse('/', status_code=302)

@app.post('/update/{post_id}')
def update_post(post_id: int, request: Request, db: Session = Depends(get_db),
                title: str = Form(), intro: str = Form(), text: str = Form()):
    post = update_post_id(db, post_id, title, intro, text)
    if post is None:
        error = "При обновлении статьи произошла ошибка. Попробуйте позже."
        return templates.TemplateResponse("error.html", {'request': request,
                                                         'error': error,
                                                         'user': 0})
    return RedirectResponse('/', status_code=302)

# @app.post('/create-user')
# def create_user_page(username: str, password:str, email: str, db: Session = Depends(get_db)):
#     return create_user(db, username, password, email)
#
# @app.get('/user')
# def read_user_page(username: str, db: Session = Depends(get_db)):
#     return read_user_name(db, username=username)

@app.get('/delete/{post_id}')
def delete_post(post_id: int, request: Request, db: Session = Depends(get_db),
                user_session_data: dict = Depends(get_session_data)):
    post = read_post_id(db, post_id)
    if user_session_data['id'] == post.user_id:
        post = delete_post_id(db, post_id)
    if post is None:
        error = "При удалении статьи произошла ошибка. Попробуйте позже."
        return templates.TemplateResponse("error.html", {'request': request,
                                                         'error': error,
                                                         'user': user_session_data})
    return RedirectResponse('/', status_code=302)

@app.get('/profile')
def profile_page(request: Request, db: Session = Depends(get_db), user_session_data: dict = Depends(get_session_data)):
    if not user_session_data:
        return RedirectResponse('/login', status_code=302)
    posts = read_posts_id(db, user_session_data['id'])
    return templates.TemplateResponse("main_page.html", {'request': request,
                                                         'posts': posts,
                                                         'user': user_session_data,
                                                         'profile': True
                                                         })

app.include_router(authorization.router)
