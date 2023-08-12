from market import db
from market.data_access.cart_repository import CartRepository
from market.data_access.product_repository import ProductRepository

product_repo = ProductRepository(db)
cart_repo = CartRepository(db)