from sqlalchemy import create_engine, MetaData, Table, Integer, Boolean, String, \
    Column, DateTime, ForeignKey, Numeric, PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from sqlalchemy.orm import relationship

Base = declarative_base()
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer,  nullable=False, unique=True)
    username = Column(String(255), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_pk'),
        UniqueConstraint('tg_user_id'),
    )
    missions = relationship("Mission")

class Mission(Base):
    __tablename__ = 'mission'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    goal = Column(String(255), default="")
    total_amount = Column(Integer,default=0)
    income = Column(Integer, default=0)
    income_frequency = Column(Integer, default=0)
    period_payments = Column(Integer, default=0)
    date_created = Column(DateTime(), default=datetime.now)
    saved_amount = Column(Integer, default=0)
    __table_args__ = (
        PrimaryKeyConstraint('id', name='mission_pk'),
        ForeignKeyConstraint(['user_id'], ['user.id']),
    )
    payments = relationship("Payment")

class Payment(Base):
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True)
    mission_id = Column(Integer, ForeignKey('mission.id'))
    amount = Column(Integer, default=0)
    date = Column(DateTime())
    is_done = Column(Boolean, default=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='payment_pk'),
        ForeignKeyConstraint(['mission_id'], ['mission.id']),
    )