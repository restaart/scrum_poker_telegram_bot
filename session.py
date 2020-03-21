from utils import get_scrum_keyboard, get_custom_keyboard


class Session:

    def set_keyboard(self, keys_list):
        self.poll_keyboard = get_custom_keyboard(keys_list)

    def __init__(self, user_manager, bot):
        self.participants = {}
        self.ongoing = True
        self.bot = bot
        self.user_manager = user_manager
        self.poll_keyboard = get_scrum_keyboard()

    def send_poll_participation_request(self, uname):
        uid = self.user_manager.users[uname]['id']
        self.bot.send_message(uid, f'Начато голосование по задаче {self.vote_case}')
        self.bot.send_message(uid, 'Предложите оценку', reply_markup=self.poll_keyboard)

    def parse_init_message(self, message):
        if '/options' in message.text:
            options = message.text.split('/options(')[1].split(')')[0].split(',')
            message.text = message.text.split('/options(')[0] + message.text.split('/options(')[1].split(')')[1]
        else:
            options = None

        entities = [ent for ent in message.entities if ent.type == 'mention']
        usernames = [message.text[ent.offset:ent.offset + ent.length] for ent in entities]
        usernames = [user[1:] for user in usernames if user[-3:] != 'bot']
        usernames = set(usernames)
        message_start = max((ent.offset + ent.length for ent in entities))
        vote_case = message.text[message_start:]

        return vote_case, usernames, options

    def start(self, message):
        self.init_message = message

        vote_case, usernames, options = self.parse_init_message(message)
        self.vote_case = vote_case
        if options:
            self.set_keyboard(options)

        unregistered_users = []
        for uname in usernames:
            self.participants[uname] = {'ready': False, 'registered': uname in self.user_manager.users}
            if self.participants[uname]['registered']:
                self.send_poll_participation_request(uname)
            else:
                unregistered_users.append(uname)

        self.bot.reply_to(message, f'Начато голосование по {self.vote_case}')

        if len(unregistered_users) > 0:
            reg_mes = ' '.join(('@' + uname for uname in unregistered_users))
            self.bot.reply_to(message, f'Зарегистрируйтесь для участия в голосовании {reg_mes} /start')

    def get_vote_text(self, user):
        return '{user}: {score}'.format(user=self.user_manager.users[user]['first_name'],
                                        score=self.participants[user]['score'])

    def vote(self, user, data):
        self.participants[user]['score'] = data
        self.participants[user]['ready'] = True

        if all((participant['ready'] for participant in self.participants.values())):
            result_message = 'Голосование завершено\n' + '\n'.join([self.get_vote_text(user)
                                                                    for user in self.participants])
            self.bot.reply_to(self.init_message, result_message)
            self.ongoing = False
            Session.poll_keyboard = get_scrum_keyboard()
