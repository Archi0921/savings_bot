import math
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy.future import select

from sqlalchemy.ext.asyncio import AsyncSession

from models import Payment, User, Mission


async def add_user(session: AsyncSession, tg_user_id: int, username: str) -> User:
    user = await session.execute(select(User).filter((User.tg_user_id == tg_user_id).any_()))

    if (user == None):
        user = User(tg_user_id=tg_user_id, username=username)
        session.add(user)
        await session.commit()
    return user


async def add_mission(session: AsyncSession, user: User, goal: str,
                      total_amount: int, income: int, income_frequency: int,
                      period_payments: int, amount: int, count_payments_in_month: int):
    # будут ли у нас цели уникальны по наименованию для пользователя?
    # надо ли делать проверку на наличие цели по наименованию?
    mission = Mission(user_id=user.id, goal=goal, total_amount=total_amount,
                      income=income, income_frequency=income_frequency,
                      period_payments=period_payments)
    session.add(mission)
    await session.commit()
    return mission


async def add_payments(session: AsyncSession, mission: Mission, amount: int, count_payments_in_month: int):
    # для определения дней платежей считаем ddays - смещение относительно начала месяца
    count_payments_in_month = 4 if (count_payments_in_month > 4) else count_payments_in_month
    count_payments_in_month = 1 if (count_payments_in_month == 0) else count_payments_in_month
    ddays = math.ceil(28 / count_payments_in_month)

    payments = []

    date_created_begin_month = datetime(mission.date_created.year, mission.date_created.month, 1)
    total_amount_cnt = 0  # будем использовать для устранения погрешности округления
    for i in range(0, mission.period_payments):
        for j in range(0, count_payments_in_month):
            dd = j * ddays + (1 if (j == 0) else 0)
            if ((dd <= mission.date_created.day) & (
                    i == 0)):  # если рассчитанный день платежа меньше или равен дню создания цели для первого месяца, переносим этот график на последний месяц
                d = date_created_begin_month + relativedelta(months=mission.period_payments) + relativedelta(
                    days=(dd - 1))
            else:
                d = date_created_begin_month + relativedelta(months=i) + relativedelta(days=(dd - 1))

            payments.append(Payment(mission_id=mission.id, amount=amount,
                                    date=d))
            total_amount_cnt = total_amount_cnt + amount

    payments.sort(key=lambda x: x.date)
    # у последней строки графика платежа отредактироваем сумму с учетом погрешностей округления
    payments[
        mission.period_payments * count_payments_in_month - 1].amount = amount + mission.total_amount - total_amount_cnt

    for payment in payments:
        session.add(payment)

    await session.commit()

