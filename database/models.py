from sqlalchemy import Column, Integer, String, create_engine, Float, BigInteger, ForeignKey, DateTime, Boolean, func, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pytz

Base = declarative_base()


moscow_tz = pytz.timezone('Europe/Moscow')

class Config(Base):
    __tablename__ = 'config'

    key = Column(String, primary_key=True)
    value = Column(String)



class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger)
    lang = Column(String, default=None)
    created_time = Column(DateTime(timezone=True))
    subscription_end = Column(DateTime(timezone=True))
    refered_by = Column(String, default=None)
    ref_secured_id = Column(String, default=None)
    ref_balance = Column(Float, default=0.0)


