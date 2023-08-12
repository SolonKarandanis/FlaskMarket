from datetime import datetime

from market.data_access.models import Order


class OrderRepository:
    def __init__(self, db):
        self.db = db

    def find_by_user_and_id(self, user_id, order_id):
        return Order.query.options(self.db.joinedload(Order.order_items)) \
            .filter_by(users_id=user_id).filter_by(id=order_id).first()

    def add(self, user_id, total_price, order_comments):
        order = Order(users_id=user_id,
                      date_created=datetime.now(),
                      status="order.submitted",
                      total_price=total_price,
                      comments=order_comments)
        self.db.session.add(order)
        return order