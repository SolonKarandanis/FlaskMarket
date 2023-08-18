from market.data_access.models.models import User
from market.data_access.repositories.IRepository import IRepository


class UserRepository(IRepository):
    def __init__(self, db):
        self.db = db

    def find_by_username(self, username: str) -> User:
        return User.query.filter_by(username=username).first()

    def find_by_email(self, email: str) -> User:
        return User.query.filter_by(email_address= email).first()

    def create(self, username: str, email_address: str, password: str) -> User:
        user_to_create = User(username=username,
                              email_address=email_address,
                              password=password)
        self.db.session.add(user_to_create)
        return user_to_create

    def find_all(self):
        pass

    def find_all_pageable(self, page, rows_per_page: int = 5):
        pass

    def find_by_id(self, item_id: int):
        pass

    def update(self, item):
        pass

    def delete(self, item_id: int):
        pass