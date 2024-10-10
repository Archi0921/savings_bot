import asyncio
from bot.create_bot import main as start_bot
from database.database import init_db


async def main():
    await init_db()
    await start_bot()


if __name__ == '__main__':
    asyncio.run(main())
