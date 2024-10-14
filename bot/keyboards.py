from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

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