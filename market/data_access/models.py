from typing import Set
from datetime import datetime
from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=30), unique=True, nullable=False)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)

    # products = db.relationship('Product', backref='owned_user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'address': self.email_address,
        }

    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        else:
            return f"{self.budget}$"

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class ProductTypeBase(db.DeclarativeBase):
    pass


product_type = db.Table(
    "product_type",
    ProductTypeBase.metadata,
    db.Column("type_id", db.ForeignKey("type.id"), primary_key=True),
    db.Column("product_id", db.ForeignKey("product.id"), primary_key=True),
)


class Type(ProductTypeBase):
    __tablename__ = 'type'

    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(length=30), nullable=False)

    def __repr__(self):
        return f"<Type {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type_name,
        }


class Product(ProductTypeBase):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(length=255), nullable=False)
    name = db.Column(db.String(length=255), nullable=False)
    supplier = db.Column(db.String(length=30), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    price = db.Column(db.Float)
    types: db.Mapped[Set[Type]] = db.relationship(secondary=product_type)

    @property
    def inline_types(self):
        types_list = list(self.types)
        if len(types_list) == 1:
            return types_list[0].type_name
        else:
            type_names = [tl.type_name for tl in types_list]
            comma_separated_strings = ','.join(type_names)
            return comma_separated_strings

    def __repr__(self):
        return f"<Product {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'supplier': self.supplier,
            'description': self.description,
            'price': self.price,
        }


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, db.Sequence("carts_sq", start=1), primary_key=True)
    total_price = db.Column(db.Float)
    modification_alert = db.Column(db.Boolean())
    date_created = db.Column(db.DateTime(timezone=True))
    date_modified = db.Column(db.DateTime(timezone=True))
    cart_items = db.relationship('CartItem', backref="cart", cascade="all, delete-orphan")
    users_id = db.Column(db.Integer, db.ForeignKey(User.id))

    def add_item_to_cart(self, products_id, quantity, price):
        existing_cart_item = next(filter(lambda ci: ci.products_id == products_id, self.cart_items), None)
        if existing_cart_item is None:
            cart_item = CartItem(quantity=quantity,
                                 modification_alert=False,
                                 unit_price=price,
                                 total_price=quantity * price,
                                 products_id=products_id)
            self.cart_items.append(cart_item)
        else:
            new_quantity = existing_cart_item.quantity + quantity
            existing_cart_item.quantity = new_quantity
            existing_cart_item.total_price = new_quantity * price

        self.update_cart_total_price()

    def update_item_quantity(self, cart_item_id, quantity):
        existing_cart_item = next(filter(lambda ci: ci.id == cart_item_id, self.cart_items), None)
        existing_cart_item.quantity = quantity
        existing_cart_item.total_price = quantity * existing_cart_item.unit_price
        self.update_cart_total_price()

    def remove_from_cart(self, cart_item):
        self.cart_items.remove(cart_item)
        self.update_cart_total_price()

    def clear_cart(self):
        self.cart_items.clear()
        self.update_cart_total_price()

    def update_cart_total_price(self):
        self.total_price = sum(ci.total_price for ci in self.cart_items)

    def __repr__(self):
        return f"<Cart {self.id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'total_price': self.total_price,
            'date_created': self.date_created,
            'date_modified': self.date_modified,
            'cart_items': [cart_item.to_dict() for cart_item in self.cart_items],
            'users_id': self.users_id,
        }


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, db.Sequence("cart_items_sq", start=1), primary_key=True)
    quantity = db.Column(db.Integer)
    modification_alert = db.Column(db.Boolean())
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    carts_id = db.Column(db.Integer, db.ForeignKey(Cart.id))
    products_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    product = db.relationship(Product, backref="cart_items")

    def __repr__(self):
        return f"<CartItem {self.id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'carts_id': self.carts_id,
            'products_id': self.products_id,
        }


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, db.Sequence("orders_sq", start=1), primary_key=True)
    date_created = db.Column(db.Date())
    status = db.Column(db.String(length=40))
    total_price = db.Column(db.Float)
    comments = db.Column(db.String(length=2048))
    order_items = db.relationship('OrderItem', backref="order")
    users_id = db.Column(db.Integer, db.ForeignKey(User.id))

    def __repr__(self):
        return f"<Order {self.id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'total_price': self.total_price,
            'date_created': self.date_created,
            'status': self.status,
            'comments': self.comments,
            'users_id': self.users_id,
            'order_items': [order_item.to_dict() for order_item in self.order_items]
        }

    def add_order_items(self, cart_items):
        for cart_item in cart_items:
            order_item = OrderItem(product_id=cart_item.products_id,
                                   product_name=cart_item.product.name,
                                   sku=cart_item.product.sku,
                                   manufacturer=cart_item.product.supplier,
                                   start_date=datetime.now(),
                                   status=self.status,
                                   price=cart_item.unit_price,
                                   quantity=cart_item.quantity,
                                   total_price=cart_item.total_price)
            self.order_items.append(order_item)


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, db.Sequence("order_items_sq", start=1), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))
    orders_id = db.Column(db.Integer, db.ForeignKey(Order.id))
    product_name = db.Column(db.String(length=255), nullable=False)
    sku = db.Column(db.String(length=255), nullable=False)
    manufacturer = db.Column(db.String(length=255), nullable=False)
    start_date = db.Column(db.Date())
    end_date = db.Column(db.Date())
    status = db.Column(db.String(length=40))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)

    def __repr__(self):
        return f"<OrderItem {self.id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'orders_id': self.orders_id,
            'product_name': self.product_name,
            'sku': self.sku,
            'manufacturer': self.manufacturer,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.status,
            'price': self.price,
            'quantity': self.quantity,
            'total_price': self.total_price,
        }
