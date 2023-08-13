from datetime import datetime

from market.data_access.models.models import Cart, CartItem
from market.data_access.repositories.IRepository import IRepository


class CartRepository(IRepository):
    def __init__(self, db):
        self.db = db

    def find_with_items_by_user_id(self, user_id: int) -> Cart:
        return Cart.query \
            .options(self.db.joinedload(Cart.cart_items)).filter_by(users_id=user_id).first()

    def find_with_items_and_products_by_user_id(self, user_id: int) -> Cart:
        return Cart.query.options(self.db.joinedload(Cart.cart_items).joinedload(CartItem.product)) \
            .filter_by(users_id=user_id).first()

    def create(self, user_id: int, cart_items=[]) -> Cart:
        cart = Cart(users_id=user_id,
                    total_price=0,
                    date_created=datetime.now(),
                    date_modified=datetime.now(),
                    cart_items=cart_items)
        self.db.session.add(cart)
        return cart

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