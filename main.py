import logging

from telebot import types, TeleBot

from session import Session
from user_manager import UserManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

with open('token') as f:
    token = f.read()

bot = TeleBot(token)
user_manager = UserManager()

session = None

def print_message(handler):
    def dec(message):
        try:
            print(message)
            handler(message)
        except Exception as e:
            logger.exception(e)
    return dec

@bot.message_handler(commands=['poll', 'options'])
@print_message
def poll_handler(message):
    global session
    if message.chat.type == 'group':
        if not session or not session.ongoing:
            # not session.ongoing or not session
            session = Session(user_manager, bot)
            session.start(message)
        else:
            bot.reply_to(message, "Голосование еще не завершено")


@bot.message_handler(commands=['start'])
@print_message
def start_handler(message):
    global session
    user_data = message.json['from']
    user_name = user_data.pop('username')
    user_manager.add_user(user_name, user_data)
    bot.reply_to(message, 'Вы зарегистрированны')
    if session and user_name in session.participants:
        session.send_poll_participation_request(user_name)

@bot.message_handler(commands=['newcase'])
@print_message
def start_handler(message):
    if session:
        if not session.ongoing:
            session.run_new_case(message)
        else:
            bot.reply_to(message,'Голосование не завершено.')
    else:
        bot.reply_to(message, 'Голосование еще не проводилось.')


@bot.callback_query_handler(func=lambda call: True)
@print_message
def callback_worker(call):
    global session
    if session and session.ongoing:
        session.vote(call.from_user.username, call.data)
        # if not session.ongoing:
        #     session = None
        bot.send_message(call.from_user.id, f'Вы проголосовали {call.data}')
        bot.delete_message(call.from_user.id, call.message.message_id)


print('start')
bot.polling(none_stop=True, interval=0)
