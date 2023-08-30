from aiogram import types
from aiogram.dispatcher import FSMContext
import keyboards as kb
from main_menu import getBackData
import data_base
from create_bot import bot, dp, RemoveMakeup, Settings, MAKEUPS
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# START REMOVING MAKEUP
@dp.callback_query_handler(text='remove_makeup', state=Settings.start)
async def callback_start_removing_makeup(callback_query: types.CallbackQuery,
                                         state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    keyboard = InlineKeyboardMarkup()
    for mk in MAKEUPS:
        keyboard.add(InlineKeyboardButton(f'Remove {mk}', callback_data=mk))
    keyboard.add(InlineKeyboardButton('Remove colour story', callback_data='colour_story'))
    keyboard.add(InlineKeyboardButton('Remove predefined colour', callback_data='colour'))
    keyboard.add(kb.backButton)

    await bot.edit_message_text('<b>Remove makeup</b>',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await RemoveMakeup.start.set()


# REMOVE MAKEUP
@dp.callback_query_handler(text=MAKEUPS, state=RemoveMakeup.start)
async def callback_remove_makeup(callback_query: types.CallbackQuery,
                                 state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    mk_type = callback_query.data
    elements = data_base.get_elements(callback_query.from_user.id, mk_type)

    if elements:
        text = f'<b>Choose {mk_type} to remove</b>:'
        elements_groups = []
        while len(elements) > 30:
            elements_groups.append(elements[:30])
            elements = elements[30:]
        else:
            elements_groups.append(elements)

        keyboard = InlineKeyboardMarkup()
        for el in elements_groups[0]:
            button_text = f'{el[0]} ({el[2]})'
            cb_data = '|'.join((el[0], str(el[1]), el[2]))
            keyboard.add(InlineKeyboardButton(button_text, callback_data=cb_data))

        if len(elements_groups) > 1:
            keyboard.add(kb.nextButton)
        keyboard.add(kb.backButton)
        keyboard.add(kb.mMenuButton)

        async with state.proxy() as data:
            data['elements_groups'] = elements_groups
            data['group_index'] = 0
            data['mk_type'] = mk_type

        await RemoveMakeup.makeup.set()

    else:
        text = f'<b>NO {mk_type}</b> in the database!'
        keyboard = kb.cancelKeyboard

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)


# REMOVE MAKEUP DONE
@dp.callback_query_handler(state=RemoveMakeup.makeup)
async def callback_removed_makeup(callback_query: types.CallbackQuery,
                                  state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    cb_data = callback_query.data.split('|')

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
                cb_data = '|'.join((el[0], str(el[1]), el[2]))
                keyboard.add(InlineKeyboardButton(button_text, callback_data=cb_data))

            keyboard.add(kb.prevButton)
            if len(elements_groups) > group_index + 1:
                keyboard.insert(kb.nextButton)
            keyboard.add(kb.backButton)
            keyboard.add(kb.mMenuButton)

            text = f'<b>Choose {mk_type} to remove</b>:\nPage {group_index + 1}'

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
                cb_data = '|'.join((el[0], str(el[1]), el[2]))
                keyboard.add(InlineKeyboardButton(button_text, callback_data=cb_data))

            if group_index - 1 >= 0:
                keyboard.add(kb.prevButton)
            keyboard.insert(kb.nextButton)
            keyboard.add(kb.backButton)
            keyboard.add(kb.mMenuButton)

            text = f'<b>Choose {mk_type} to remove</b>:\nPage {group_index + 1}'

            async with state.proxy() as data:
                data['group_index'] = group_index
        else:
            text = 'No prev data. It\'s an error. Send nudes to the developer!'
            keyboard = kb.cancelKeyboard

        await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
        return

    data_base.remove_element(callback_query.from_user.id, int(cb_data[1]))
    if cb_data[2]:
        text = f'<b>{cb_data[0]} ({cb_data[2]}) removed!</b>'
    else:
        text = f'<b>{cb_data[0]} removed!</b>'
    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.gotKeyboard)


# REMOVE COLOUR STORY
@dp.callback_query_handler(text='colour_story', state=RemoveMakeup.start)
async def callback_remove_colour_story(callback_query: types.CallbackQuery,
                                       state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    colour_stories = data_base.get_colour_stories(callback_query.from_user.id)
    if colour_stories:
        keyboard = InlineKeyboardMarkup()
        for cs in colour_stories:
            cb_data = '|'.join((cs[0], str(cs[1])))
            keyboard.add(InlineKeyboardButton(cs[0], callback_data=cb_data))
        keyboard.add(kb.backButton)

        await bot.edit_message_text('<b>Choose colour story to remove</b>',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
        await RemoveMakeup.colour_story.set()
    else:
        await bot.edit_message_text('<b>There is no colour stories in the data base!</b>',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.cancelKeyboard)


# REMOVE COLOUR STORY DONE
@dp.callback_query_handler(state=RemoveMakeup.colour_story)
async def callback_removed_colour_story(callback_query: types.CallbackQuery,
                                        state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    cb_data = callback_query.data.split('|')
    data_base.remove_colour_story(callback_query.from_user.id, int(cb_data[1]))

    await bot.edit_message_text(f'<b>Colour story {cb_data[0].capitalize()} removed!</b>',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.gotKeyboard)


# REMOVE COLOUR
@dp.callback_query_handler(text='colour', state=RemoveMakeup.start)
async def callback_remove_colour(callback_query: types.CallbackQuery,
                                 state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    colours = data_base.get_colours(callback_query.from_user.id)
    if not colours:
        await bot.edit_message_text(
            f'<b>There is no colours  in the data base! Please add any colour from "Add predefined colour"!</b>',
            callback_query.from_user.id, callback_query.message.message_id,
            reply_markup=kb.cancelKeyboard)
        return

    keyboard = InlineKeyboardMarkup()
    for color in colours:
        cb_data = '|'.join((color[0], str(color[1])))
        keyboard.add(InlineKeyboardButton(color[0], callback_data=cb_data))
    keyboard.add(kb.backButton)

    await bot.edit_message_text('<b>Choose colour to remove:</b>',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await RemoveMakeup.colour.set()


# REMOVE COLOUR STORY DONE
@dp.callback_query_handler(state=RemoveMakeup.colour)
async def callback_removed_colour(callback_query: types.CallbackQuery,
                                  state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    cb_data = callback_query.data.split('|')
    data_base.remove_colour(callback_query.from_user.id, int(cb_data[1]))

    await bot.edit_message_text(f'<b>Colour {cb_data[0].capitalize()} removed!</b>',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.gotKeyboard)
