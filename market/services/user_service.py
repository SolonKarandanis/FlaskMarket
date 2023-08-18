from market.data_access import UserRepository
from market.data_access.models.models import User
from market import app, bcrypt
import jwt
from time import time


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def find_by_username(self, username: str) -> User:
        return self.repo.find_by_username(username)

    def find_by_email(self, email: str) -> User:
        return self.repo.find_by_email(email)

    def create(self, username: str, email_address: str, password: str) -> User:
        return self.repo.create(username, email_address, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    def verify_reset_password_token(self, token: str) -> User:
        try:
            userId = jwt.decode(token, app.config['SECRET_KEY'],
                                algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(userId)
