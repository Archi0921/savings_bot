from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from aiogram import Bot

from bot.keyboards import create_schedule_kb
from database.models import *
from database.database import AsyncSessionLocal as async_session
import logging

from database.utils import get_mission_by_id


def set_scheduled_jobs(scheduler, bot):
    # тестовая задача, следующую строку необходимо закомментить в рабочем варианте
    scheduler.add_job(send_schedules, "cron", hour ="*", minute = "*", args=(bot, ))
    #задачи, которые надо раскомментировать для рабочего варианта
    # scheduler.add_job(send_schedules, "cron", day=1, hour=12, minute=0, args=(bot, ))
    # scheduler.add_job(send_schedules, "cron", day=10, hour=12, minute=0, args=(bot, ))
    # scheduler.add_job(send_schedules, "cron", day=20, hour=12, minute=0, args=(bot, ))


@asynccontextmanager
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def send_schedules(bot: Bot):

    first_day_current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    second_day_current_month = first_day_current_month.replace(day=2)
    logging.info('Start send schedules')

    async with get_session() as session:
        payments = await session.scalars(select(Payment).where(
            (Payment.date >= first_day_current_month)
            & (Payment.date < second_day_current_month)
            & (Payment.is_done == False)))

        for payment in payments:
            mission = await get_mission_by_id(session, payment.mission_id)

            await bot.send_message(chat_id=mission.user_id,
                                   text="Для достижения цели: " + mission.goal + "\nне забудьте положить в копилку " + str(
                                       payment.amount), reply_markup=create_schedule_kb(payment.id))

    logging.info('Finish send schedules')
