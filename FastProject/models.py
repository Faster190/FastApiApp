from sqlalchemy import Column, Integer, String, create_engine, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

DATABASE_URL = "sqlite:///./blog.db"
Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Users(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(127), unique=True)
    password = Column(String(255))
    email = Column(String(20))
    date = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return '<Users %r>' % self.id


class Posts(Base):
    __tablename__ = "Posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    intro = Column(String(200))
    text = Column(Text)
    date = Column(DateTime, default=datetime.now)
    user_id = Column(Integer)


    def __repr__(self):
        return '<Games %r>' % self.id


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
