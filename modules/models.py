from sqlalchemy import Column, Integer, String, Text, ForeignKey, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    fullname = Column(String(150), nullable=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    dob = Column(String(20), nullable=True)
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250), nullable=True)
    reset_token = Column(String(250), nullable=True)
    confirmemail = Column(String(120), nullable=True)
    image = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    following = Column(PickleType, nullable=True, default=[])
    followingcount = Column(Integer, default=0)
    followers = Column(PickleType, nullable=True, default=[])
    followerscount = Column(Integer, default=0)
    memories = Column(PickleType, nullable=True, default={"public": [], "liked": [], "draft": [], "private": []})
    my_comments = Column(PickleType, nullable=True, default=[])


class Memory(Base):
    __tablename__ = 'memories'

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    timestamp = Column(String(50), nullable=False)
    image = Column(PickleType, nullable=True, default=[])
    description = Column(Text, nullable=True)
    share = Column(String(50), nullable=True)
    type = Column(String(50), nullable=False)
    calendar = Column(String(50), nullable=True)
    likes = Column(Integer, default=0)
    likelist = Column(PickleType, nullable=True, default=[])
    file = Column(PickleType, nullable=True, default=[])
    comments = Column(PickleType, nullable=True, default=[])

    user = relationship('User', backref='memories')
