from aiogram import types
from aiogram.dispatcher import FSMContext
import keyboards as kb
from main_menu import getBackData
import data_base
from create_bot import bot, dp, MainMenu, RemoveMakeup, MAKEUPS
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# START REMOVING MAKEUP
@dp.callback_query_handler(text='remove_makeup', state=MainMenu.start)
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

    elements = data_base.get_elements(callback_query.from_user.id, callback_query.data)

    if elements:
        keyboard = InlineKeyboardMarkup()
        for element in elements:
            cb_data = '|'.join((element[0], str(element[1])))
            keyboard.add(InlineKeyboardButton(element[0], callback_data=cb_data))
        keyboard.add(kb.backButton)

        await bot.edit_message_text('<b>Choose makeup to remove:</b>',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
        await RemoveMakeup.makeup.set()

    else:
        await bot.edit_message_text(f'<b>No {callback_query.data} to remove!</b>',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.cancelKeyboard)


# REMOVE MAKEUP DONE
@dp.callback_query_handler(state=RemoveMakeup.makeup)
async def callback_removed_makeup(callback_query: types.CallbackQuery,
                                 state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    cb_data = callback_query.data.split('|')
    data_base.remove_element(callback_query.from_user.id, int(cb_data[1]))

    await bot.edit_message_text(f'<b>{cb_data[0].capitalize()} removed!</b>',
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
        await bot.edit_message_text(f'<b>There is no colours  in the data base! Please add any colour from "Add predefined colour"!</b>',
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
