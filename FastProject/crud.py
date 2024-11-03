from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from models import Users, Posts


def create_user(db: Session, username, password, email):
    db_item = Users(username=username, password=password, email=email)
    db.add(db_item)
    db.commit()
    return db_item

def create_post(db: Session, title, intro, text, user_id):
    db_item = Posts(title=title, intro=intro, text=text, user_id=user_id)
    db.add(db_item)
    db.commit()
    return db_item

def read_post_id(db: Session, post_id):
    db_item = db.query(Posts).filter(Posts.id == post_id).first()
    if db_item is not None:
        return db_item
    return None

def read_user_id(db: Session, user_id):
    db_item = db.query(Users).filter(Users.id == user_id).first()
    if db_item is not None:
        return db_item
    return None

def read_user_name(db: Session, username):
    db_item = db.query(Users).filter(Users.username == username).first()
    if db_item is not None:
        return db_item
    return None

def read_posts(db: Session):
    db_item = db.query(Posts).order_by(Posts.date.desc()).all()
    if db_item is not None:
        return db_item
    return None

def read_posts_id(db: Session, user_id):
    db_item = db.query(Posts).filter(Posts.user_id == user_id).order_by(Posts.date.desc()).all()
    if db_item is not None:
        return db_item
    return None

def update_post_id(db: Session, post_id, title, intro, text):
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if post is not None:
        db.execute(update(Posts).where(Posts.id == post_id).values(title=title, intro=intro, text=text))
        db.commit()
        return post_id
    return None

def delete_post_id(db: Session, post_id):
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if post is not None:
        db.execute(delete(Posts).where(Posts.id == post_id))
        db.commit()
        return post_id
    return None
