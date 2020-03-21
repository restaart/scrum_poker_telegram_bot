from utils import get_scrum_keyboard


class Session:
    def __init__(self,user_manager,bot):
        self.participants = {}
        self.bot = bot
        self.user_manager = user_manager


    def start(self,message):
        self.init_message = message
        entities = [ent for ent in message.entities if ent.type == 'mention']
        usernames = [message.text[ent.offset:ent.offset + ent.length] for ent in entities]
        usernames = [user[1:] for user in usernames if user[-3:] != 'bot']
        message_start = max((ent.offset + ent.length for ent in entities))
        text = message.text[message_start:]
        self.vote_case = text
        user_ids = [self.user_manager.users[uname]['id'] for uname in usernames]
        keyboard = get_scrum_keyboard()
        for uid,uname in zip(user_ids,usernames):
            self.participants[uname] = {'ready': False}
            self.bot.send_message(uid, f'Начато голосование по задаче {self.vote_case}')
            self.bot.send_message(uid, 'Предложите оценку', reply_markup=keyboard)

    def get_vote_text(self,user):
        return '{user}: {score}'.format(user=self.user_manager.users[user]['first_name'], score=self.participants[user]['score'])


    def vote(self,user,data):
        self.participants[user]['score'] = data
        self.participants[user]['ready'] = True

        if all((participant['ready'] for participant in self.participants.values())):
            result_message = 'Голосование завершено\n' + '\n'.join([self.get_vote_text(user)
                                                                    for user in self.participants])
            self.bot.reply_to(self.init_message, result_message)
            del self