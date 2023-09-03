from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from create_bot import MAKEUPS

# Global Buttons
backButton = InlineKeyboardButton('<< Back', callback_data='back')
cancelButton = InlineKeyboardButton('<< Cancel', callback_data='back')
confirmButton = InlineKeyboardButton('>> Confirm <<', callback_data='confirm')
mMenuButton = InlineKeyboardButton('<< Main menu >>', callback_data='main_menu')
gotButton = InlineKeyboardButton('<< Got it! >>', callback_data='back')
nextButton = InlineKeyboardButton('Next -->>', callback_data='next')
prevButton = InlineKeyboardButton('<<-- Previous', callback_data='prev')

# Got it! Keyboard
gotKeyboard = InlineKeyboardMarkup().add(gotButton)

# Back Keyboard
backKeyboard = InlineKeyboardMarkup().add(backButton)

# Next Keyboard
nextKeyboard = InlineKeyboardMarkup()
nextKeyboard.insert(nextButton)
nextKeyboard.add(backButton)

# Prev Keyboard
prevKeyboard = InlineKeyboardMarkup()
prevKeyboard.insert(prevButton)
prevKeyboard.add(backButton)

# Next\Prev Keyboard
nextPrevKeyboard = InlineKeyboardMarkup()
nextPrevKeyboard.insert(prevButton)
nextPrevKeyboard.insert(nextButton)
nextPrevKeyboard.add(backButton)

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
    InlineKeyboardButton('Colour Story', callback_data='colour_story'),
    InlineKeyboardButton('Full Random', callback_data='full_random'),
    InlineKeyboardButton('Random Element', callback_data='elements'),
    InlineKeyboardButton('Random Image', callback_data='images'),
    InlineKeyboardButton('Settings', callback_data='settings'))

mMenuKeyboard = InlineKeyboardMarkup()
for button in main_menu_buttons:
    mMenuKeyboard.add(button)

#  Settings keyboard
settings_buttons = (
    InlineKeyboardButton('Show All', callback_data='show'),
    InlineKeyboardButton('Find Makeup', callback_data='find'),
    InlineKeyboardButton('Edit Makeup', callback_data='edit'),
    InlineKeyboardButton('Add Makeup', callback_data='add_makeup'),
    InlineKeyboardButton('Remove Makeup', callback_data='remove_makeup'),
    InlineKeyboardButton('Add Image', callback_data='add_image'),
    InlineKeyboardButton('Remove Image', callback_data='remove_image'))

settingsKeyboard = InlineKeyboardMarkup()
for button in settings_buttons:
    settingsKeyboard.add(button)
settingsKeyboard.add(backButton)

# Edit Keyboard
edit_buttons = (
    InlineKeyboardButton('Edit Name', callback_data='edit_name'),
    InlineKeyboardButton('Edit Colours', callback_data='edit_colours'),
    InlineKeyboardButton('Edit Priority', callback_data='edit_priority'))

editKeyboard = InlineKeyboardMarkup()
for button in edit_buttons:
    editKeyboard.add(button)
editKeyboard.add(backButton)
editKeyboard.add(mMenuButton)

# Images Keyboard
edit_buttons = (
    InlineKeyboardButton('Edit Name', callback_data='edit_name'),
    InlineKeyboardButton('Edit Colours', callback_data='edit_colours'),
    InlineKeyboardButton('Edit Priority', callback_data='edit_priority'))