import math
from datetime import datetime
from typing import Optional
from dateutil.relativedelta import relativedelta
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Payment, User, Mission
import logging

logger = logging.getLogger(__name__)


async def add_user(session: AsyncSession, tg_user_id: int, username: str) -> User:
    query = select(User).where(User.tg_user_id == tg_user_id)
    user = await session.scalar(query)

    if user is None:
        user = User(tg_user_id=tg_user_id, username=username)
        session.add(user)
        await session.commit()
        logging.info(f'Создали в бд пользователя с tg id = {user.tg_user_id}')
    return user


async def add_mission(session: AsyncSession, user_id: int, goal: str,
                      total_amount: int, income: int, period_payments: int) -> Optional[Mission]:
    mission = Mission(
        user_id=user_id,
        goal=goal,
        total_amount=total_amount,
        income=income,
        period_payments=period_payments,
        saved_amount=0
    )
    session.add(mission)
    await session.commit()
    logger.info(f'Создали миссию с id = {mission.id} для пользователя {mission.user_id}')
    return mission

async def create_payments(session: AsyncSession, mission: Mission, period_payments: int, equal_payment: int, remainder: int):
    async with session.begin():
        payments = []
        current_date = datetime.now()

        for i in range(period_payments):
            payment_date = (current_date + relativedelta(months=i)).replace(day=1)
            payment_amount = equal_payment

            if i == period_payments - 1:
                payment_amount += remainder

            payment = Payment(
                mission_id=mission.id,
                amount=payment_amount,
                date=payment_date
            )
            payments.append(payment)

        session.add_all(payments)
        await session.commit()
        logger.info(f'Создали {len(payments)} платежей для миссии {mission.id}')

# async def add_payments(session: AsyncSession, mission: Mission, amount: int, count_payments_in_month: int):
#     # для определения дней платежей считаем ddays - смещение относительно начала месяца
#     count_payments_in_month = 4 if (count_payments_in_month > 4) else count_payments_in_month
#     count_payments_in_month = 1 if (count_payments_in_month == 0) else count_payments_in_month
#     ddays = math.ceil(28 / count_payments_in_month)
#
#     payments = []
#
#     date_created_begin_month = datetime(mission.date_created.year, mission.date_created.month, 1)
#     total_amount_cnt = 0  # будем использовать для устранения погрешности округления
#     for i in range(0, mission.period_payments):
#         for j in range(0, count_payments_in_month):
#             dd = j * ddays + (1 if (j == 0) else 0)
#             if ((dd <= mission.date_created.day) & (
#                     i == 0)):  # если рассчитанный день платежа меньше или равен дню создания цели для первого месяца, переносим этот график на последний месяц
#                 d = date_created_begin_month + relativedelta(months=mission.period_payments) + relativedelta(
#                     days=(dd - 1))
#             else:
#                 d = date_created_begin_month + relativedelta(months=i) + relativedelta(days=(dd - 1))
#
#             payments.append(Payment(mission_id=mission.id, amount=amount,
#                                     date=d))
#             total_amount_cnt = total_amount_cnt + amount
#
#     payments.sort(key=lambda x: x.date)
#     # у последней строки графика платежа отредактируем сумму с учетом погрешностей округления
#     payments[
#         mission.period_payments * count_payments_in_month - 1].amount = amount + mission.total_amount - total_amount_cnt
#
#     for payment in payments:
#         session.add(payment)
#
#     await session.commit()
