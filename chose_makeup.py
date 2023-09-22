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
    eyeshadows_raw = data_base.get_elements(callback_query.from_user.id, 'eyeshadow', amount=amount)
    eyeshadows = [f'{element[0]} ({element[2]})' if element[2] else element[0]
                  for element in eyeshadows_raw]
    if not eyeshadows:
        text = f'There is no eyeshadows in database!'
    elif len(eyeshadows) < amount:
        items = ', '.join([i for i in eyeshadows])
        text = f'Not enough eyeshadows in database! Got all of them:\n<b>{items}</b>.'
    else:
        items = ', '.join([i for i in eyeshadows])
        text = f'Eyeshadows to use:\n\n<b>{items}</b>.'

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
    eyeliners_raw = data_base.get_elements(callback_query.from_user.id, 'eyeliner', amount=amount)
    eyeliners = [f'{element[0]} ({element[2]})' if element[2] else element[0]
                 for element in eyeliners_raw]
    if not eyeliners:
        text = f'There is no eyeliners in database!'
    elif len(eyeliners) < amount:
        items = ', '.join([i for i in eyeliners])
        text = f'Not enough eyeliners in database! Got all of them:\n<b>{items}</b>.'
    else:
        items = ', '.join([i for i in eyeliners])
        text = f'Eyeliners to use:\n\n<b>{items}</b>.'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


# LIPSTICKS
@dp.callback_query_handler(text='lipstick', state=MainMenu.elements)
async def callback_lipsticks(callback_query: types.CallbackQuery,
                             state: FSMContext):
    await getBackData(state, callback_query.message)
    lipsticks = [f'{element[0]} ({element[2]})' if element[2] else element[0]
                 for element in data_base.get_elements(callback_query.from_user.id, 'lipstick', amount=1)]
    if not lipsticks:
        text = f'There is no lipsticks in data base!'
    else:
        item = str(lipsticks[0])
        text = f'Lipstick to use:\n\n<b>{item}</b>.'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


# LIPSLINERS
@dp.callback_query_handler(text='lipliner', state=MainMenu.elements)
async def callback_lipliner(callback_query: types.CallbackQuery,
                            state: FSMContext):
    await getBackData(state, callback_query.message)
    lipliners = [f'{element[0]} ({element[2]})' if element[2] else element[0]
                 for element in data_base.get_elements(callback_query.from_user.id, 'lipliner', amount=1)]
    if lipliners:
        item = str(lipliners[0])
        text = f'Lipliner to use:\n\n<b>{item}</b>.'
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
    lipglosses = [f'{element[0]} ({element[2]})' if element[2] else element[0]
                  for element in data_base.get_elements(callback_query.from_user.id, 'lipgloss', amount=1)]
    if lipglosses:
        item = str(lipglosses[0])
        text = f'Lipgloss to use:\n\n<b>{item}</b>.'
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

    glitters = [f'{element[0]} ({element[2]})' if element[2] else element[0]
                for element in data_base.get_elements(callback_query.from_user.id, 'glitter', amount=1)]
    if glitters:
        item = str(glitters[0])
        text = f'Glitter to use:\n\n<b>{item}</b>.'
    else:
        text = f'No Glitters in Database!'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


# HIGHLIGHTER
@dp.callback_query_handler(text='highlighter', state=MainMenu.elements)
async def callback_highlighter(callback_query: types.CallbackQuery,
                               state: FSMContext):
    await getBackData(state, callback_query.message)
    highlighters = [f'{element[0]} ({element[2]})' if element[2] else element[0]
                    for element in data_base.get_elements(callback_query.from_user.id, 'highlighter', amount=1)]
    if not highlighters:
        text = f'There is no highlighters in data base!'
    else:
        item = str(highlighters[0])
        text = f'Highlighter to use:\n\n<b>{item}</b>.'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


# BLUSH
@dp.callback_query_handler(text='blush', state=MainMenu.elements)
async def callback_blush(callback_query: types.CallbackQuery,
                         state: FSMContext):
    await getBackData(state, callback_query.message)
    blushes = [f'{element[0]} ({element[2]})' if element[2] else element[0]
               for element in data_base.get_elements(callback_query.from_user.id, 'blush', amount=1)]
    if not blushes:
        text = f'There is no blushes in data base!'
    else:
        item = str(blushes[0])
        text = f'Blush to use:\n\n<b>{item}</b>.'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)


# MASCARA
@dp.callback_query_handler(text='mascara', state=MainMenu.elements)
async def callback_mascara(callback_query: types.CallbackQuery,
                           state: FSMContext):
    await getBackData(state, callback_query.message)
    mascaras = [f'{element[0]} ({element[2]})' if element[2] else element[0]
                for element in data_base.get_elements(callback_query.from_user.id, 'mascara', amount=1)]
    if mascaras:
        item = str(mascaras[0])
        text = f'Mascara to use:\n\n<b>{item}</b>.'
    else:
        text = f'No Mascaras in Database!'

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)
