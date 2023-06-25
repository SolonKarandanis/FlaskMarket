from datetime import datetime

from market import app, db
from flask import render_template, redirect, url_for, flash, request
from market.models import Product, User, Cart, CartItem
from market.forms import RegisterForm, LoginForm, ProductListAddToCartForm, ProductAddToCartForm
from flask_login import login_user, logout_user, login_required, current_user
import logging

logger = logging.getLogger(__name__)


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


# user = session.query(User).filter_by(name=name).first()
@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(Product).order_by(Product.id).paginate(page=page, per_page=5)
    logger.info('Loaded products')
    productList_form = ProductListAddToCartForm()

    if request.method == 'POST':
        user_id = current_user.id
        cart = Cart.query.options(db.joinedload(Cart.cart_items)).filter_by(users_id=user_id).first()
        if cart is None:
            cart = Cart(users_id=user_id,
                        total_price=0,
                        date_created=datetime.now(),
                        cart_items=[])

        for product, product_form in zip(pagination.items, productList_form.products):
            is_selected = product_form.selected.data
            quantity = product_form.quantity.data
            if is_selected:
                cart.add_item_to_cart(product.id, quantity, product.price)
        cart.update_cart_total_price()
        db.session.add(cart)
        db.session.commit()

        return redirect(url_for('cart'))

    for product in pagination.items:
        product_form = ProductAddToCartForm()
        product_form.selected = False
        product_form.id = product.id
        product_form.sku = product.sku
        product_form.name = product.name
        product_form.supplier = product.supplier
        product_form.description = product.description
        product_form.price = product.price
        productList_form.products.append_entry(product_form)
    return render_template('market.html', productList_form=productList_form, pagination=pagination)


@app.route('/product/<int:product_id>/', methods=['GET'])
@login_required
def product_detail_page(product_id):
    product = db.session.query(Product).options(db.joinedload(Product.types)).filter_by(id=product_id).first()
    return render_template('product.html', product=product)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('market_page'))
    if form.errors != {}:  # If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # Declare the login form
    form = LoginForm()
    # Apply all validations defined in the form
    if form.validate_on_submit():
        # recover form information
        attempted_username = form.username.data
        attempted_password = form.password.data

        attempted_user = User.query.filter_by(username=attempted_username).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password
        ):
            login_user(attempted_user)
            logger.info(f'User logged in as: {attempted_user.username}')
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form)


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    if request.method == 'GET':
        user_id = current_user.id
        cart = Cart.query.options(db.joinedload(Cart.cart_items).joinedload(CartItem.product)) \
            .filter_by(users_id=user_id).first()
        if cart is None:
            cart = Cart(users_id=user_id,
                        total_price=0,
                        date_created=datetime.now(),
                        date_modified=datetime.now())
            db.session.add(cart)
            db.session.commit()
        return render_template('cart.html', cart=cart)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out", category='info')
    return redirect(url_for('home_page'))


# Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(error):
    return render_template("500.html"), 500

# @app.route('/create/', methods=('GET', 'POST'))
# def create():
#     if request.method == 'POST':
#         firstname = request.form['firstname']
#         lastname = request.form['lastname']
#         email = request.form['email']
#         age = int(request.form['age'])
#         bio = request.form['bio']
#         student = Student(firstname=firstname,
#                           lastname=lastname,
#                           email=email,
#                           age=age,
#                           bio=bio)
#         db.session.add(student)
#         db.session.commit()
#
#         return redirect(url_for('index'))
#
#     return render_template('create.html')

# @app.route('/<int:student_id>/edit/', methods=('GET', 'POST'))
# def edit(student_id):
#     student = Student.query.get_or_404(student_id)
#
#     if request.method == 'POST':
#         firstname = request.form['firstname']
#         lastname = request.form['lastname']
#         email = request.form['email']
#         age = int(request.form['age'])
#         bio = request.form['bio']
#
#         student.firstname = firstname
#         student.lastname = lastname
#         student.email = email
#         student.age = age
#         student.bio = bio
#
#         db.session.add(student)
#         db.session.commit()
#
#         return redirect(url_for('index'))
#
#     return render_template('edit.html', student=student)

# @app.post('/<int:student_id>/delete/')
# def delete(student_id):
#     student = Student.query.get_or_404(student_id)
#     db.session.delete(student)
#     db.session.commit()
#     return redirect(url_for('index'))

# q = session.query(Item.id).filter(Item.email==email)
# session.query(q.exists()).scalar()    # returns True or False
