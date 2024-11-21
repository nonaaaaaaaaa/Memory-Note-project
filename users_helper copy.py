from os import path
from json import dump, load
from werkzeug.security import generate_password_hash, check_password_hash


class Users_function():
    """class user"""
    def __init__(self):
        self.filename = 'users.json'

    def check_if_file_exists(self):
        """check if file exists"""
        return path.exists(self.filename)

    def hash_password(self, password):
        """User passwords should NEVER be stored in plain text in a database."""
        return generate_password_hash(password)

    def is_valid(self, hashed_password, password):
        """is_valid function that expects 2 arguments and returns a boolean."""
        return check_password_hash(hashed_password, password)

    def load_user_data(self):
        """load user data from json file"""
        if self.check_if_file_exists() is True:
            with open(self.filename, 'r') as f:
                return load(f)
        else:
            return []

    def save_user_data(self, data):
        """Save user data to a JSON file."""
        current_users = self.load_user_data()
        current_users.append(data)
        with open(self.filename, 'w') as f:
            dump(current_users, f, indent=4)

    def check_user_if_exists(self, username, password):
        """check user if exists"""
        users = self.load_user_data()
        for user in users:
            if (user['email'] == username or user['username'] == username) and self.is_valid(user['password'], password):
                return user
            return False
    

# if __name__ == '__main__':
    # user = Users_function()
    # data = user.hash_password('000')
    # print(data)
    # print(user.is_valid(data, '000'))