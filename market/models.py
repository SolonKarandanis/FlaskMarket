from typing import Set

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


class Product(ProductTypeBase):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(length=255), nullable=False)
    name = db.Column(db.String(length=30), nullable=False)
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


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Float)
    modification_alert = db.Column(db.Boolean())
    date_created = db.Column(db.DateTime(timezone=True))
    date_modified = db.Column(db.DateTime(timezone=True))
    cart_items = db.relationship('CartItem', backref="cart")


    def __repr__(self):
        return f"<Cart {self.id}>"


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    modification_alert = db.Column(db.Boolean())
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    carts_id = db.Column(db.Integer, db.ForeignKey(Cart.id))
    products_id = db.Column(db.Integer, db.ForeignKey(Product.id))

    def __repr__(self):
        return f"<CartItem {self.id}>"


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.Date())
    status = db.Column(db.String(length=40))
    total_price = db.Column(db.Float)

    def __repr__(self):
        return f"<Order {self.id}>"
