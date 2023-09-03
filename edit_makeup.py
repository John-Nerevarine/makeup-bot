from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified
import keyboards as kb
import json
from main_menu import getBackData
import data_base
from create_bot import bot, dp, Edit, Settings, CollectionEdit, MAKEUPS
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
        elements_groups = []
        while len(elements) > 30:
            elements_groups.append(elements[:30])
            elements = elements[30:]
        else:
            elements_groups.append(elements)

        keyboard = InlineKeyboardMarkup()
        for el in elements_groups[0]:
            button_text = f'{el[0]} ({el[2]})'
            keyboard.add(InlineKeyboardButton(button_text, callback_data=str(el[1])))

        if len(elements_groups) > 1:
            keyboard.add(kb.nextButton)
        keyboard.add(kb.backButton)
        keyboard.add(kb.mMenuButton)

        async with state.proxy() as data:
            data['elements_groups'] = elements_groups
            data['group_index'] = 0
            data['mk_type'] = mk_type

        await Edit.chose_makeup.set()

    else:
        text = f'<b>NO {mk_type}</b> in the database!'
        keyboard = kb.cancelKeyboard

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)


# EDIT MENU / NEXT-PREV
@dp.callback_query_handler(state=Edit.chose_makeup)
async def callback_edit_menu(callback_query: types.CallbackQuery,
                             state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    # Show next
    if callback_query.data == 'next':
        async with state.proxy() as data:
            elements_groups = data['elements_groups']
            group_index = data['group_index']
            mk_type = data['mk_type']
        if len(elements_groups) > group_index + 1:
            group_index += 1
            keyboard = InlineKeyboardMarkup()
            for el in elements_groups[group_index]:
                button_text = f'{el[0]} ({el[2]})'
                keyboard.add(InlineKeyboardButton(button_text, callback_data=str(el[1])))

            keyboard.add(kb.prevButton)
            if len(elements_groups) > group_index + 1:
                keyboard.insert(kb.nextButton)
            keyboard.add(kb.backButton)
            keyboard.add(kb.mMenuButton)

            text = f'<b>Choose {mk_type}</b>:\nPage {group_index + 1}'

            async with state.proxy() as data:
                data['group_index'] = group_index
        else:
            text = 'No next data. It\'s an error. Send nudes to the developer!'
            keyboard = kb.cancelKeyboard

        await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
        return
    # Show previous
    elif callback_query.data == 'prev':
        async with state.proxy() as data:
            elements_groups = data['elements_groups']
            group_index = data['group_index']
            mk_type = data['mk_type']
        if group_index - 1 >= 0:
            group_index -= 1
            keyboard = InlineKeyboardMarkup()
            for el in elements_groups[group_index]:
                button_text = f'{el[0]} ({el[2]})'
                keyboard.add(InlineKeyboardButton(button_text, callback_data=str(el[1])))

            if group_index - 1 >= 0:
                keyboard.add(kb.prevButton)
                keyboard.insert(kb.nextButton)
            else:
                keyboard.add(kb.nextButton)
            keyboard.add(kb.backButton)
            keyboard.add(kb.mMenuButton)

            text = f'<b>Choose {mk_type}</b>:\nPage {group_index + 1}'

            async with state.proxy() as data:
                data['group_index'] = group_index
        else:
            text = 'No prev data. It\'s an error. Send nudes to the developer!'
            keyboard = kb.cancelKeyboard

        await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
        return
    mk_id = int(callback_query.data)
    makeup = data_base.get_one_element(callback_query.from_user.id, mk_id)
    text = f'{makeup["type"].capitalize()} <b>"{makeup["name"]} ({makeup["collection"]})"</b>,\
 Colours: {makeup["colours"]}, Priority: {makeup["priority"]}'

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

    if makeup['collection']:
        text = f'Enter new name for <b>"{makeup["name"]} ({makeup["collection"]}):"</b>'
    else:
        text = f'Enter new name for <b>"{makeup["name"]}:"</b>'

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
        data['makeup']['name'] = name
        data['makeup']['collection'] = collection
        makeup = data['makeup']
        message_id = data['message_id']
        data['backStates'].pop(-1)
        data['backTexts'].pop(-1)
        data['backKeyboards'].pop(-1)

    data_base.edit(makeup['id'], 'name', name)
    data_base.edit(makeup['id'], 'collection', collection)

    if makeup['collection']:
        text = '\n\n'.join((f'<b>Name changed!</b>',
                            f'{makeup["type"].capitalize()} <b>"{makeup["name"]} ({makeup["collection"]})"</b>,\
 Colours: {makeup["colours"]}, Priority: {makeup["priority"]}'))
    else:
        text = '\n\n'.join((f'<b>Name changed!</b>',
                            f'{makeup["type"].capitalize()} <b>"{makeup["name"]}"</b>,\
 Colours: {makeup["colours"]}, Priority: {makeup["priority"]}'))

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

        if makeup['collection']:
            text = f'Choose new colour for <b>"{makeup["name"]} ({makeup["collection"]})"</b>:'
        else:
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

    if makeup['collection']:
        text = '\n\n'.join((f'{makeup["type"]} <b>"{makeup["name"]} ({makeup["collection"]})"</b>',
                            f'New colours: <i>{colours_name}</i>'))
    else:
        text = '\n\n'.join((f'{makeup["type"]} <b>"{makeup["name"]}"</b>',
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

    if makeup['collection']:
        text = '\n\n'.join((f'{makeup["type"]} <b>"{makeup["name"]} ({makeup["collection"]})"</b>',
                            f'New colours: <i>{colours_name}</i>\nChoose colour to add:'))
    else:
        text = '\n\n'.join((f'{makeup["type"]} <b>"{makeup["name"]}"</b>',
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

    if makeup['collection']:
        text = '\n\n'.join((f'<b>Colours changed!</b>',
                            f'{makeup["type"].capitalize()} <b>"{makeup["name"]} ({makeup["collection"]})"</b>,\
 Colours: {makeup["colours"]}, Priority: {makeup["priority"]}'))
    else:
        text = '\n\n'.join((f'<b>Colours changed!</b>',
                            f'{makeup["type"].capitalize()} <b>"{makeup["name"]}"</b>,\
 Colours: {makeup["colours"]}, Priority: {makeup["priority"]}'))

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.editKeyboard)
    await Edit.edit.set()


# ENTER PRIORITY
@dp.callback_query_handler(text='edit_priority', state=Edit.edit)
async def callback_edit_priority(callback_query: types.CallbackQuery,
                                 state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    async with state.proxy() as data:
        makeup = data['makeup']

    if makeup['collection']:
        text = f'Enter new priority for <b>"{makeup["name"]} ({makeup["collection"]}):"</b>'
    else:
        text = f'Enter new priority for <b>"{makeup["name"]}:"</b>'

    m = await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.cancelKeyboard)

    async with state.proxy() as data:
        data['message_id'] = m.message_id

    await Edit.enter_priority.set()


# PRIORITY CHANGED
@dp.message_handler(state=Edit.enter_priority)
async def massage_edit_name(message: types.Message,
                            state: FSMContext):
    if message.text.isdigit() and 0 <= int(message.text) <= 10:
        priority = int(message.text)
    else:
        async with state.proxy() as data:
            makeup = data['makeup']
            message_id = data['message_id']
        if makeup['collection']:
            text = '\n'.join((f'Enter new priority for <b>"{makeup["name"]} ({makeup["collection"]}):"</b>',
                              'Enter number between 0 and 10!',))
        else:
            text = '\n'.join((f'Enter new priority for <b>"{makeup["name"]}:"</b>',
                              'Enter number between 0 and 10!',))

        await bot.delete_message(message.from_user.id, message.message_id)
        try:
            await bot.edit_message_text(text,
                                        message.from_user.id, message_id,
                                        reply_markup=kb.cancelKeyboard)
        except MessageNotModified:
            text += '!'
            await bot.edit_message_text(text,
                                        message.from_user.id, message_id,
                                        reply_markup=kb.cancelKeyboard)
        return

    async with state.proxy() as data:
        data['makeup']['priority'] = priority
        makeup = data['makeup']
        message_id = data['message_id']
        data['backStates'].pop(-1)
        data['backTexts'].pop(-1)
        data['backKeyboards'].pop(-1)

    data_base.edit(makeup['id'], 'priority', priority)

    if makeup['collection']:
        text = '\n\n'.join((f'<b>Priority changed!</b>',
                            f'{makeup["type"].capitalize()} <b>"{makeup["name"]} ({makeup["collection"]})"</b>,\
 Colours: {makeup["colours"]}, Priority: {makeup["priority"]}'))
    else:
        text = '\n\n'.join((f'<b>Priority changed!</b>',
                            f'{makeup["type"].capitalize()} <b>"{makeup["name"]}"</b>,\
 Colours: {makeup["colours"]}, Priority: {makeup["priority"]}'))

    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.edit_message_text(text,
                                message.from_user.id, message_id,
                                reply_markup=kb.editKeyboard)

    await Edit.edit.set()


# CHOOSE COLLECTION
@dp.callback_query_handler(text='edit_palette', state=Settings.start)
async def callback_edit_palette_choose(callback_query: types.CallbackQuery,
                                      state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    collections = data_base.get_palettes(callback_query.from_user.id)

    if collections:
        text = f'<b>Choose Palette</b>:'
        palettes_groups = []
        while len(collections) > 30:
            palettes_groups.append(collections[:30])
            collections = collections[30:]
        else:
            palettes_groups.append(collections)

        keyboard = InlineKeyboardMarkup()
        for palette in palettes_groups[0]:
            if palette[0]:
                keyboard.add(InlineKeyboardButton(palette[0], callback_data=palette[0]))

        if len(palettes_groups) > 1:
            keyboard.add(kb.nextButton)
        keyboard.add(kb.backButton)
        keyboard.add(kb.mMenuButton)

        async with state.proxy() as data:
            data['palettes_groups'] = palettes_groups
            data['group_index'] = 0

        await CollectionEdit.start.set()

    else:
        text = f'<b>NO Palettes</b> in the database!'
        keyboard = kb.cancelKeyboard

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)


# ENTER PRIORITY / NEXT-PREV
@dp.callback_query_handler(state=CollectionEdit.start)
async def callback_edit_palette_enter_priority(callback_query: types.CallbackQuery,
                                              state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    # Show next
    if callback_query.data == 'next':
        async with state.proxy() as data:
            palettes_groups = data['palettes_groups']
            group_index = data['group_index']
        if len(palettes_groups) > group_index + 1:
            group_index += 1

            keyboard = InlineKeyboardMarkup()
            for palette in palettes_groups[group_index]:
                if palette[0]:
                    keyboard.add(InlineKeyboardButton(palette[0], callback_data=palette[0]))

            keyboard.add(kb.prevButton)
            if len(palettes_groups) > group_index + 1:
                keyboard.insert(kb.nextButton)
            keyboard.add(kb.backButton)
            keyboard.add(kb.mMenuButton)

            text = f'<b>Choose Palette</b>:\nPage {group_index + 1}'

            async with state.proxy() as data:
                data['group_index'] = group_index
        else:
            text = 'No next data. It\'s an error. Send nudes to the developer!'
            keyboard = kb.cancelKeyboard

        await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
        return
    # Show previous
    elif callback_query.data == 'prev':
        async with state.proxy() as data:
            palettes_groups = data['palettes_groups']
            group_index = data['group_index']
        if group_index - 1 >= 0:
            group_index -= 1
            keyboard = InlineKeyboardMarkup()
            for palette in palettes_groups[group_index]:
                keyboard.add(InlineKeyboardButton(palette[0], callback_data=palette[0]))

            if group_index - 1 >= 0:
                keyboard.add(kb.prevButton)
                keyboard.insert(kb.nextButton)
            else:
                keyboard.add(kb.nextButton)
            keyboard.add(kb.backButton)
            keyboard.add(kb.mMenuButton)

            text = f'<b>Choose Palette</b>:\nPage {group_index + 1}'

            async with state.proxy() as data:
                data['group_index'] = group_index
        else:
            text = 'No prev data. It\'s an error. Send nudes to the developer!'
            keyboard = kb.cancelKeyboard

        await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
        return
    palette = callback_query.data
    text = f'Enter new priority for <b>{palette}</b>:'

    m = await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.backKeyboard)

    async with state.proxy() as data:
        data['palette'] = palette
        data['message_id'] = m.message_id

    await CollectionEdit.enter_priority.set()


# COLLECTION PRIORITY CHANGED
@dp.message_handler(state=CollectionEdit.enter_priority)
async def massage_collection_edit_priority(message: types.Message,
                                           state: FSMContext):
    if message.text.isdigit() and 0 <= int(message.text) <= 10:
        priority = int(message.text)
    else:
        async with state.proxy() as data:
            palette = data['palette']
            message_id = data['message_id']

        text = '\n'.join((f'Enter new priority for <b>"{palette}:"</b>',
                          'Enter number between 0 and 10!',))

        await bot.delete_message(message.from_user.id, message.message_id)
        try:
            await bot.edit_message_text(text,
                                        message.from_user.id, message_id,
                                        reply_markup=kb.cancelKeyboard)
        except MessageNotModified:
            text += '!'
            await bot.edit_message_text(text,
                                        message.from_user.id, message_id,
                                        reply_markup=kb.cancelKeyboard)
        return

    async with state.proxy() as data:
        palette = data['palette']
        message_id = data['message_id']

    data_base.change_palette_priority(message.from_user.id, palette, priority)

    text = f'Priority for <b>{palette}</b> changed to <b>{priority}</b>!'

    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.edit_message_text(text,
                                message.from_user.id, message_id,
                                reply_markup=kb.backKeyboard)
