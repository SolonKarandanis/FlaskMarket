from market.data_access.models.models import User


class UserRepository:
    def __init__(self, db):
        self.db = db

    def find_by_username(self, username: str) -> User:
        return User.query.filter_by(username=username).first()

    def create(self, username: str, email_address: str, password: str) -> User:
        user_to_create = User(username=username,
                              email_address=email_address,
                              password=password)
        self.db.session.add(user_to_create)
        return user_to_create
