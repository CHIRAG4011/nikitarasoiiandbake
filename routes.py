from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from models import User, Product, Order, Review, Address, OrderItem, VisitorLog, Category
from data_store import data_store, add_visitor_log, get_next_id, get_weekly_visitors
from utils import (get_current_user, add_to_cart, remove_from_cart, update_cart_quantity, 
                  get_cart_total, get_cart_count, clear_cart, send_order_confirmation_email,
                  calculate_order_stats, search_products, get_cart)
import logging
from datetime import datetime
import json

@app.before_request
def log_visitor():
    """Log visitor information"""
    if request.endpoint not in ['static']:
        try:
            add_visitor_log(
                request.remote_addr,
                request.headers.get('User-Agent', ''),
                request.endpoint
            )
        except Exception as e:
            # If visitor logging fails, don't break the app
            logging.warning(f"Failed to log visitor: {e}")

@app.context_processor
def inject_globals():
    """Inject global variables into templates"""
    return {
        'current_user': get_current_user(),
        'cart_count': get_cart_count(),
        'cart_total': get_cart_total(),
        'data_store': data_store
    }

@app.route('/')
def index():
    """Home page"""
    # Get first 6 products as featured
    featured_products = list(data_store['products'].values())[:6]
    return render_template('index.html', featured_products=featured_products)

@app.route('/products')
def products():
    """Products page with search and filter"""
    query = request.args.get('q', '')
    category = request.args.get('category', 'all')
    
    if query or category != 'all':
        product_list = search_products(query, category)
    else:
        product_list = list(data_store['products'].values())
    
    # Get categories from data store
    categories = [cat.name for cat in data_store['categories'].values() if cat.is_active]
    
    return render_template('products.html', 
                         products=product_list, 
                         categories=categories,
                         current_query=query,
                         current_category=category)

@app.route('/categories')
def categories():
    """Categories page showing all available categories"""
    active_categories = [cat for cat in data_store['categories'].values() if cat.is_active]
    return render_template('categories.html', categories=active_categories)

@app.route('/category/<category_name>')
def category_products(category_name):
    """Show products for a specific category"""
    # Get the category object
    category = None
    for cat in data_store['categories'].values():
        if cat.name == category_name and cat.is_active:
            category = cat
            break
    
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('products'))
    
    # Get products for this category
    category_products = [p for p in data_store['products'].values() if p.category == category_name]
    
    return render_template('category_products.html', 
                         category=category, 
                         products=category_products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = data_store['products'].get(product_id)
    if not product:
        from flask import abort
        abort(404)
    
    # Get reviews for this product
    product_reviews = [r for r in data_store['reviews'].values() if r.product_id == product_id]
    
    return render_template('product_detail.html', product=product, reviews=product_reviews)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart_route(product_id):
    """Add item to cart"""
    quantity = int(request.form.get('quantity', 1))
    
    if add_to_cart(product_id, quantity):
        flash('Item added to cart!', 'success')
    else:
        flash('Unable to add item to cart. Please check availability.', 'error')
    
    return redirect(request.referrer or url_for('products'))

@app.route('/cart')
def cart():
    """Shopping cart page"""
    cart_items = []
    cart_data = get_cart()
    
    for product_id_str, item_data in cart_data.items():
        product_id = int(product_id_str)
        product = data_store['products'].get(product_id)
        if product:
            cart_items.append({
                'product': product,
                'quantity': item_data['quantity'],
                'total': item_data['quantity'] * item_data['price']
            })
    
    return render_template('cart.html', cart_items=cart_items)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart quantities"""
    product_id = int(request.form.get('product_id', '0'))
    quantity = int(request.form.get('quantity', '1'))
    
    if update_cart_quantity(product_id, quantity):
        flash('Cart updated!', 'success')
    else:
        flash('Unable to update cart.', 'error')
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart_route(product_id):
    """Remove item from cart"""
    if remove_from_cart(product_id):
        flash('Item removed from cart!', 'success')
    else:
        flash('Unable to remove item.', 'error')
    
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    """Checkout page"""
    user = get_current_user()
    if not user:
        flash('Please login to checkout.', 'error')
        return redirect(url_for('login'))
    
    cart_data = get_cart()
    if not cart_data:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart'))
    
    # Get user addresses
    user_addresses = [addr for addr in data_store['addresses'].values() 
                     if addr.user_id == user.id]
    
    # Calculate final amount
    cart_total = get_cart_total()
    delivery_fee = 50.00
    tax_amount = (cart_total + delivery_fee) * 0.18
    final_amount = cart_total + delivery_fee + tax_amount
    
    return render_template('checkout.html', 
                         addresses=user_addresses,
                         final_amount=final_amount)

@app.route('/place_order', methods=['POST'])
def place_order():
    """Process order placement with QR code or COD payment"""
    user = get_current_user()
    if not user:
        flash('Please login to place an order.', 'error')
        return redirect(url_for('login'))
    
    cart_data = get_cart()
    if not cart_data:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart'))
    
    # Get shipping address
    address_id = request.form.get('address_id')
    new_address = request.form.get('new_address')
    payment_method = request.form.get('payment_method', 'qr_payment')
    
    if address_id:
        address = data_store['addresses'].get(int(address_id))
        if address:
            shipping_address = f"{address.name}, {address.street}, {address.city}, {address.state} {address.zip_code}"
        else:
            flash('Selected address not found.', 'error')
            return redirect(url_for('checkout'))
    elif new_address and new_address.strip():
        shipping_address = new_address.strip()
    else:
        flash('Please provide a delivery address to continue.', 'error')
        return redirect(url_for('checkout'))
    
    # Calculate final amount
    cart_total = get_cart_total()
    delivery_fee = 50.00
    tax_amount = (cart_total + delivery_fee) * 0.18
    final_amount = cart_total + delivery_fee + tax_amount
    
    # Add COD charges for cash on delivery
    if payment_method == 'cash_on_delivery':
        final_amount += 20.00  # COD handling charges
    
    # Create order items and validate stock
    order_items = []
    
    for product_id_str, item_data in cart_data.items():
        product_id = int(product_id_str)
        product = data_store['products'].get(product_id)
        
        if not product or product.stock < item_data['quantity']:
            flash(f'Insufficient stock for {product.name if product else "unknown item"}.', 'error')
            return redirect(url_for('cart'))
        
        order_items.append({
            'product_id': product_id,
            'quantity': item_data['quantity'],
            'price': item_data['price']
        })
        
        # Update stock
        product.stock -= item_data['quantity']
    
    # Create order
    order_id = get_next_id('order_id')
    
    # Set order status based on payment method
    if payment_method == 'cash_on_delivery':
        status = 'pending'
    else:
        status = 'payment_pending'  # Waiting for QR payment confirmation
    
    order = Order(
        order_id=order_id,
        user_id=user.id,
        items=order_items,
        total=final_amount,
        shipping_address=shipping_address,
        status=status
    )
    
    # Add payment method info
    order.payment_method = payment_method
    
    data_store['orders'][order_id] = order
    
    # Send confirmation email (but catch any errors)
    try:
        send_order_confirmation_email(user.email, order)
    except Exception as e:
        logging.warning(f"Failed to send confirmation email: {e}")
    
    # Clear cart
    clear_cart()
    
    # Redirect based on payment method
    if payment_method == 'cash_on_delivery':
        flash(f'Order #{order_id} placed successfully! Payment will be collected on delivery.', 'success')
        return redirect(url_for('order_tracking', order_id=order_id))
    else:
        # Redirect to QR payment page
        session['payment_order_id'] = order_id
        session['payment_amount'] = final_amount
        return redirect(url_for('qr_payment'))

@app.route('/qr_payment')
def qr_payment():
    """QR code payment page"""
    user = get_current_user()
    if not user:
        flash('Please login to continue.', 'error')
        return redirect(url_for('login'))
    
    order_id = session.get('payment_order_id')
    amount = session.get('payment_amount')
    
    if not order_id or not amount:
        flash('Invalid payment session.', 'error')
        return redirect(url_for('index'))
    
    # Get order details
    order = data_store['orders'].get(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('index'))
    
    return render_template('qr_payment.html', 
                         order_id=order_id, 
                         amount=amount,
                         order=order)

@app.route('/confirm_payment/<int:order_id>', methods=['POST'])
def confirm_payment(order_id):
    """Confirm QR code payment"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Please login to proceed'}), 401
    
    order = data_store['orders'].get(order_id)
    if not order or order.user_id != user.id:
        return jsonify({'error': 'Order not found'}), 404
    
    # Update order status to paid
    order.status = 'confirmed'
    order.updated_at = datetime.now()
    
    # Clear payment session
    session.pop('payment_order_id', None)
    session.pop('payment_amount', None)
    
    flash(f'Payment confirmed! Order #{order_id} is now being processed.', 'success')
    return jsonify({'success': True, 'redirect': url_for('order_tracking', order_id=order_id)})

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        # Check if user exists
        existing_user = None
        for user_obj in data_store['users'].values():
            if user_obj.username == username or user_obj.email == email:
                existing_user = user_obj
                break
        
        if existing_user:
            flash('Username or email already exists.', 'error')
            return render_template('auth/register.html')
        
        # Create user
        from data_store import get_next_id
        user_id = get_next_id('user_id')
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=generate_password_hash(password or '')
        )
        
        data_store['users'][user_id] = user
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user
        user = None
        for user_obj in data_store['users'].values():
            if user_obj.username == username or user_obj.email == username:
                user = user_obj
                break
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username/email or password.', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user_id', None)
    session.pop('cart', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    """User profile page"""
    user = get_current_user()
    if not user:
        flash('Please login to view your profile.', 'error')
        return redirect(url_for('login'))
    
    # Get user addresses
    user_addresses = [addr for addr in data_store['addresses'].values() if addr.user_id == user.id]
    
    return render_template('user/profile.html', addresses=user_addresses)

@app.route('/add_address', methods=['POST'])
def add_address():
    """Add a new address"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    from data_store import get_next_id
    address_id = get_next_id('address_id')
    address = Address(
        address_id=address_id,
        user_id=user.id,
        name=request.form.get('name'),
        street=request.form.get('street'),
        city=request.form.get('city'),
        state=request.form.get('state'),
        zip_code=request.form.get('zip_code')
    )
    
    data_store['addresses'][address_id] = address
    flash('Address added successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/orders')
def user_orders():
    """User orders page"""
    user = get_current_user()
    if not user:
        flash('Please login to view your orders.', 'error')
        return redirect(url_for('login'))
    
    user_orders_list = [order for order in data_store['orders'].values() if order.user_id == user.id]
    
    user_orders_list.sort(key=lambda x: x.created_at, reverse=True)
    
    return render_template('user/orders.html', orders=user_orders_list)

@app.route('/order/<int:order_id>')
def order_tracking(order_id):
    """Order tracking page"""
    order = data_store['orders'].get(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('user_orders'))
    
    user = get_current_user()
    if not user or (order.user_id != user.id and not user.is_admin):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('index'))
    
    # Get order items with product details
    order_items = []
    for item in order.items:
        product = data_store['products'].get(item['product_id'])
        if product:
            order_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': item['price'],
                'total': item['quantity'] * item['price']
            })
    
    return render_template('user/order_detail.html', order=order, order_items=order_items)

@app.route('/add_review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    """Add a product review"""
    user = get_current_user()
    if not user:
        flash('Please login to add a review.', 'error')
        return redirect(url_for('login'))
    
    rating = int(request.form.get('rating', '1'))
    comment = request.form.get('comment')
    
    from data_store import get_next_id
    review_id = get_next_id('review_id')
    review = Review(
        review_id=review_id,
        product_id=product_id,
        user_id=user.id,
        rating=rating,
        comment=comment
    )
    
    data_store['reviews'][review_id] = review
    flash('Review added successfully!', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

# Admin routes
@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    stats = calculate_order_stats()
    from data_store import get_daily_visitors
    daily_visitors = get_daily_visitors()
    recent_orders = list(data_store['orders'].values())
    recent_orders.sort(key=lambda x: x.created_at, reverse=True)
    recent_orders = recent_orders[:10]
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         daily_visitors=daily_visitors,
                         recent_orders=recent_orders)

@app.route('/admin/products')
def admin_products():
    """Admin products management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    products = list(data_store['products'].values())
    categories = list(data_store['categories'].values())
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/add_product', methods=['POST'])
def admin_add_product():
    """Add a new product"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    product_id = get_next_id('product_id')
    product = Product(
        product_id=product_id,
        name=request.form.get('name'),
        description=request.form.get('description'),
        price=float(request.form.get('price', '0')),
        category=request.form.get('category'),
        image_url=request.form.get('image_url'),
        stock=int(request.form.get('stock', '0'))
    )
    
    data_store['products'][product_id] = product
    flash('Product added successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/update_stock/<int:product_id>', methods=['POST'])
def admin_update_stock(product_id):
    """Update product stock"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    product = data_store['products'].get(product_id)
    if product:
        product.stock = int(request.form.get('stock', '0'))
        flash('Stock updated successfully!', 'success')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/edit_product', methods=['POST'])
def admin_edit_product():
    """Edit an existing product"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    product_id_str = request.form.get('product_id')
    if not product_id_str:
        flash('Product ID is required.', 'error')
        return redirect(url_for('admin_products'))
    product_id = int(product_id_str)
    product = data_store['products'].get(product_id)
    
    if product:
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price', '0'))
        product.category = request.form.get('category')
        product.image_url = request.form.get('image_url')
        product.stock = int(request.form.get('stock', '0'))
        flash('Product updated successfully!', 'success')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
def admin_orders():
    """Admin orders management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    orders = list(data_store['orders'].values())
    orders.sort(key=lambda x: x.created_at, reverse=True)
    
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
def admin_update_order_status(order_id):
    """Update order status"""
    user = get_current_user()
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    
    order = data_store['orders'].get(order_id)
    if order:
        new_status = request.form.get('status')
        order.update_status(new_status)
        flash('Order status updated successfully!', 'success')
    
    return redirect(url_for('admin_orders'))

@app.route('/admin/analytics')
def admin_analytics():
    """Admin analytics page"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    weekly_visitors = get_weekly_visitors()
    stats = calculate_order_stats()
    
    return render_template('admin/analytics.html', 
                         weekly_visitors=weekly_visitors,
                         stats=stats)

# Admin User Management
@app.route('/admin/users')
def admin_users():
    """Admin user management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    users = list(data_store['users'].values())
    return render_template('admin/users.html', users=users)

@app.route('/admin/categories')
def admin_categories():
    """Admin category management"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    categories = list(data_store['categories'].values())
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/add_category', methods=['GET', 'POST'])
def admin_add_category():
    """Add new category"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        if not name:
            flash('Category name is required.', 'error')
            return render_template('admin/add_category.html')
        
        # Check if category name already exists
        existing_category = None
        for cat in data_store['categories'].values():
            if cat.name.lower() == name.lower():
                existing_category = cat
                break
        
        if existing_category:
            flash('Category with this name already exists.', 'error')
            return render_template('admin/add_category.html')
        
        # Create new category
        category_id = get_next_id('category_id')
        new_category = Category(
            category_id=category_id,
            name=name,
            description=description,
            image_url=image_url
        )
        
        data_store['categories'][category_id] = new_category
        flash(f'Category "{name}" added successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/add_category.html')

@app.route('/admin/edit_category/<int:category_id>', methods=['GET', 'POST'])
def admin_edit_category(category_id):
    """Edit existing category"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    category = data_store['categories'].get(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin_categories'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        if not name:
            flash('Category name is required.', 'error')
            return render_template('admin/edit_category.html', category=category)
        
        # Check if category name already exists (excluding current category)
        existing_category = None
        for cat in data_store['categories'].values():
            if cat.name.lower() == name.lower() and cat.id != category_id:
                existing_category = cat
                break
        
        if existing_category:
            flash('Category with this name already exists.', 'error')
            return render_template('admin/edit_category.html', category=category)
        
        # Update category
        category.name = name
        category.description = description
        category.image_url = image_url
        category.is_active = is_active
        
        flash(f'Category "{name}" updated successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/edit_category.html', category=category)

@app.route('/admin/toggle_category_status/<int:category_id>', methods=['POST'])
def admin_toggle_category_status(category_id):
    """Toggle category active status"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    category = data_store['categories'].get(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin_categories'))
    
    category.is_active = not category.is_active
    status = "activated" if category.is_active else "deactivated"
    flash(f'Category "{category.name}" {status} successfully!', 'success')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/delete_category/<int:category_id>', methods=['POST', 'GET'])
def admin_delete_category(category_id):
    """Delete a category"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    category = data_store['categories'].get(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin_categories'))
    
    # Check if category has products
    products_in_category = [p for p in data_store['products'].values() if p.category == category.name]
    if products_in_category:
        flash(f'Cannot delete category "{category.name}" because it contains {len(products_in_category)} products. Please move or delete these products first.', 'error')
        return redirect(url_for('admin_categories'))
    
    # Delete the category
    category_name = category.name
    del data_store['categories'][category_id]
    flash(f'Category "{category_name}" deleted successfully!', 'success')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    """Delete a product"""
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    product = data_store['products'].get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_products'))
    
    # Delete associated reviews
    reviews_to_delete = [r_id for r_id, review in data_store['reviews'].items() if review.product_id == product_id]
    for review_id in reviews_to_delete:
        del data_store['reviews'][review_id]
    
    # Delete the product
    product_name = product.name
    del data_store['products'][product_id]
    flash(f'Product "{product_name}" and its {len(reviews_to_delete)} reviews deleted successfully!', 'success')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
def toggle_admin(user_id):
    """Toggle admin privileges for a user"""
    current_user = get_current_user()
    if not current_user or not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    target_user = data_store['users'].get(user_id)
    if not target_user:
        from flask import abort
        abort(404)
    
    # Prevent removing admin from yourself
    if target_user.id == current_user.id:
        flash('You cannot remove admin privileges from yourself.', 'error')
        return redirect(url_for('admin_users'))
    
    target_user.is_admin = not target_user.is_admin
    # No commit needed for in-memory storage
    
    action = 'granted' if target_user.is_admin else 'removed'
    flash(f'Admin privileges {action} for {target_user.username}.', 'success')
    return redirect(url_for('admin_users'))
