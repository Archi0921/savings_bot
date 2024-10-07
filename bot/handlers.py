from aiogram import Router
from aiogram.filters import Command
from aiogram import types

router = Router()

def register_handlers(dp):
    dp.include_router(router)