from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

add_mission_button = KeyboardButton(text='🗒️ Добавить цель')
list_mission_button = KeyboardButton(text='💭 Посмотреть все цели')
delete_mission_button = KeyboardButton(text='❌ Удалить цель')
back_to_main_menu_button = KeyboardButton(text='🔙 Вернуться к основному меню')
stop_state_button = KeyboardButton(text='❌ Отменить действие')

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [add_mission_button, list_mission_button],
        [delete_mission_button]
    ],
    resize_keyboard=True,
    input_field_placeholder='Воспользуйся меню 👇'
)

list_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [list_mission_button, delete_mission_button],
        [back_to_main_menu_button]
    ],
    resize_keyboard=True,
    input_field_placeholder='Воспользуйся меню 👇'
)

stop_state_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[stop_state_button]])

def create_schedule_kb(payment_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Положил в копилку ", callback_data="saved_"+str(payment_id)))
    builder.row(InlineKeyboardButton(text="Перенести платёж \nи увеличить срок накопления", callback_data="repayment_"+str(payment_id)))
    builder.adjust(1)
    return builder.as_markup()

