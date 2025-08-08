from datetime import datetime
from werkzeug.security import check_password_hash

class User:
    def __init__(self, user_id, username, email, password_hash, is_admin=False, created_at=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = created_at or datetime.now()
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class Product:
    def __init__(self, product_id, name, description, price, category, image_url, stock=0, created_at=None):
        self.id = product_id
        self.name = name
        self.description = description
        self.price = float(price)
        self.category = category
        self.image_url = image_url
        self.stock = int(stock)
        self.created_at = created_at or datetime.now()
    
    def get_average_rating(self):
        from data_store import data_store
        reviews = [r for r in data_store['reviews'].values() if r.product_id == self.id]
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

class Order:
    def __init__(self, order_id, user_id, total, shipping_address, status='pending', items=None, created_at=None):
        self.id = order_id
        self.user_id = user_id
        self.total = float(total)
        self.shipping_address = shipping_address
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = self.created_at
        self.items = items or []  # List of order items
    
    def update_status(self, new_status):
        self.status = new_status
        self.updated_at = datetime.now()

class OrderItem:
    def __init__(self, order_id, product_id, quantity, price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = int(quantity)
        self.price = float(price)

class Review:
    def __init__(self, review_id, product_id, user_id, rating, comment, created_at=None):
        self.id = review_id
        self.product_id = product_id
        self.user_id = user_id
        self.rating = int(rating)
        self.comment = comment
        self.created_at = created_at or datetime.now()

class Address:
    def __init__(self, address_id, user_id, name, street, city, state, zip_code, phone=None, created_at=None):
        self.id = address_id
        self.user_id = user_id
        self.name = name
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.phone = phone
        self.created_at = created_at or datetime.now()

class VisitorLog:
    def __init__(self, ip_address, user_agent, page=None, timestamp=None):
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.page = page
        self.timestamp = timestamp or datetime.now()

class CartItem:
    def __init__(self, product_id, quantity, price):
        self.product_id = product_id
        self.quantity = int(quantity)
        self.price = float(price)
    
    def get_total(self):
        return self.quantity * self.price
