import json


class UserManager:

    def __init__(self, filename='users.json'):
        self.filename = filename
        try:
            with open(filename, "r") as file:
                self.users = json.load(file)
        except FileNotFoundError:
            self.users = {}

    def add_user(self, user_name, user_data):
        self.users[user_name] = user_data

        with open(self.filename, "w") as file:
            json.dump(self.users, file)

    def user_by_id(self, id):
        for user, user_data in self.users.values():
            if id == user_data['id']:
                return user
