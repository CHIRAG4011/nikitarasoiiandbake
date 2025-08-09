from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from models import User, Product, Order, Review, Address, VisitorLog, Category

# In-memory data storage
data_store = {
    'users': {},
    'products': {},
    'orders': {},
    'reviews': {},
    'addresses': {},
    'categories': {},
    'visitor_logs': [],
    'counters': {
        'user_id': 1,
        'product_id': 1,
        'order_id': 1,
        'review_id': 1,
        'address_id': 1,
        'category_id': 1
    }
}

def init_data_store():
    """Initialize the data store with sample data"""
    
    # Create admin user
    admin_user = User(
        user_id=1,
        username='admin',
        email='admin@nikitarasoi.com',
        password_hash=generate_password_hash('admin123'),
        is_admin=True
    )
    data_store['users'][1] = admin_user
    data_store['counters']['user_id'] = 2
    
    # Initialize categories
    categories_data = [
        {
            'name': 'Bread',
            'description': 'Fresh artisan breads, rolls, and baked goods made daily with premium ingredients.',
            'image_url': 'https://pixabay.com/get/gf46697f3b2eb0f69055e68cf462fe7f12f666a1cef093298d99ac12155b9f9a73786df5c026a3d306610f736380e291652992b984cc3e2305bb1f72dd7b7831a_1280.jpg'
        },
        {
            'name': 'Pastries',
            'description': 'Buttery, flaky pastries and croissants made with traditional French techniques.',
            'image_url': 'https://pixabay.com/get/g7fc235a8396e1e878415cdd61ade6fd8a773e2667829a11c6e2118808a681b4abd2a480212ead51ada7e326f7f210cdbe2aac2c1c8a0ce9310ea0497f2c98d88_1280.jpg'
        },
        {
            'name': 'Muffins',
            'description': 'Moist and fluffy muffins with various flavors and mix-ins to start your day right.',
            'image_url': 'https://pixabay.com/get/g002d90cded0d0d8029098ba11a7e534bc2a16e58b1b935f8abf23e301924125103d7e7aa0971c7d3b6044f125aace9b89bfa10cb192bce99d1393e0914d96939_1280.jpg'
        },
        {
            'name': 'Desserts',
            'description': 'Decadent desserts, tarts, and sweet treats perfect for any special occasion.',
            'image_url': 'https://pixabay.com/get/g686d80765ed6bf3ee31605efc8f64b836790a4a5520e1d6c6612c4093dabbe17dfec22312d97234015f0cd6a400527d092ea3a0603e2b30529c4cd59a2f45308_1280.jpg'
        }
    ]
    
    for i, category_data in enumerate(categories_data, 1):
        category = Category(
            category_id=i,
            name=category_data['name'],
            description=category_data['description'],
            image_url=category_data['image_url']
        )
        data_store['categories'][i] = category
    
    data_store['counters']['category_id'] = len(categories_data) + 1
    
    # Sample products with stock photos
    products_data = [
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
        },
        {
            'name': 'Danish Pastries',
            'description': 'Traditional Danish pastries with various fillings including cream cheese, fruit preserves, and custard.',
            'price': 189.99,
            'category': 'Pastries',
            'image_url': 'https://pixabay.com/get/gaffffc737998f81ca3a19e76aa6ff9177b067d35a05e7f8c25e830c8deac60f5febbf4447fe4bc429641c026c2764c8c508a364e12bc0e06b6a6b6b4196335fd_1280.jpg',
            'stock': 12
        },
        {
            'name': 'Whole Wheat Rolls',
            'description': 'Healthy whole wheat dinner rolls, perfect for any meal. Made with organic flour and seeds.',
            'price': 69.99,
            'category': 'Bread',
            'image_url': 'https://pixabay.com/get/ge311c6a94d5e6e9d79f52733a022bfded80843d182c630b20a3b3b4c6df7bb33f610ab05806b5193f036f3cfb9bb1b651bb14c71317129c47140528a6e49e7e6_1280.jpg',
            'stock': 20
        },
        {
            'name': 'Cinnamon Rolls',
            'description': 'Soft, gooey cinnamon rolls with cream cheese frosting. Baked fresh every morning.',
            'price': 149.99,
            'category': 'Pastries',
            'image_url': 'https://pixabay.com/get/ge4a523739a8b375a4398fa7e3e9fa0b5fa31395997465b711435e0fd5a022c2ff5e600d688fd11addd7e9b811f542ce892b7db1d407390227e4cfda1bbf477dd_1280.jpg',
            'stock': 16
        },
        {
            'name': 'Artisan Bagels',
            'description': 'Hand-rolled bagels available in various flavors: plain, sesame, poppy seed, and everything.',
            'price': 99.99,
            'category': 'Bread',
            'image_url': 'https://pixabay.com/get/g16dc05f5f036ac44088b8762b08a8f4fba9c3d54104d0f05f20405769619f798061a01280002dbcbb5a47914af1b25e6436eb32bcd4cb4682d88c658e14ff435_1280.jpg',
            'stock': 22
        },
        {
            'name': 'Fruit Tarts',
            'description': 'Beautiful individual fruit tarts with pastry cream and fresh seasonal fruits.',
            'price': 229.99,
            'category': 'Desserts',
            'image_url': 'https://pixabay.com/get/g686d80765ed6bf3ee31605efc8f64b836790a4a5520e1d6c6612c4093dabbe17dfec22312d97234015f0cd6a400527d092ea3a0603e2b30529c4cd59a2f45308_1280.jpg',
            'stock': 8
        }
    ]
    
    for i, product_data in enumerate(products_data, 1):
        product = Product(
            product_id=i,
            name=product_data['name'],
            description=product_data['description'],
            price=product_data['price'],
            category=product_data['category'],
            image_url=product_data['image_url'],
            stock=product_data['stock']
        )
        data_store['products'][i] = product
    
    data_store['counters']['product_id'] = len(products_data) + 1

def get_next_id(counter_name):
    """Get next available ID for a given counter"""
    current_id = data_store['counters'][counter_name]
    data_store['counters'][counter_name] += 1
    return current_id

def add_visitor_log(ip_address, user_agent, page=None):
    """Add a visitor log entry"""
    visitor_log = VisitorLog(ip_address, user_agent, page)
    data_store['visitor_logs'].append(visitor_log)

def get_daily_visitors():
    """Get visitor count for today"""
    today = datetime.now().date()
    daily_visitors = [log for log in data_store['visitor_logs'] 
                     if log.timestamp.date() == today]
    return len(set(log.ip_address for log in daily_visitors))

def get_weekly_visitors():
    """Get visitor data for the past week"""
    week_ago = datetime.now() - timedelta(days=7)
    weekly_data = {}
    
    for i in range(7):
        date = (week_ago + timedelta(days=i)).date()
        daily_logs = [log for log in data_store['visitor_logs'] 
                     if log.timestamp.date() == date]
        weekly_data[date.strftime('%Y-%m-%d')] = len(set(log.ip_address for log in daily_logs))
    
    return weekly_data
