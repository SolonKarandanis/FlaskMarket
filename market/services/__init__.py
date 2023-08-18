from market.data_access import cart_repo, user_repo, order_repo, product_repo
from market.services.cart_service import CartService
from market.services.email_service import EmailService
from market.services.user_service import UserService

email_service = EmailService()
cart_service = CartService(cart_repo)
user_service = UserService(user_repo)
