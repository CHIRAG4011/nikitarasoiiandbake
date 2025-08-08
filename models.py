from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, user_id, username, email, password_hash, is_admin=False):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = datetime.now()
        self.addresses = []
    
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
    def __init__(self, product_id, name, description, price, category, image_url, stock=0):
        self.id = product_id
        self.name = name
        self.description = description
        self.price = float(price)
        self.category = category
        self.image_url = image_url
        self.stock = int(stock)
        self.created_at = datetime.now()
        self.reviews = []
    
    def get_average_rating(self):
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

class Order:
    def __init__(self, order_id, user_id, items, total, shipping_address, status='pending'):
        self.id = order_id
        self.user_id = user_id
        self.items = items  # List of {'product_id', 'quantity', 'price'}
        self.total = float(total)
        self.shipping_address = shipping_address
        self.status = status  # pending, confirmed, preparing, out_for_delivery, delivered, cancelled
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_status(self, new_status):
        self.status = new_status
        self.updated_at = datetime.now()

class Review:
    def __init__(self, review_id, product_id, user_id, rating, comment):
        self.id = review_id
        self.product_id = product_id
        self.user_id = user_id
        self.rating = int(rating)
        self.comment = comment
        self.created_at = datetime.now()

class CartItem:
    def __init__(self, product_id, quantity, price):
        self.product_id = product_id
        self.quantity = int(quantity)
        self.price = float(price)
    
    def get_total(self):
        return self.quantity * self.price

class Address:
    def __init__(self, address_id, user_id, name, street, city, state, zip_code, phone):
        self.id = address_id
        self.user_id = user_id
        self.name = name
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.phone = phone

class VisitorLog:
    def __init__(self, ip_address, user_agent, timestamp=None):
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.timestamp = timestamp or datetime.now()
