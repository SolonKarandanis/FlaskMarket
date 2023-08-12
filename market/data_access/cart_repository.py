from market.data_access.models import Cart


class CartRepository:
    def __init__(self, db):
        self.db = db

    def find_by_user_id(self, user_id):
        return Cart.query \
            .options(self.db.joinedload(Cart.cart_items)).filter_by(users_id=user_id).first()
