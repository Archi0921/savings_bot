from aiogram import Router
from aiogram import types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from savings_bot.database.database import AsyncSessionLocal as async_session
from savings_bot.database.models import Mission

router = Router()


def register_handlers(dp):
    dp.include_router(router)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет! Это бот для накоплений. '
                         'Вам нужно ввести свою цель, сумму, дату, к которой нужно накопить и информацию о доходах'
                         'А я помогу вам рассчитать размер и частоту внесения для достижения цели'
                         'Чтобы начать отправьте команду /goal')


class UserMissionState(StatesGroup):
    goal = State()
    total_amount = State()
    income = State()
    income_frequency = State()
    period_payments = State()


@router.message(Command('goal'))
async def add_goal(message: Message, state: FSMContext):
    await message.answer('Введите название цели:')
    await state.set_state(UserMissionState.goal)


@router.message(UserMissionState.goal)
async def goal_handler(message: Message, state: FSMContext):
    goal = message.text
    await state.update_data(goal=goal)

    await message.answer('Введите сумму цели:')
    await state.set_state(UserMissionState.total_amount)


@router.message(UserMissionState.total_amount)
async def total_amount_handler(message: Message, state: FSMContext):
    try:
        total_amount = int(message.text)
        await state.update_data(total_amount=total_amount)

        await message.answer('Введите сумму вашего дохода:')
        await state.set_state(UserMissionState.income)
    except ValueError:
        await message.answer('Сумму цели нужно указать числом')


@router.message(UserMissionState.income)
async def income_handler(message: Message, state: FSMContext):
    try:
        income = int(message.text)
        await state.update_data(income=income)

        await message.answer('Введите частоту вашего дохода:')
        await state.set_state(UserMissionState.income_frequency)
    except ValueError:
        await message.answer('Частоту дохода нужно указать числом')


@router.message(UserMissionState.income_frequency)
async def income_frequency_handler(message: Message, state: FSMContext):
    try:
        income_frequency = int(message.text,)
        await state.update_data(income_frequency=income_frequency)

        await message.answer('Введите период накопления в месяцах:')
        await state.set_state(UserMissionState.period_payments)
    except ValueError:
        await message.answer('Период накоплений нужно указать числом')


@router.message(UserMissionState.period_payments)
async def period_payments_handler(message: Message, state: FSMContext, session: AsyncSession):
    period_payments = int(message.text)
    await state.update_data(period_payments=period_payments)

    data = await state.get_data()
    if not all(key in data for key in ['goal', 'total_amount', 'income', 'income_frequency', 'period_payments']):
        await message.answer('Ошибка: Нехватает данных для сохранения цели')
        return

    user_id = message.from_user.id
    goal = data['goal']
    total_amount = data['total_amount']
    income = data['income']
    income_frequency = data['income_frequency']
    period_payments = data['period_payments']

    new_mission = Mission(user_id=user_id,
                          goal=goal,
                          total_amount=total_amount,
                          income=income,
                          income_frequency=income_frequency,
                          period_payments=period_payments
                          )

    try:
        session.add(new_mission)
        await session.commit()
        await message.answer('Ваша цель успешно сохранена')
    except Exception as e:
        await session.rollback()
        await message.answer(f'Произошла ошибка при сохранении цели: {str(e)}')
    finally:
        await state.clear()
