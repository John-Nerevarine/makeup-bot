from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified
import keyboards as kb
from main_menu import getBackData
import data_base
from create_bot import bot, dp, Settings, MainMenu, Image
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# GET IMAGE
@dp.callback_query_handler(text='images', state=MainMenu.start)
async def callback_get_image(callback_query: types.CallbackQuery,
                             state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    image = data_base.get_random_image(callback_query.from_user.id)
    if image:
        image_message = await bot.send_photo(chat_id=callback_query.from_user.id, photo=image['telegram_id'])
        await bot.edit_message_text(f'<b>{image["name"]}</b>\nPlease, return to menu, when finished!',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.cancelKeyboard)
        async with state.proxy() as data:
            data['image_message_id'] = image_message.message_id
    else:
        await bot.edit_message_text(f'No images in base!',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.cancelKeyboard)
    await Image.show_image.set()


# ADD IMAGE
@dp.callback_query_handler(text='add_image', state=Settings.start)
async def callback_add_image(callback_query: types.CallbackQuery,
                             state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)
    m = await bot.edit_message_text('<b>Please, send a photo:</b>',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.cancelKeyboard)

    async with state.proxy() as data:
        data['message_id'] = m.message_id

    await Image.send.set()


# IMAGE ID
@dp.message_handler(state=Image.send, content_types=types.ContentType.PHOTO)
async def massage_save_image(message: types.Message,
                             state: FSMContext):
    telegram_id = message.photo[-1].file_id

    async with state.proxy() as data:
        data['telegram_id'] = telegram_id
        message_id = data['message_id']

    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.edit_message_text('<b>Type name for the photo:</b>',
                                message.from_user.id, message_id,
                                reply_markup=kb.cancelKeyboard)

    await Image.enter_name.set()


# ENTER IMAGE NAME
@dp.message_handler(state=Image.enter_name)
async def massage_enter_image_name(message: types.Message,
                                   state: FSMContext):
    async with state.proxy() as data:
        message_id = data['message_id']
        telegram_id = data['telegram_id']

    if message.text:
        async with state.proxy() as data:
            message_id = data['message_id']

        if data_base.image_find_existence(message.from_user.id, message.text):
            await bot.delete_message(message.from_user.id, message.message_id)
            text = f'<b>{message.text}</b> is already in base! Try another one...'
            try:
                await bot.edit_message_text(text,
                                            message.from_user.id, message_id,
                                            reply_markup=kb.cancelKeyboard)
            except MessageNotModified:
                await bot.edit_message_text(text + '.',
                                            message.from_user.id, message_id,
                                            reply_markup=kb.cancelKeyboard)
            return

    else:
        await bot.delete_message(message.from_user.id, message.message_id)
        text = f'Name cannot be empty! Enter name!'
        try:
            await bot.edit_message_text(text,
                                        message.from_user.id, message_id,
                                        reply_markup=kb.cancelKeyboard)
        except MessageNotModified:
            await bot.edit_message_text(text + '!',
                                        message.from_user.id, message_id,
                                        reply_markup=kb.cancelKeyboard)
        return

    data_base.add_image(message.from_user.id, message.text, telegram_id)

    text = f'Image <b>{message.text}</b> successfully added to base.'
    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.edit_message_text(text,
                                message.from_user.id, message_id,
                                reply_markup=kb.backKeyboard)


# REMOVE IMAGE
@dp.callback_query_handler(text='remove_image', state=Settings.start)
async def callback_remove_image(callback_query: types.CallbackQuery,
                                state: FSMContext):
    await getBackData(state, callback_query.message)
    await bot.answer_callback_query(callback_query.id)

    images = data_base.get_all_images_names(callback_query.from_user.id)
    if images:
        keyboard = InlineKeyboardMarkup()
        for image in images:
            keyboard.add(InlineKeyboardButton(text=image[1], callback_data=image[0]))
        keyboard.add(kb.backButton)
        await bot.edit_message_text(f'Choose image to delete:',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=keyboard)
    else:
        await bot.edit_message_text(f'No images in base!',
                                    callback_query.from_user.id, callback_query.message.message_id,
                                    reply_markup=kb.backKeyboard)
    await Image.delete.set()


# IMAGE REMOVED
@dp.callback_query_handler(state=Image.delete)
async def callback_image_removed(callback_query: types.CallbackQuery,
                                 state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    data_base.remove_image(callback_query.data)

    await bot.edit_message_text(f'Image removed!',
                                callback_query.from_user.id, callback_query.message.message_id,
                                reply_markup=kb.backKeyboard)
