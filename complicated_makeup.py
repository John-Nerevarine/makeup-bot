from aiogram import types
from aiogram.dispatcher import FSMContext
import keyboards as kb
from main_menu import getBackData
import data_base
from create_bot import bot, dp, ColourStory, Eyeshadowing, MainMenu, MAKEUPS, MAKEUPS_WO_LIPS
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
        elements_text = '\n'.join(f'{mkp.capitalize()}: <b>{makeup[mkp]}</b>' for mkp in MAKEUPS_WO_LIPS)

        text = '\n'.join((f'Colour story: <i>{cs_name}</i>', elements_text))

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

    elements_text = '\n'.join(f'{mkp.capitalize()}: <b>{makeup[mkp]}</b>' for mkp in MAKEUPS_WO_LIPS)

    text = '\n'.join((f'Colour story: <i>{cs_name}</i>', elements_text))

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

    text = '\n'.join((f'Full random:', elements_text))

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.restartKeyboard)


# EYESHADOWING
@dp.callback_query_handler(text='eyeshadowing', state=MainMenu.start)
async def callback_eyeshadowing_choose(callback_query: types.CallbackQuery,
                                       state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    eyeshadows = data_base.get_elements(callback_query.from_user.id, 'eyeshadow')

    if eyeshadows:
        text = f'<b>Choose Eyeshadow</b>:'
        eyeshadows_groups = []
        while len(eyeshadows) > 30:
            eyeshadows_groups.append(eyeshadows[:30])
            eyeshadows = eyeshadows[30:]
        else:
            eyeshadows_groups.append(eyeshadows)

        keyboard = InlineKeyboardMarkup()
        for shadow in eyeshadows_groups[0]:
            if shadow[2]:
                text = f'{shadow[0]} ({shadow[2]})'
            else:
                text = shadow[0]
            keyboard.add(InlineKeyboardButton(text, callback_data=shadow[1]))

        if len(eyeshadows_groups) > 1:
            keyboard.add(kb.nextButton)
        keyboard.add(kb.backButton)
        keyboard.add(kb.mMenuButton)

        async with state.proxy() as data:
            data['eyeshadows_groups'] = eyeshadows_groups
            data['group_index'] = 0

        await Eyeshadowing.start.set()
    else:
        text = f'There is no eyeshadows in database!'
        keyboard = kb.cancelKeyboard

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)


# EYESHADOWING RESULT / NEXT-PREV
@dp.callback_query_handler(state=Eyeshadowing.start)
async def callback_eyeshadowing_result(callback_query: types.CallbackQuery,
                                       state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    # Show next
    if callback_query.data == 'next':
        async with state.proxy() as data:
            eyeshadows_groups = data['eyeshadows_groups']
            group_index = data['group_index']
        if len(eyeshadows_groups) > group_index + 1:
            group_index += 1

            keyboard = InlineKeyboardMarkup()
            for shadow in eyeshadows_groups[group_index]:
                if shadow[2]:
                    text = f'{shadow[0]} ({shadow[2]})'
                else:
                    text = shadow[0]
                keyboard.add(InlineKeyboardButton(text, callback_data=shadow[1]))

            keyboard.add(kb.prevButton)
            if len(eyeshadows_groups) > group_index + 1:
                keyboard.insert(kb.nextButton)
            keyboard.add(kb.backButton)
            keyboard.add(kb.mMenuButton)

            text = f'<b>Choose Eyeshadow</b>:\nPage {group_index + 1}'

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
            eyeshadows_groups = data['eyeshadows_groups']
            group_index = data['group_index']
        if group_index - 1 >= 0:
            group_index -= 1
            keyboard = InlineKeyboardMarkup()
            for shadow in eyeshadows_groups[group_index]:
                if shadow[2]:
                    text = f'{shadow[0]} ({shadow[2]})'
                else:
                    text = shadow[0]
                keyboard.add(InlineKeyboardButton(text, callback_data=shadow[1]))

            if group_index - 1 >= 0:
                keyboard.add(kb.prevButton)
                keyboard.insert(kb.nextButton)
            else:
                keyboard.add(kb.nextButton)
            keyboard.add(kb.backButton)
            keyboard.add(kb.mMenuButton)

            text = f'<b>Choose Eyeshadow</b>:\nPage {group_index + 1}'

            async with state.proxy() as data:
                data['group_index'] = group_index
        else:
            text = 'No prev data. It\'s an error. Send nudes to the developer!'
            keyboard = kb.cancelKeyboard

        await bot.edit_message_text(text,
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
        return

    text = data_base.eyeshadowing(callback_query.from_user.id, callback_query.data)

    await bot.edit_message_text(text,
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)

    await Eyeshadowing.end.set()
