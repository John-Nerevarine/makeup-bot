from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
import keyboards as kb
from create_bot import MainMenu, bot, MAIN_MENU_MESSAGE


# Any button action if bot has been restarted
async def callbackEmergencyStart(callback_query: types.CallbackQuery,
                                 state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    try:
        m = await bot.edit_message_text(MAIN_MENU_MESSAGE,
                                        callback_query.from_user.id, callback_query.message.message_id,
                                        reply_markup=kb.mMenuKeyboard)
    except Exception as e:
        if str(e) == 'Message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message':
            m = callback_query.message
        else:
            m = await bot.send_message(callback_query.from_user.id,
                                       '<b>==Main Menu==</b>',
                                       reply_markup=kb.mMenuKeyboard)
    await state.finish()
    await MainMenu.start.set()
    async with state.proxy() as data:
        data['backStates'] = []
        data['backTexts'] = []
        data['backKeyboards'] = []
        data['message_id'] = m.message_id


# Deleting any useless user message
async def commandDeleteMessage(message: types.Message, state: FSMContext):
    await bot.delete_message(message.from_user.id, message.message_id)


def registerHandlers(dp: Dispatcher):
    dp.register_callback_query_handler(callbackEmergencyStart, lambda c: True, state='*')
    dp.register_message_handler(commandDeleteMessage, state='*')
