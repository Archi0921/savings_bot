from contextlib import asynccontextmanager

from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.orm import selectinload

from database.database import AsyncSessionLocal as async_session
from database.models import *
from database.utils import *

logger = logging.getLogger(__name__)
router = Router()


def register_handlers(dp):
    dp.include_router(router)


@asynccontextmanager
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@router.message(CommandStart())
async def cmd_start(message: Message):
    async with get_session() as session:
        user = await add_user(session, message.from_user.id, message.from_user.username)
    await message.answer(f'Привет! Это бот для накоплений.\n'
                         'Вам нужно ввести свою цель, сумму, дату, к которой нужно накопить и информацию о доходах\n'
                         'А я помогу вам рассчитать размер и частоту внесения для достижения цели\n'
                         'Чтобы начать, отправьте команду /goal\n'
                         'Чтобы посмотреть список всех целей, введите /list\n')


class UserMissionState(StatesGroup):
    goal = State()
    total_amount = State()
    income = State()
    savings_percentage = State()


class GoalSelectionState(StatesGroup):
    goal_number = State()


@router.message(Command('goal'))
async def add_goal(message: Message, state: FSMContext):
    await message.answer('На что вы планируете копить? Укажите название для вашей цели:')
    await state.set_state(UserMissionState.goal)


@router.message(UserMissionState.goal)
async def goal_handler(message: Message, state: FSMContext):
    async with get_session() as session:
        goal = message.text
        user_id = message.from_user.id

        existing_mission_query = select(Mission).where(Mission.user_id == user_id, Mission.goal == goal)
        existing_mission = await session.scalar(existing_mission_query)

        if existing_mission is not None:
            await message.answer('У вас уже есть цель с таким названием. Пожалуйста, введите другое название:')
            return

        await state.update_data(goal=goal)
        await message.answer('Какую сумму вы хотите накопить? Введите число:')
        await state.set_state(UserMissionState.total_amount)


@router.message(UserMissionState.total_amount)
async def total_amount_handler(message: Message, state: FSMContext):
    try:
        total_amount = int(message.text)
        await state.update_data(total_amount=total_amount)

        await message.answer('Какова ваша месячная зарплата?')
        await state.set_state(UserMissionState.income)
    except ValueError:
        await message.answer('Пожалуйста, укажите сумму вашей цели числом:')


@router.message(UserMissionState.income)
async def income_handler(message: Message, state: FSMContext):
    try:
        income = int(message.text)
        await state.update_data(income=income)

        await message.answer('Какой процент от зарплаты вы готовы откладывать ежемесячно?')
        await state.set_state(UserMissionState.savings_percentage)
    except ValueError:
        await message.answer('Сумму дохода необходимо указать числом:')


@router.message(UserMissionState.savings_percentage)
async def savings_percentage_handler(message: Message, state: FSMContext):
    async with get_session() as session:
        try:
            savings_percentage = int(message.text)
            await state.update_data(savings_percentage=savings_percentage)

            data = await state.get_data()
            if not all(key in data for key in ['goal', 'total_amount', 'income', 'savings_percentage']):
                await message.answer('Ошибка: Не хватает данных для сохранения цели')
                return

            goal = data['goal']
            total_amount = data['total_amount']
            income = data['income']

            monthly_savings = round(income * (savings_percentage / 100))
            period_payments = total_amount // monthly_savings

            equal_payment = total_amount // period_payments
            remainder = total_amount % period_payments

            user_id = message.from_user.id
            user_query = select(User).where(User.tg_user_id == user_id)
            user = await session.scalar(user_query)
            if user is None:
                user = User(tg_user_id=user_id, username=message.from_user.username)
                session.add(user)
                await session.commit()

            mission = await add_mission(
                session=session,
                user_id=user.tg_user_id,
                goal=goal,
                total_amount=total_amount,
                income=income,
                period_payments=period_payments
            )

            await create_payments(session, mission, period_payments, equal_payment, remainder)

            await message.answer(
                f"Цель: {goal}\n"
                f"Необходимая сумма: {total_amount}\n"
                f"Месячный доход: {income}\n"
                f"Процент откладывания: {savings_percentage}%\n"
                f"Период накоплений: {period_payments} месяцев\n"
                f"Ежемесячный взнос: {equal_payment}\n\n"
                f"Чтобы посмотреть список всех целей, введите /list\n"
                f"Чтобы добавить еще цель, введите /goal\n"
            )

            await state.clear()
        except ValueError:
            await message.answer('Процент дохода необходимо указать числом:')


@router.message(Command('list'))
async def goals_list_handler(message: Message, state: FSMContext):
    async with (get_session() as session):
        user_id = message.from_user.id
        query = select(Mission).where(Mission.user_id == user_id)
        result = await session.execute(query)

        goals = result.scalars().all()
# Проверить эту часть
        if goals:
            goals_list = [f'{idx + 1}. {goal.goal}' for idx, goal in enumerate(goals)]
            goals_text = f'\n'.join(goals_list)

            await message.answer(f'Вот список ваших целей:\n{goals_text}\n\n')
            await message.answer('Введите номер цели, чтобы увидеть подробную информацию')
            await state.set_state(GoalSelectionState.goal_number)
        else:
            await message.answer('У вас пока нет целей\n'
                                 'Чтобы добавить цель введите команду /goal')
            return


@router.message(GoalSelectionState.goal_number)
async def goal_details_handler(message: Message, state:FSMContext):
    try:
        number = int(message.text) - 1
    except ValueError:
        await message.answer('Пожалуйста, введите корректный номер цели')

    async with get_session() as session:
        user_id = message.from_user.id
        goals = await session.execute(
            select(Mission)
            .where(Mission.user_id == user_id)
            .options(selectinload(Mission.payments))
        )
        goals = goals.scalars().all()

    if 0 <= number < len(goals):
        selected_goal = goals[number]
        payments = selected_goal.payments
        goal_info = (
            f"Цель: {selected_goal.goal}\n"
            f"Необходимая сумма: {selected_goal.total_amount}\n"
            f"Месячный доход: {selected_goal.income}\n"
            f"Период накоплений: {selected_goal.period_payments} месяцев\n"
            f"Количество внесенных платежей: {selected_goal.saved_amount}\n"
        )
        payment = payments[0]
        goal_info += (f'Ежемесячный взнос: {payment.amount}\n\n'
                      f'Вернуться к списку /list'
                      )

        await message.answer(goal_info)
    else:
        await message.answer('Неправильный номер целию Попробуйте снова')

    await state.clear()



#
# @router.message(UserMissionState.period_payments)
# async def period_payments_handler(message: Message, state: FSMContext):
#     async with get_session() as session:
#         try:
#             period_payments = int(message.text)
#             await state.update_data(period_payments=period_payments)
#
#             data = await state.get_data()
#             if not all(key in data for key in ['goal', 'total_amount', 'income', 'income_frequency', 'period_payments']):
#                 await message.answer('Ошибка: Нехватает данных для сохранения цели')
#                 return
#
#             user_id = message.from_user.id
#             goal = data['goal']
#             total_amount = data['total_amount']
#             income = data['income']
#             income_frequency = data['income_frequency']
#             period_payments = data['period_payments']
#
#             user_query = select(User).where(User.tg_user_id == user_id)
#             user = await session.scalar(user_query)
#             if user is None:
#                 user = User(tg_user_id=user_id, username=message.from_user.username)
#                 session.add(user)
#                 await session.commit()
#
#             new_mission = await add_mission(session, user.tg_user_id, goal, total_amount, income, income_frequency, period_payments)
#
#             total_payments = period_payments * income_frequency
#             payment_amount = total_amount // total_payments
#             await add_payments(session, new_mission, payment_amount, income_frequency)
#
#             await message.answer(f'Ваша цель успешно сохранена:\n'
#                                  f'Название: {new_mission.goal}\n'
#                                  f'Сумма: {new_mission.total_amount}\n'
#                                  f'Общее количество платежей: {total_payments}\n'
#                                  f'Сумма одного платежа: {payment_amount}')
#             await state.clear()
#         except ValueError:
#             await message.answer('Пожалуйста, укажите количество месяцев числом:')