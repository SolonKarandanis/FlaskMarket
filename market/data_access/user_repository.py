from market.data_access.models import User


class UserRepository:
    def __init__(self, db):
        self.db = db

    def find_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def add(self, username, email_address, password):
        user_to_create = User(username=username,
                              email_address=email_address,
                              password=password)
        self.db.session.add(user_to_create)
        return user_to_create
