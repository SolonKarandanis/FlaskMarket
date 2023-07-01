from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, FloatField, \
    FieldList, FormField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from market.models import User


class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists!')

    def validate_email_address(self, email_to_check):
        user = User.query.filter_by(email_address=email_to_check.data).first()
        if user:
            raise ValidationError('Email already exists!')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[
        Email(message='Not a valid email address.'), DataRequired()
    ])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[
        EqualTo('password1', message='Passwords must match.'), DataRequired()
    ])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class ProductAddToCartForm(FlaskForm):
    selected = BooleanField()
    quantity = IntegerField()


class ProductListAddToCartForm(FlaskForm):
    products = FieldList(FormField(ProductAddToCartForm))
    add_to_cart = SubmitField('Add to Cart')


class ProductDetailsAddToCartForm(FlaskForm):
    quantity = IntegerField()
    add_to_cart = SubmitField('Add to Cart')

class UpdateCartItemForm(FlaskForm):
    quantity = IntegerField()
    update = SubmitField('Update cart')