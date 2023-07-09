#!venv/bin/python

from aiogram.utils import executor

from create_bot import dp
from pathlib import Path
import data_base as db
import main_menu, chose_makeup, complicated_makeup, add_makeup, remove_makeup, support


def on_startup():
    db.sqlStart()

# do last
support.registerHandlers(dp)

# STARTING
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup())
