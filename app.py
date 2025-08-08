import os
import logging
from flask import Flask
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'admin@nikitarasoi.com')

# Initialize extensions
from models import db
db.init_app(app)
mail = Mail(app)

# Import models and routes after initialization
from models import User, Product, Order, Review, Address, VisitorLog, OrderItem
from routes import *

# Create tables and sample data
with app.app_context():
    db.create_all()
    
    # Create default admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        from werkzeug.security import generate_password_hash
        admin = User(
            username='admin',
            email='admin@nikitarasoi.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        
        # Add sample products
        sample_products = [
            {
                'name': 'Artisan Sourdough Bread',
                'description': 'Traditional sourdough bread made with our signature starter, fermented for 24 hours for that perfect tangy flavor.',
                'price': 89.99,
                'category': 'Bread',
                'image_url': 'https://pixabay.com/get/gf46697f3b2eb0f69055e68cf462fe7f12f666a1cef093298d99ac12155b9f9a73786df5c026a3d306610f736380e291652992b984cc3e2305bb1f72dd7b7831a_1280.jpg',
                'stock': 15
            },
            {
                'name': 'Fresh Croissants',
                'description': 'Buttery, flaky croissants made fresh daily with premium French butter. Perfect for breakfast or afternoon tea.',
                'price': 129.99,
                'category': 'Pastries',
                'image_url': 'https://pixabay.com/get/g7fc235a8396e1e878415cdd61ade6fd8a773e2667829a11c6e2118808a681b4abd2a480212ead51ada7e326f7f210cdbe2aac2c1c8a0ce9310ea0497f2c98d88_1280.jpg',
                'stock': 24
            },
            {
                'name': 'Chocolate Chip Muffins',
                'description': 'Moist and fluffy muffins loaded with premium chocolate chips. A family favorite!',
                'price': 159.99,
                'category': 'Muffins',
                'image_url': 'https://pixabay.com/get/g002d90cded0d0d8029098ba11a7e534bc2a16e58b1b935f8abf23e301924125103d7e7aa0971c7d3b6044f125aace9b89bfa10cb192bce99d1393e0914d96939_1280.jpg',
                'stock': 18
            }
        ]
        
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        logging.info("Database initialized with admin user and sample products")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
