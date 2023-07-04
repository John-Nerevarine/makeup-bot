from aiogram import types
from aiogram.dispatcher import FSMContext
import keyboards as kb
from main_menu import getBackData
import data_base
from create_bot import bot, dp, AdditionalParameters, MainMenu
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from random import randint, choice


# ELEMENTS MENU
@dp.callback_query_handler(text='elements', state=MainMenu.start)
async def callback_choose_elements(callback_query: types.CallbackQuery,
                                   state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    await bot.edit_message_text('<b>Choose element:</b>',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.randomElementsKeyboard)

    await MainMenu.elements.set()


# EYESHADOWS
@dp.callback_query_handler(text='eyeshadow', state=MainMenu.elements)
async def callback_choose_eyeshadow(callback_query: types.CallbackQuery,
                                    state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('1', callback_data='1'))
    keyboard.insert(InlineKeyboardButton('2', callback_data='2'))
    keyboard.insert(InlineKeyboardButton('3', callback_data='3'))
    keyboard.add(kb.backButton)

    await bot.edit_message_text('<b>Eyeshadow</b>\n\nChoose amount:',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)

    await AdditionalParameters.eyeshadow.set()


@dp.callback_query_handler(text=['1', '2', '3'], state=AdditionalParameters.eyeshadow)
async def callback_amount_eyeshadow(callback_query: types.CallbackQuery,
                                    state: FSMContext):
    amount = int(callback_query.data)
    eyeshadows = [element[0] for element in data_base.get_elements(callback_query.from_user.id, 'eyeshadow')]
    if not eyeshadows:
        text = f'There is no eyeshadows in database!'
    elif len(eyeshadows) < amount:
        items = ', '.join([i for i in eyeshadows])
        text = f'Not enough eyeshadows in database! Got all of them:\n<b>{items}</b>.'
    else:
        items = ''
        for i in range(amount):
            curr_item = choice(eyeshadows)
            eyeshadows.remove(curr_item)
            items = ', '.join((items, curr_item)) if items else curr_item
        text = f'Eyeshadows to use:\n<b>{items}</b>.'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


# EYELINERS
@dp.callback_query_handler(text='eyeliner', state=MainMenu.elements)
async def callback_choose_eyeliner(callback_query: types.CallbackQuery,
                                   state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('Black', callback_data='black'))
    keyboard.insert(InlineKeyboardButton('Colourful', callback_data='colour'))
    keyboard.add(kb.backButton)

    await bot.edit_message_text('<b>Eyeliner</b>\n\nChoose colour:',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)

    await AdditionalParameters.eyeliner.set()


@dp.callback_query_handler(text='black', state=AdditionalParameters.eyeliner)
async def callback_choose_black_eyeliner(callback_query: types.CallbackQuery,
                                         state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    decision = bool(randint(0, 1))
    text = '<b>USE</b> black eyeliner.' if decision else 'Use <b>NO</b> eyeliner.'

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


@dp.callback_query_handler(text='colour', state=AdditionalParameters.eyeliner)
async def callback_choose_colour_eyeliner(callback_query: types.CallbackQuery,
                                          state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('1', callback_data='1'))
    keyboard.insert(InlineKeyboardButton('2', callback_data='2'))
    keyboard.insert(InlineKeyboardButton('3', callback_data='3'))
    keyboard.add(kb.backButton)

    await bot.edit_message_text('<b>Eyeliner</b>\n\nChoose amount:',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)


@dp.callback_query_handler(text=['1', '2', '3'], state=AdditionalParameters.eyeliner)
async def callback_amount_eyeliner(callback_query: types.CallbackQuery,
                                   state: FSMContext):
    amount = int(callback_query.data)
    eyeliners = [element[0] for element in data_base.get_elements(callback_query.from_user.id, 'eyeliner')]
    if not eyeliners:
        text = f'There is no eyeliners in database!'
    elif len(eyeliners) < amount:
        items = ', '.join([i for i in eyeliners])
        text = f'Not enough eyeliners in database! Got all of them:\n<b>{items}</b>.'
    else:
        items = ''
        for i in range(amount):
            curr_item = choice(eyeliners)
            eyeliners.remove(curr_item)
            items = ', '.join((items, curr_item)) if items else curr_item
        text = f'Eyeliners to use:\n<b>{items}</b>.'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


# LIPSTICKS
@dp.callback_query_handler(text='lipstick', state=MainMenu.elements)
async def callback_eyeliner(callback_query: types.CallbackQuery,
                            state: FSMContext):
    await getBackData(state, callback_query.message)
    lipsticks = [element[0] for element in data_base.get_elements(callback_query.from_user.id, 'lipstick')]
    if not lipsticks:
        text = f'There is no lipsticks in data base!'
    elif lipsticks:
        item = str(choice(lipsticks))
        text = f'Lipstick to use:\n<b>{item}</b>.'
    else:
        text = f'No lipsticks in Database!'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


# LIPSLINERS
@dp.callback_query_handler(text='lipliner', state=MainMenu.elements)
async def callback_lipliner(callback_query: types.CallbackQuery,
                            state: FSMContext):
    await getBackData(state, callback_query.message)
    lipliners = [element[0] for element in data_base.get_elements(callback_query.from_user.id, 'lipliner')]
    if lipliners:
        item = str(choice(lipliners))
        text = f'Lipliner to use:\n<b>{item}</b>.'
    else:
        text = f'No lipliners in Database!'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


# LIPGLOSSES
@dp.callback_query_handler(text='lipgloss', state=MainMenu.elements)
async def callback_lipgloss(callback_query: types.CallbackQuery,
                            state: FSMContext):
    await getBackData(state, callback_query.message)
    lipglosses = [element[0] for element in data_base.get_elements(callback_query.from_user.id, 'lipgloss')]
    if lipglosses:
        item = str(choice(lipglosses))
        text = f'Lipgloss to use:\n<b>{item}</b>.'
    else:
        text = f'No lipglosses in Database!'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


# GLITTER
@dp.callback_query_handler(text='glitter', state=MainMenu.elements)
async def callback_glitter(callback_query: types.CallbackQuery,
                           state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    decision = bool(randint(0, 1))
    text = '<b>USE</b> glitter.' if decision else 'Use <b>NO</b> glitter.'

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)