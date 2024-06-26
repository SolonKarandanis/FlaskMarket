from datetime import datetime

from market import app, db
from flask import render_template, redirect, url_for, flash, request
from flask_babel import _

from market.data_access import product_repo, order_repo
from market.forms import RegisterForm, LoginForm, ProductListAddToCartForm, ProductAddToCartForm, \
    ProductDetailsAddToCartForm, CartItemsForm, CartItemUpdateForm, PlaceDraftOrderForm, ResetPasswordRequestForm, \
    ResetPasswordForm
from flask_login import login_user, logout_user, login_required, current_user
import logging

from market.services import email_service, cart_service, user_service

logger = logging.getLogger(__name__)


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    page = request.args.get('page', 1, type=int)
    pagination = product_repo.find_all_pageable(page)
    logger.info('Loaded products')
    productList_form = ProductListAddToCartForm()

    if request.method == 'POST':
        user_id = current_user.id
        cart = cart_service.find_with_items_by_user_id(user_id)
        if cart is None:
            cart = cart_service.create(user_id)

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
            flash(_("Error while adding items to cart"))

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
    product = product_repo.find_by_id(product_id)
    product_details_add_to_cart_form = ProductDetailsAddToCartForm()
    if request.method == 'POST':
        user_id = current_user.id
        cart = cart_service.find_with_items_by_user_id(user_id)
        if cart is None:
            cart = cart_service.create(user_id)
        quantity = product_details_add_to_cart_form.quantity.data
        cart.add_item_to_cart(product.id, quantity, product.price)
        db.session.add(cart)
        try:
            db.session.commit()
            return redirect(url_for('cart'))
        except:
            flash(_("Error while adding items to cart"))
    return render_template('product.html', product=product,
                           product_details_add_to_cart_form=product_details_add_to_cart_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = user_service.create(form.username.data, form.email_address.data, form.password1.data)
        db.session.commit()
        return redirect(url_for('market_page'))
    if form.errors != {}:  # If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(_('There was an error with creating a user: {err}'.format(err=err_msg)), category='danger')

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

        attempted_user = user_service.find_by_username(attempted_username)
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


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = user_service.find_by_email(form.email.data)
        if user:
            email_service.send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login_page'))
    return render_template('reset_password_request.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    user = user_service.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home_page'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/user')
@login_required
def profile_page():
    user = current_user
    return render_template('profile.html', user=user)


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    place_draft_order_form = PlaceDraftOrderForm()
    user_id = current_user.id
    cart = cart_service.find_with_items_and_products_by_user_id(user_id)
    if request.method == 'GET':
        cart_items_form = CartItemsForm()
        if cart is None:
            cart = cart_service.create(user_id)
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
        order = order_repo.create(user_id, cart.total_price, order_comments)
        cart_items = cart.cart_items
        order.add_order_items(cart_items)
        db.session.add(order)
        cart.clear_cart()
        db.session.add(cart)
        try:
            db.session.commit()

        except:
            flash("Error while creating  order")
        return redirect(url_for('order_detail_page', order_id=order.id))


@app.post('/cart/<int:item_id>/delete/')
@login_required
def delete_cart_item(item_id):
    user_id = current_user.id
    cart = cart_service.find_with_items_by_user_id(user_id)
    cart_item = next(filter(lambda ci: ci.id == item_id, cart.cart_items), None)
    cart.remove_from_cart(cart_item)
    db.session.add(cart)
    try:
        db.session.commit()
    except:
        flash("Error while deleting item from cart")
    return redirect(url_for('cart'))


@app.post('/cart/<int:item_id>/update/')
@login_required
def update_cart_item_quantity(item_id):
    user_id = current_user.id
    cart = cart_service.find_with_items_by_user_id(user_id)
    s = request.form.get(f'cart_items-{item_id - 1}-quantity')
    logger.info(f's: {request.form}')
    quantity = int(request.form.get(f'cart_items-{item_id - 1}-quantity'))
    cart.update_item_quantity(item_id, quantity)
    db.session.add(cart)
    try:
        db.session.commit()
    except:
        flash("Error while updating item in cart")
    return redirect(url_for('cart'))


@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def order_detail_page(order_id):
    user_id = current_user.id
    order = order_repo.find_by_user_and_id(user_id, order_id)
    return render_template('order_details.html', order=order)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out", category='info')
    return redirect(url_for('home_page'))

# q = session.query(Item.id).filter(Item.email==email)
# session.query(q.exists()).scalar()    # returns True or False

# @app.route('/api/data')
# def data():
#    return {'data': [user.to_dict() for user in User.query]}

# @app.route('/api/data')
# def data():
#    query = User.query

#    total_filtered = query.count()

# pagination
#    start = request.args.get('start', type=int)
#    length = request.args.get('length', type=int)
#    query = query.offset(start).limit(length)

# response
#    return {
#        'data': [user.to_dict() for user in query],
#        'recordsFiltered': total_filtered,
#        'recordsTotal': User.query.count(),
#        'draw': request.args.get('draw', type=int),
#    }
