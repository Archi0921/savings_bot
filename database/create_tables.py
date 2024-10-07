import os
import sqlite3
import logging

logger = logging.getLogger(__name__)

db_file_path = os.path.join(os.path.dirname(__file__), 'database', 'bot.db')
conn = sqlite3.connect(db_file_path)

if not os.path.exists(db_file_path):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    with open(os.path.join(os.path.dirname(__file__), 'db_script.sql'), 'r') as f:
        sql_script = f.read()

    cursor.executescript(sql_script)
    logger.info('Таблицы успешно созданы.')

    conn.close()
