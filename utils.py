from telebot import types

def get_scrum_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for key_label in ['0.5','1','2','3','5','8', '13']:
        key = types.InlineKeyboardButton(text=key_label, callback_data=key_label)
        keyboard.add(key)
    return keyboard
