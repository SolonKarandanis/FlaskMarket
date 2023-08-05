from datetime import datetime

from market import app, db
from flask import render_template, redirect, url_for, flash, request
from market.models import Product, User, Cart, CartItem,Order
from market.forms import RegisterForm, LoginForm, ProductListAddToCartForm, ProductAddToCartForm, \
    ProductDetailsAddToCartForm, CartItemsForm, CartItemUpdateForm, PlaceDraftOrderForm
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

        try:
            db.session.commit()
            return redirect(url_for('cart'))
        except:
            flash("Error while adding items to cart")

        return redirect(url_for('market_page'))

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


@app.route('/product/<int:product_id>/', methods=['GET', 'POST'])
@login_required
def product_detail_page(product_id):
    product = db.session.query(Product).options(db.joinedload(Product.types)).filter_by(id=product_id).first()
    product_details_add_to_cart_form = ProductDetailsAddToCartForm()
    if request.method == 'POST':
        user_id = current_user.id
        cart = Cart.query.options(db.joinedload(Cart.cart_items)).filter_by(users_id=user_id).first()
        if cart is None:
            cart = Cart(users_id=user_id,
                        total_price=0,
                        date_created=datetime.now(),
                        cart_items=[])
        quantity = product_details_add_to_cart_form.quantity.data
        cart.add_item_to_cart(product.id, quantity, product.price)
        cart.update_cart_total_price()
        db.session.add(cart)
        try:
            db.session.commit()
            return redirect(url_for('cart'))
        except:
            flash("Error while adding items to cart")
    return render_template('product.html', product=product,
                           product_details_add_to_cart_form=product_details_add_to_cart_form)


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
    place_draft_order_form = PlaceDraftOrderForm()
    user_id = current_user.id
    cart = Cart.query.options(db.joinedload(Cart.cart_items).joinedload(CartItem.product)) \
        .filter_by(users_id=user_id).first()
    if request.method == 'GET':
        cart_items_form = CartItemsForm()
        if cart is None:
            cart = Cart(users_id=user_id,
                        total_price=0,
                        date_created=datetime.now(),
                        date_modified=datetime.now())
            db.session.add(cart)
            try:
                db.session.commit()
            except:
                flash("Error while fetching  cart")

        for cart_item in cart.cart_items:
            cart_item_update_form = CartItemUpdateForm()
            cart_item_update_form.quantity = cart_item.quantity
            cart_items_form.cart_items.append_entry(cart_item_update_form)
        return render_template('cart.html', cart=cart, cart_items_form=cart_items_form,
                               place_draft_order_form=place_draft_order_form)

    if place_draft_order_form.validate_on_submit():
        order_comments = place_draft_order_form.comments.data


@app.post('/cart/<int:item_id>/delete/')
@login_required
def delete_cart_item(item_id):
    user_id = current_user.id
    cart = Cart.query.options(db.joinedload(Cart.cart_items)).filter_by(users_id=user_id).first()
    cart_item = next(filter(lambda ci: ci.id == item_id, cart.cart_items), None)
    db.session.delete(cart_item)
    cart.update_cart_total_price()
    try:
        db.session.commit()
    except:
        flash("Error while deleting item from cart")
    return redirect(url_for('cart'))


@app.post('/cart/<int:item_id>/update/')
@login_required
def update_cart_item_quantity(item_id):
    user_id = current_user.id
    cart = Cart.query.options(db.joinedload(Cart.cart_items)).filter_by(users_id=user_id).first()
    quantity = int(request.form.get(f'cart_items-{item_id - 1}-quantity'))
    cart.update_item_quantity(item_id, quantity)
    cart.update_cart_total_price()
    db.session.add(cart)
    try:
        db.session.commit()
    except:
        flash("Error while updating item in cart")
    return redirect(url_for('cart'))


@app.route('/order', methods=['GET', 'POST'])
@login_required
def place_draft_order():
    user_id = current_user.id
    order = Order.query.options(db.joinedload(Order.order_items)).filter_by(users_id=user_id).first()



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

# q = session.query(Item.id).filter(Item.email==email)
# session.query(q.exists()).scalar()    # returns True or False
