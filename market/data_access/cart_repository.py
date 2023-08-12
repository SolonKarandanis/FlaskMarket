from datetime import datetime

from market.data_access.models import Cart, CartItem


class CartRepository:
    def __init__(self, db):
        self.db = db

    def find_with_items_by_user_id(self, user_id):
        return Cart.query \
            .options(self.db.joinedload(Cart.cart_items)).filter_by(users_id=user_id).first()

    def find_with_items_and_products_by_user_id(self, user_id):
        return Cart.query.options(self.db.joinedload(Cart.cart_items).joinedload(CartItem.product)) \
            .filter_by(users_id=user_id).first()

    def add(self, user_id, cart_items=[]):
        cart = Cart(users_id=user_id,
                    total_price=0,
                    date_created=datetime.now(),
                    date_modified=datetime.now(),
                    cart_items=cart_items)
        self.db.session.add(cart)
        return cart