from market import db
from market.data_access.repositories.cart_repository import CartRepository
from market.data_access.repositories.order_repository import OrderRepository
from market.data_access.repositories.product_repository import ProductRepository
from market.data_access.repositories.user_repository import UserRepository

product_repo = ProductRepository(db)
cart_repo = CartRepository(db)
user_repo = UserRepository(db)
order_repo = OrderRepository(db)
