from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from create_bot import MAKEUPS

# Global Buttons
backButton = InlineKeyboardButton('<< Back', callback_data='back')
cancelButton = InlineKeyboardButton('<< Cancel', callback_data='back')
confirmButton = InlineKeyboardButton('>> Confirm <<', callback_data='confirm')
mMenuButton = InlineKeyboardButton('<< Main menu >>', callback_data='main_menu')
gotButton = InlineKeyboardButton('<< Got it! >>', callback_data='back')

# Got it! Keyboard
gotKeyboard = InlineKeyboardMarkup().add(gotButton)

# Back Keyboard
backKeyboard = InlineKeyboardMarkup().add(backButton)

# Restart Keyboard
restartKeyboard = InlineKeyboardMarkup().add(mMenuButton)

# Cancel Keyboard
cancelKeyboard = InlineKeyboardMarkup().add(cancelButton)

# Confirm Keyboard
confirmKeyboard = InlineKeyboardMarkup()
confirmKeyboard.add(confirmButton)
confirmKeyboard.add(cancelButton)

random_elements_buttons = ([InlineKeyboardButton(mk.capitalize(), callback_data=mk) for mk in MAKEUPS])
randomElementsKeyboard = InlineKeyboardMarkup()

for button in random_elements_buttons:
    randomElementsKeyboard.add(button)

randomElementsKeyboard.add(InlineKeyboardButton('Glitter', callback_data='glitter'))
randomElementsKeyboard.add(backButton)

# Main Menu Keyboard
main_menu_buttons = (
    InlineKeyboardButton('Random element', callback_data='elements'),
    InlineKeyboardButton('Colour story', callback_data='colour_story'),
    InlineKeyboardButton('Full random', callback_data='full_random'),
    InlineKeyboardButton('Show all', callback_data='show'),
    InlineKeyboardButton('Add makeup', callback_data='add_makeup'),
    InlineKeyboardButton('Remove makeup', callback_data='remove_makeup'))

mMenuKeyboard = InlineKeyboardMarkup()
for button in main_menu_buttons:
    mMenuKeyboard.add(button)

