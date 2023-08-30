from aiogram import types
from aiogram.dispatcher import FSMContext
import keyboards as kb
from main_menu import getBackData
import data_base
from create_bot import bot, dp, Find, Edit, Settings, MAKEUPS
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# CHOOSE TYPE
@dp.callback_query_handler(text='find', state=Settings.start)
async def callback_find_makeup(callback_query: types.CallbackQuery,
                               state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    keyboard = InlineKeyboardMarkup()
    for mk in MAKEUPS:
        keyboard.add(InlineKeyboardButton(f'Find {mk.capitalize()}', callback_data=mk))
    keyboard.add(kb.backButton)

    await bot.edit_message_text('<b>Choose makeup to find:</b>',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=keyboard)
    await Find.start.set()


# TYPE NAME
@dp.callback_query_handler(text=MAKEUPS, state=Find.start)
async def callback_find_type_name(callback_query: types.CallbackQuery,
                                  state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    mk_type = callback_query.data

    m = await bot.edit_message_text(f'<b>Find {mk_type.capitalize()}</b>\nEnter name:',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.cancelKeyboard)

    async with state.proxy() as data:
        data['mk_type'] = mk_type
        data['message_id'] = m.message_id

    await Find.type_name.set()


# RESULT
@dp.message_handler(state=Find.type_name)
async def callback_find_result(message: types.Message,
                               state: FSMContext):
    name = message.text if message.text else "Unnamed"
    async with state.proxy() as data:
        mk_type = data['mk_type']
        message_id = data['message_id']

    result = data_base.find(message.from_user.id, mk_type, name)

    if result:
        text = f'{mk_type.capitalize()} <b>"{name}"</b> found:'
        elements_groups = []
        while len(result) > 30:
            elements_groups.append(result[:30])
            result = result[30:]
        else:
            elements_groups.append(result)

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
        await bot.delete_message(message.from_user.id, message.message_id)
        text = f'<b>NO {mk_type.capitalize()} "{name}" found.</b>'
        keyboard = kb.backKeyboard

    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.edit_message_text(text,
                                message.from_user.id, message_id,
                                reply_markup=keyboard)
