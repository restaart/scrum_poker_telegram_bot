from telebot import types, TeleBot

from session import Session
from user_manager import UserManager

with open('token') as f:
    token = f.read()

bot = TeleBot(token)
user_manager = UserManager()

session = None


@bot.message_handler(commands=['poll', 'options'])
def poll_handler(message):
    global session
    if message.chat.type == 'group' and not session:
        session = Session(user_manager, bot)
        session.start(message)


@bot.message_handler(commands=['start'])
def start_handler(message):
    user_data = message.json['from']
    user_name = user_data.pop('username')
    user_manager.add_user(user_name, user_data)
    bot.reply_to(message, 'Вы зарегистрированны')
    if session and user_name in session.participants:
        session.send_poll_participation_request(user_name)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global session
    if session and session.ongoing:
        session.vote(call.from_user.username, call.data)
        if not session.ongoing:
            session = None
        bot.send_message(call.from_user.id, f'Вы проголосовали {call.data}')
        bot.delete_message(call.from_user.id, call.message.message_id)


print('start')
bot.polling(none_stop=True, interval=0)
