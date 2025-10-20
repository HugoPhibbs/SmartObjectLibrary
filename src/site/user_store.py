from flask_login import UserMixin

users = {
    "admin": {"username": "admin", 'password': "password123"},
}


class User(UserMixin):
    def __init__(self, id: str, username: str):
        self.id = id
        self.username = username


def get_username(user_id: str):
    user_info = users.get(user_id)
    if user_info:
        return user_info['username']
    return None


def verify_user(username, password):
    for user_id, user_info in users.items():
        if user_info['username'] == username and user_info['password'] == password:
            return True
    return False


__all__ = ['get_username', 'verify_user', 'User']
