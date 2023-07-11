from aiogram import types
from aiogram.dispatcher import FSMContext
import keyboards as kb
import json
from main_menu import getBackData
import data_base
from create_bot import bot, dp, Find, Edit, Settings, MAKEUPS
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# CHOOSE TYPE
@dp.callback_query_handler(text='edit', state=Settings.start)
async def callback_edit_choose_type(callback_query: types.CallbackQuery,
                                    state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    keyboard = InlineKeyboardMarkup()

    for mk in MAKEUPS:
        keyboard.add(InlineKeyboardButton(f'{mk.capitalize()}', callback_data=mk))
    keyboard.add(kb.backButton)

    await bot.edit_message_text('<b>Choose makeup type to edit:</b>',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await Edit.start.set()


# CHOOSE NAME
@dp.callback_query_handler(text=MAKEUPS, state=Edit.start)
async def callback_edit_choose_name(callback_query: types.CallbackQuery,
                                    state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    mk_type = callback_query.data

    elements = data_base.get_elements(callback_query.from_user.id, mk_type)
    if elements:
        text = f'<b>Choose {mk_type}</b>:'
        keyboard = InlineKeyboardMarkup()
        for el in elements:
            keyboard.add(InlineKeyboardButton(el[0], callback_data=str(el[1])))
        keyboard.add(kb.backButton)
        keyboard.add(kb.mMenuButton)
    else:
        text = f'<b>NO {mk_type}</b> in the database!'
        keyboard = kb.backKeyboard
        keyboard.add(kb.mMenuButton)

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await Edit.chose_makeup.set()


# EDIT MENU
@dp.callback_query_handler(state=Edit.chose_makeup)
async def callback_edit_menu(callback_query: types.CallbackQuery,
                             state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    mk_id = int(callback_query.data)
    makeup = data_base.get_one_element(callback_query.from_user.id, mk_id)
    text = f'<b>{makeup["type"].capitalize()}</b> "{makeup["name"]}". Colours: {makeup["colours"]}'

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.editKeyboard)

    async with state.proxy() as data:
        data['makeup'] = makeup

    await Edit.edit.set()


# ENTER NAME
@dp.callback_query_handler(text='edit_name', state=Edit.edit)
async def callback_edit_name(callback_query: types.CallbackQuery,
                             state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    async with state.proxy() as data:
        makeup = data['makeup']

    text = f'Enter new name for "{makeup["name"]}:"'

    m = await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.cancelKeyboard)

    async with state.proxy() as data:
        data['message_id'] = m.message_id

    await Edit.enter_name.set()


# NAME CHANGED
@dp.message_handler(state=Edit.enter_name)
async def massage_edit_name(message: types.Message,
                            state: FSMContext):
    name = message.text if message.text else "Unnamed"
    async with state.proxy() as data:
        data['makeup']['name'] = name
        makeup = data['makeup']
        message_id = data['message_id']
        data['backStates'].pop(-1)
        data['backTexts'].pop(-1)
        data['backKeyboards'].pop(-1)

    data_base.edit(makeup['id'], 'name', name)

    text = '\n\n'.join((f'<b>Name changed!</b>',
                        f'<b>{makeup["type"].capitalize()} "{makeup["name"]}". Colours: {makeup["colours"]}</b>'))

    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.edit_message_text(text,
                                message.from_user.id, message_id,
                                reply_markup=kb.editKeyboard)

    await Edit.edit.set()


# CHOOSE COLOURS
@dp.callback_query_handler(text='edit_colours', state=Edit.edit)
async def callback_edit_colours(callback_query: types.CallbackQuery,
                                state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    colours = data_base.get_colours(callback_query.from_user.id)

    async with state.proxy() as data:
        makeup = data['makeup']
        data['colours'] = colours
        data['colours_id'] = []
        data['colours_name'] = ''

    if colours:
        keyboard = InlineKeyboardMarkup()
        for colour in colours:
            cb_data = '|'.join((colour[0], str(colour[1])))
            keyboard.add(InlineKeyboardButton(colour[0], callback_data=cb_data))
        keyboard.add(kb.cancelButton)

        text = f'Choose new colour for <b>"{makeup["name"]}"</b>:'
        await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
        await Edit.colours.set()
    else:
        await bot.edit_message_text(
            f'<b>There is no colours  in the data base! Please add any colour from "Add predefined colour"!</b>',
            callback_query.from_user.id, callback_query.message.message_id,
            reply_markup=kb.cancelKeyboard)


# CONFIRM COLOURS
@dp.callback_query_handler(state=Edit.colours)
async def callback_edit_confirm_colours(callback_query: types.CallbackQuery,
                                        state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        colours_name = data.get('colours_name')
        colours_id = data.get('colours_id')

    cb_data = callback_query.data.split('|')
    colours_id.append(int(cb_data[1]))
    colours_name = ', '.join((colours_name, cb_data[0])) if colours_name else cb_data[0]

    async with state.proxy() as data:
        makeup = data['makeup']
        data['colours_id'] = colours_id
        data['colours_name'] = colours_name

    text = '\n\n'.join((f'{makeup["type"]} "{makeup["name"]}"',
                        f'New colours: <i>{colours_name}</i>'))

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Add More Colour', callback_data='add'))
    keyboard.add(kb.confirmButton)
    keyboard.add(kb.cancelButton)

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await Edit.confirm_colours.set()


# ADDITIONAL COLOUR
@dp.callback_query_handler(text='add', state=Edit.confirm_colours)
async def callback_edit_colour_additional(callback_query: types.CallbackQuery,
                                     state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        makeup = data['makeup']
        colours = data['colours']
        colours_name = data['colours_name']

    text = '\n\n'.join((f'{makeup["type"]} "{makeup["name"]}"',
                        f'New colours: <i>{colours_name}</i>\nChoose colour to add:'))

    keyboard = InlineKeyboardMarkup()
    for colour in colours:
        cb_data = '|'.join((colour[0], str(colour[1])))
        keyboard.add(InlineKeyboardButton(colour[0], callback_data=cb_data))
    keyboard.add(kb.cancelButton)

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await Edit.colours.set()


# CONFIRMED COLOURS
@dp.callback_query_handler(text='confirm', state=Edit.confirm_colours)
async def callback_confirmed_colours(callback_query: types.CallbackQuery,
                                 state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['makeup']['colours'] = data['colours_name']
        makeup = data['makeup']
        colours_id = data['colours_id']
        data['colours_id'] = []
        data['backStates'].pop(-1)
        data['backTexts'].pop(-1)
        data['backKeyboards'].pop(-1)

    colours_id = json.dumps(colours_id)
    data_base.edit(makeup['id'], 'colours', colours_id)

    text = '\n\n'.join((f'<b>Colours changed!</b>',
                        f'<b>{makeup["type"].capitalize()} "{makeup["name"]}". Colours: {makeup["colours"]}</b>'))

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.editKeyboard)
    await Edit.edit.set()
