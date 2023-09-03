from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import TOKEN

storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

MAKEUPS = ('eyeshadow', 'eyeliner', 'lipstick', 'lipliner', 'lipgloss', 'highlighter', 'blush')
MAKEUPS_WO_LIPS = ('eyeshadow', 'eyeliner', 'highlighter', 'blush')
MAIN_MENU_MESSAGE = '<b>Lizz Makeup Bot</b>\n\n== Main Menu =='


class MainMenu(StatesGroup):
    start = State()
    elements = State()


class AdditionalParameters(StatesGroup):
    eyeshadow = State()
    eyeliner = State()


class AddMakeup(StatesGroup):
    start = State()
    enter_name = State()
    choose_colour = State()
    additional_colour = State()
    confirm = State()


class AddColour(StatesGroup):
    enter_name = State()
    add_colour_story = State()
    choose_colour = State()
    additional_colour = State()
    confirm = State()


class RemoveMakeup(StatesGroup):
    start = State()
    makeup = State()
    colour_story = State()
    colour = State()


class ColourStory(StatesGroup):
    start = State()
    choose_cs = State()


class Settings(StatesGroup):
    start = State()
    show = State()


class Find(StatesGroup):
    start = State()
    type_name = State()
    result = State()


class Edit(StatesGroup):
    start = State()
    chose_makeup = State()
    edit = State()
    enter_name = State()
    enter_priority = State()
    colours = State()
    confirm_colours = State()
    additional_colour = State()
    type = State()
    priority = State()


class Image(StatesGroup):
    show_image = State()
    send = State()
    enter_name = State()
    delete = State()


class CollectionEdit(StatesGroup):
    start = State()
    enter_priority = State()