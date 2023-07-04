from aiogram import types
from aiogram.dispatcher import FSMContext

import data_base
from support import callbackEmergencyStart
import keyboards as kb
import datetime
from create_bot import MainMenu, bot, dp, MAKEUPS, MAIN_MENU_MESSAGE
from config import USERS


# Start Command
@dp.message_handler(commands=['start'], state=['*', None])
async def commandStart(message: types.Message, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message_id)
    if message.from_user.id in USERS:
        m = await bot.send_message(message.from_user.id, MAIN_MENU_MESSAGE,
                                   reply_markup=kb.mMenuKeyboard)
        await state.finish()
        await MainMenu.start.set()
        async with state.proxy() as data:
            data['backStates'] = []
            data['backTexts'] = []
            data['backKeyboards'] = []
            data['message_id'] = m.message_id
    else:
        m = await bot.send_message(message.from_user.id, '<b>==Access denied==</b>')
        try:
            with open('unauthorized_access_log.txt', 'a') as file:
                file.write(f'{datetime.datetime.now()} | {message.from_user.id}' +
                           f' | {message.from_user.full_name} | {message.from_user.username}\n')
        finally:
            file.close()


# Return to main menu
@dp.callback_query_handler(text='main_menu', state=['*'])
async def callbackMainMenu(callback_query: types.CallbackQuery,
                           state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    m = await bot.edit_message_text(MAIN_MENU_MESSAGE,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.mMenuKeyboard)
    await state.finish()
    await MainMenu.start.set()
    async with state.proxy() as data:
        data['backStates'] = []
        data['backTexts'] = []
        data['backKeyboards'] = []
        data['message_id'] = m.message_id


# Save current data to go back
async def getBackData(state: FSMContext, message):
    async with state.proxy() as data:
        data['backStates'].append(await state.get_state())
        data['backTexts'].append(message.text)
        data['backKeyboards'].append(message.reply_markup)


# Go back
@dp.callback_query_handler(lambda c: c.data == 'back', state=['*'])
async def callbackGoBack(callback_query: types.CallbackQuery,
                         state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    if await state.get_state():
        async with state.proxy() as data:
            await bot.edit_message_text(data['backTexts'][-1],
                                        callback_query.from_user.id, callback_query.message.message_id,
                                        reply_markup=data['backKeyboards'][-1])
            if data['backStates'][-1] == 'MainMenu:start':
                await state.finish()
                await MainMenu.start.set()
                data['backStates'] = []
                data['backTexts'] = []
                data['backKeyboards'] = []
            else:
                await state.set_state(data['backStates'][-1])
                data['backStates'].pop(-1)
                data['backTexts'].pop(-1)
                data['backKeyboards'].pop(-1)
    else:
        await callbackEmergencyStart(callback_query, state)


# ELEMENTS MENU
@dp.callback_query_handler(text='show', state=MainMenu.start)
async def callback_show(callback_query: types.CallbackQuery,
                        state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    text = '<b>Elements in base:</b>'
    for makeup in MAKEUPS:
        elements = data_base.get_readable_elements(callback_query.from_user.id, makeup)
        text = '\n\n'.join((text, f'{makeup.capitalize()}{"es" if makeup[-1] == "s" else "s"}:'))
        if elements:
            for element in elements:
                text = '\n'.join((text, f'- "{element[0]}", colours: {element[1]}.'))
        else:
            text = '\n'.join((text, f'- No {makeup} in  database!'))

    text = '\n\n'.join((text, 'Colour stories:'))
    colour_stories = data_base.get_colour_stories(callback_query.from_user.id)
    if colour_stories:
        for cs in colour_stories:
            text = '\n'.join((text, f'- "{cs[0]}"'))
    else:
        text = '\n'.join((text, f'- No colour stories in database!'))

    text = '\n\n'.join((text, 'Colours:'))
    colours = data_base.get_colours(callback_query.from_user.id)
    if colours:
        colours = ', '.join(col[0] for col in colours)
        text = '\n'.join((text, f'- {colours}.'))
    else:
        text = '\n'.join((text, f'- No colours in database!'))

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)