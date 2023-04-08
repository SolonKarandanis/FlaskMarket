from market import db
from market import bcrypt


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=30), unique=True, nullable=False)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    products = db.relationship('Product', backref='owned_user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self,plain_text_password):
        self.password_hash=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

class ProductType(db.Model):
    __tablename__ = 'product_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)

    def __repr__(self):
        return f"<ProductType {self.name}>"


class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    supplier = db.Column(db.String(length=30), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<Product {self.name}>"
