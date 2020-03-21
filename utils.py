from telebot import types


def get_scrum_keyboard():
    return get_custom_keyboard(['0.5', '1', '2', '3', '5', '8', '13'])

def get_custom_keyboard(keys):
    keyboard = types.InlineKeyboardMarkup()
    for key_label in keys:
        key = types.InlineKeyboardButton(text=key_label, callback_data=key_label)
        keyboard.add(key)
    return keyboard
