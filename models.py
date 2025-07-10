from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
