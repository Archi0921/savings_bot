import os
import sqlite3
import logging

logger = logging.getLogger(__name__)

db_file_path = os.path.join(os.path.dirname(__file__), '', 'bot.db')

if not os.path.exists(db_file_path):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    with open(os.path.join(os.path.dirname(__file__), 'db_script.sql'), 'r') as f:
        sql_script = f.read()

    cursor.executescript(sql_script)
    conn.close()
    logger.info('Таблицы успешно созданы.')
else:
    logger.info('Таблицы уже существуют.')