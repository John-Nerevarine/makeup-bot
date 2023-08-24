from aiogram import types
from aiogram.dispatcher import FSMContext
import keyboards as kb
from main_menu import getBackData
import data_base
from create_bot import bot, dp, AddMakeup, AddColour, Settings, MAKEUPS
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ADD MAKEUP
@dp.callback_query_handler(text='add_makeup', state=Settings.start)
async def callback_add_makeup(callback_query: types.CallbackQuery,
                              state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    keyboard = InlineKeyboardMarkup()
    for mk in MAKEUPS:
        keyboard.add(InlineKeyboardButton(f'Add {mk.capitalize()}', callback_data=mk))
    keyboard.add(InlineKeyboardButton('Add Colour Story', callback_data='colour_story'))
    keyboard.add(InlineKeyboardButton('Add Predefined Colour', callback_data='colour'))
    keyboard.add(kb.backButton)

    await bot.edit_message_text('<b>Add makeup</b>',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await AddMakeup.start.set()


# ENTER NAME
@dp.callback_query_handler(text=MAKEUPS, state=AddMakeup.start)
async def callback_adding_makeup(callback_query: types.CallbackQuery,
                                 state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    mk_type = callback_query.data

    m = await bot.edit_message_text(f'<b>New {mk_type.capitalize()}</b>\nEnter name:',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.cancelKeyboard)

    async with state.proxy() as data:
        data['mk_type'] = mk_type
        data['message_id'] = m.message_id

    await AddMakeup.enter_name.set()


# CHOOSE COLOURS
@dp.message_handler(state=AddMakeup.enter_name)
async def massage_enter_makeup_name(message: types.Message,
                                    state: FSMContext):
    if message.text:
        if '(' in message.text and ')' in message.text:
            collection = message.text[message.text.index('(') + 1:message.text.index(')')]
            name = message.text[:message.text.index('(')]
            if name[-1] == ' ':
                name = name[:-1]
        else:
            name = message.text
            collection = None
    else:
        name = "Unnamed"
        collection = None

    async with state.proxy() as data:
        mk_type = data['mk_type']
        data['name'] = name
        data['collection'] = collection
        message_id = data['message_id']
        data['colours_id'] = []
        data['colours_name'] = ''

    colours = data_base.get_colours(message.from_user.id)
    if colours:
        keyboard = InlineKeyboardMarkup()
        for colour in colours:
            cb_data = '|'.join((colour[0], str(colour[1])))
            keyboard.add(InlineKeyboardButton(colour[0], callback_data=cb_data))
        keyboard.add(kb.cancelButton)

        await bot.delete_message(message.from_user.id, message.message_id)
        await bot.edit_message_text(f'<b>New {mk_type.capitalize()}</b>\nName: {name}\nCollection: {collection}\nChoose colour:',
                                    message.from_user.id, message_id,
                                    reply_markup=keyboard)
        await AddMakeup.choose_colour.set()
    else:
        await bot.delete_message(message.from_user.id, message.message_id)
        await bot.edit_message_text(
            f'<b>There is no colours  in the data base! Please add any colour from "Add predefined colour"!</b>',
            message.from_user.id, message_id,
            reply_markup=kb.cancelKeyboard)


# CONFIRM MAKEUP
@dp.callback_query_handler(state=AddMakeup.choose_colour)
async def callback_colour_chosen(callback_query: types.CallbackQuery,
                                 state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        colours_name = data.get('colours_name')
        colours_id = data.get('colours_id')

    cb_data = callback_query.data.split('|')
    colours_id.append(int(cb_data[1]))
    colours_name = ', '.join((colours_name, cb_data[0])) if colours_name else cb_data[0]

    async with state.proxy() as data:
        mk_type = data['mk_type']
        name = data['name']
        collection = data['collection']
        data['colours_id'] = colours_id
        data['colours_name'] = colours_name

    text = '\n'.join((f'<b>New {mk_type}</b>',
                      f'Name: <i>{name}</i>',
                      f'Collection: <i>{collection}</i>',
                      f'Colours: <i>{colours_name}</i>'))

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Add More Colour', callback_data='add'))
    keyboard.add(kb.confirmButton)
    keyboard.add(kb.cancelButton)

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await AddMakeup.confirm.set()


# ADDITIONAL COLOUR
@dp.callback_query_handler(text='add', state=AddMakeup.confirm)
async def callback_colour_additional(callback_query: types.CallbackQuery,
                                     state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        mk_type = data['mk_type']
        name = data['name']
        collection = data['collection']
        colours_name = data['colours_name']

    text = '\n'.join((f'<b>New {mk_type}</b>',
                      f'Name: <i>{name}</i>',
                      f'Collection: <i>{collection}</i>',
                      f'Colours: <i>{colours_name}</i>'))

    colours = data_base.get_colours(callback_query.from_user.id)
    keyboard = InlineKeyboardMarkup()
    for colour in colours:
        cb_data = '|'.join((colour[0], str(colour[1])))
        keyboard.add(InlineKeyboardButton(colour[0], callback_data=cb_data))
    keyboard.add(kb.cancelButton)

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await AddMakeup.choose_colour.set()


# CONFIRMED MAKEUP
@dp.callback_query_handler(text='confirm', state=AddMakeup.confirm)
async def callback_confirm_makeup(callback_query: types.CallbackQuery,
                                  state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        mk_type = data['mk_type']
        name = data['name']
        collection = data['collection']
        colours_id = data['colours_id']
        data['colours_id'] = []
        colours_name = data['colours_name']

    data_base.add_element(user_id=callback_query.from_user.id,
                          name=name,
                          mk_type=mk_type,
                          colours=colours_id,
                          collection=collection)

    text = '\n'.join((f'<b>New {mk_type}</b>',
                      f'Name: <i>{name}</i>',
                      f'Collection: <i>{collection}</i>',
                      f'Colours: <i>{colours_name}</i>',
                      '\nAdded to database!'))

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.gotKeyboard)


# ADD COLOUR
@dp.callback_query_handler(text='colour', state=AddMakeup.start)
async def callback_adding_colour(callback_query: types.CallbackQuery,
                                 state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    m = await bot.edit_message_text(f'<b>New colour</b>\n\nEnter colour name:',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.cancelKeyboard)

    async with state.proxy() as data:
        data['message_id'] = m.message_id

    await AddColour.enter_name.set()


# COLOUR ADDED
@dp.message_handler(state=AddColour.enter_name)
async def callback_enter_colour_name(message: types.Message,
                                     state: FSMContext):
    name = message.text if message.text else "Unnamed"
    async with state.proxy() as data:
        message_id = data['message_id']

    data_base.add_colour(message.from_user.id, colour_name=name)

    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.edit_message_text(f'<b>New colour "<i>{name}"</i> added!</b>\n',
                                message.from_user.id, message_id,
                                reply_markup=kb.gotKeyboard)


# ADD COLOUR STORY
@dp.callback_query_handler(text='colour_story', state=AddMakeup.start)
async def callback_adding_colour_story(callback_query: types.CallbackQuery,
                                       state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    colours = data_base.get_colours(callback_query.from_user.id)
    if colours:
        async with state.proxy() as data:
            data['colours'] = colours
            data['new_colours'] = []

        keyboard = InlineKeyboardMarkup()
        for clr in colours:
            cb_data = '|'.join((clr[0], str(clr[1])))
            keyboard.add(InlineKeyboardButton(clr[0], callback_data=cb_data))
        keyboard.add(kb.backButton)

        await bot.edit_message_text(f'<b>Choose colour:</b>\n',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)

        await AddColour.choose_colour.set()
    else:
        await bot.edit_message_text(
            f'<b>There is no colours  in the data base! Please add any colour from "Add predefined colour"!</b>',
            callback_query.from_user.id, callback_query.message.message_id,
            reply_markup=kb.cancelKeyboard)


# CONFIRM COLOR STORY
@dp.callback_query_handler(state=[AddColour.choose_colour, AddColour.additional_colour])
async def callback_confirm_colour_story(callback_query: types.CallbackQuery,
                                        state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    cb_data = callback_query.data.split('|')
    cb_data[1] = int(cb_data[1])

    async with state.proxy() as data:
        new_colours = data['new_colours']
        new_colours.append(cb_data)
        data['new_colours'] = new_colours

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Add More Colour', callback_data='more_colour'))
    keyboard.add(kb.confirmButton)
    keyboard.add(kb.backButton)

    text = '/'.join(colour[0] for colour in new_colours)

    await bot.edit_message_text(f'<b>New colour story:</b>\n\n{text}.',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await AddColour.confirm.set()


# ADDITIONAL COLOUR
@dp.callback_query_handler(text='more_colour', state=AddColour.confirm)
async def callback_adding_more_in_colour_story(callback_query: types.CallbackQuery,
                                               state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    async with state.proxy() as data:
        colours = data['colours']

    keyboard = InlineKeyboardMarkup()
    for clr in colours:
        cb_data = '|'.join((clr[0], str(clr[1])))
        keyboard.add(InlineKeyboardButton(clr[0], callback_data=cb_data))
    keyboard.add(kb.backButton)

    await bot.edit_message_text(f'<b>Adding one more colour to colour story.</b>\n\nChoose colour:',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)

    await AddColour.additional_colour.set()


# CONFIRMED COLOUR STORY
@dp.callback_query_handler(text='confirm', state=AddColour.confirm)
async def callback_confirmed_colour_story(callback_query: types.CallbackQuery,
                                          state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    async with state.proxy() as data:
        new_colours = data['new_colours']
    data_base.add_colour_story(callback_query.from_user.id, new_colours)

    text = '/'.join(colour[0] for colour in new_colours)

    await bot.edit_message_text(f'<b>New colour story added:</b>\n\n{text}.',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.gotKeyboard)
