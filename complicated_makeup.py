from aiogram import types
from aiogram.dispatcher import FSMContext
import keyboards as kb
from main_menu import getBackData
import data_base
from create_bot import bot, dp, ColourStory, MainMenu, MAKEUPS
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from random import choice


# COLOUR STORY
@dp.callback_query_handler(text='colour_story', state=MainMenu.start)
async def callback_colour_story(callback_query: types.CallbackQuery,
                                state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('Random Colour Story', callback_data='random'))
    keyboard.add(InlineKeyboardButton('Choose Colour Story', callback_data='choose'))
    keyboard.add(kb.backButton)

    await bot.edit_message_text('<b>Colour story</b>\n',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)

    await ColourStory.start.set()


# RANDOM
@dp.callback_query_handler(text='random', state=ColourStory.start)
async def callback_random_colour_story(callback_query: types.CallbackQuery,
                                       state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    colour_stories = data_base.get_colour_stories(callback_query.from_user.id)
    if colour_stories:
        colour_story = choice(colour_stories)
        cs_name = colour_story[0]
        makeup = data_base.get_makeup_from_colour_story(user_id=callback_query.from_user.id,
                                                        colour_story_id=colour_story[1])
        elements_text = '\n'.join(f'{mkp.capitalize()}: <b>{makeup[mkp]}</b>' for mkp in MAKEUPS)

        text = '\n'.join((f'Colour story: <i>{cs_name}</i>',
                          elements_text,
                          f'Glitter: <b>{"Yes" if makeup["glitter"] else "No"}</b>',
                          ))

        await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.restartKeyboard)
    else:
        await bot.edit_message_text('<b>There is no colour stories in the data base!</b>',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.restartKeyboard)


# CHOOSE
@dp.callback_query_handler(text='choose', state=ColourStory.start)
async def callback_choose_colour_story(callback_query: types.CallbackQuery,
                                       state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    colour_stories = data_base.get_colour_stories(callback_query.from_user.id)
    if colour_stories:
        keyboard = InlineKeyboardMarkup()
        for cs in colour_stories:
            cb_data = '|'.join((cs[0], str(cs[1])))
            keyboard.add(InlineKeyboardButton(text=cs[0], callback_data=cb_data))
        keyboard.add(kb.backButton)
        text = '<b>Choose colour story</b>:'
        await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
        await ColourStory.choose_cs.set()
    else:
        await bot.edit_message_text('<b>There is no colour stories in the data base!</b>',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.restartKeyboard)


@dp.callback_query_handler(state=ColourStory.choose_cs)
async def callback_colour_story_get(callback_query: types.CallbackQuery,
                                    state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    cb_data = callback_query.data.split('|')
    colour_story_id = int(cb_data[1])
    cs_name = cb_data[0]
    makeup = data_base.get_makeup_from_colour_story(user_id=callback_query.from_user.id,
                                                    colour_story_id=colour_story_id)

    elements_text = '\n'.join(f'{mkp.capitalize()}: <b>{makeup[mkp]}</b>' for mkp in MAKEUPS)

    text = '\n'.join((f'Colour story: <i>{cs_name}</i>',
                      elements_text,
                      f'Glitter: <b>{"Yes" if makeup["glitter"] else "No"}</b>',
                      ))

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.restartKeyboard)


# FULL RANDOM
@dp.callback_query_handler(text='full_random', state=MainMenu.start)
async def callback_full_random(callback_query: types.CallbackQuery,
                               state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    makeup = data_base.get_full_random(callback_query.from_user.id)

    elements_text = '\n'.join(f'{mkp.capitalize()}: <b>{makeup[mkp]}</b>' for mkp in MAKEUPS)

    text = '\n'.join((f'Full random:',
                      elements_text,
                      f'Glitter: <b>{"Yes" if makeup["glitter"] else "No"}</b>',
                      ))

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.restartKeyboard)
