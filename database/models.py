from sqlalchemy import Integer, Boolean, String, DateTime, ForeignKey, func
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)

    missions = relationship("Mission", back_populates="user", cascade="all, delete-orphan")


class Mission(Base):
    __tablename__ = 'mission'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.tg_user_id'))
    goal: Mapped[str] = mapped_column(String(255))
    total_amount: Mapped[int] = mapped_column(Integer)
    income: Mapped[int] = mapped_column(Integer)
    period_payments: Mapped[int] = mapped_column(Integer)
    date_created: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    saved_amount: Mapped[int] = mapped_column(Integer, default=0)

    user = relationship('User', back_populates='missions', foreign_keys=[user_id])
    payments = relationship("Payment", back_populates="mission", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = 'payment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mission_id: Mapped[int] = mapped_column(Integer, ForeignKey('mission.id'))
    amount: Mapped[int] = mapped_column(Integer, default=0)
    date: Mapped[datetime] = mapped_column(DateTime())
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)

    mission = relationship("Mission", back_populates="payments", foreign_keys=[mission_id])
