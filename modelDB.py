from sqlalchemy import Column, Integer, String, BOOLEAN, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, server_default='now()')
    id_telega = Column(BigInteger, unique=True)
    nickname = Column(String)
    username = Column(String)
    subs = Column(BOOLEAN)  # True - подписан , False - отписался


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name_ct = Column(String)
    general = Column(BOOLEAN)  # True - общие, False - личные


class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    name_word = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'))
    word = relationship(Category, backref="Words")
    general = Column(BOOLEAN)  # True - общие, False - личные


class UserCategory(Base):
    __tablename__ = 'user_categories'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)
    flag_active = Column(BOOLEAN)


class UserWord(Base):
    __tablename__ = 'user_words'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'), primary_key=True)
    flag_active = Column(BOOLEAN)


def create_tables(engine):
    Base.metadata.create_all(engine)
