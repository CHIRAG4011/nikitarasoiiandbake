# Sweet Crumbs Bakery

## Overview

Sweet Crumbs Bakery is a Flask-based e-commerce web application for an online bakery business. The application provides a complete shopping experience with product browsing, cart management, order placement, user authentication, and admin management capabilities. It features a warm, bakery-themed design with brown and cream color schemes, product catalogs with search and filtering, shopping cart functionality, order tracking, user profile management, and comprehensive admin tools for managing products, orders, and analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **CSS Framework**: Bootstrap 5 for responsive design and UI components
- **Custom Styling**: CSS custom properties for consistent bakery theme (brown/cream color palette)
- **JavaScript**: Vanilla JavaScript for cart management and interactive features
- **Icon Library**: Font Awesome for consistent iconography

### Backend Architecture
- **Web Framework**: Flask with modular route organization
- **Session Management**: Flask sessions for cart persistence and user authentication
- **Email System**: Flask-Mail for order confirmations and notifications
- **Data Models**: Object-oriented models for User, Product, Order, Review, and Address entities
- **Authentication**: Werkzeug password hashing with session-based user management
- **Middleware**: ProxyFix for handling reverse proxy headers

### Data Storage
- **Primary Storage**: In-memory data store using Python dictionaries
- **Data Structure**: Hierarchical dictionary structure for users, products, orders, reviews, addresses, and visitor logs
- **Auto-incrementing IDs**: Counter-based ID generation for all entities
- **Session Storage**: Flask sessions for cart data and user authentication state

### Application Structure
- **Modular Design**: Separated concerns with distinct files for routes, models, utilities, and data management
- **Template Hierarchy**: Base template with extending child templates for consistent layout
- **Static Assets**: Organized CSS and JavaScript files for frontend functionality
- **Admin Interface**: Dedicated admin templates and routes for business management

### Security Features
- **Password Security**: Werkzeug password hashing for secure credential storage
- **Session Security**: Configurable session secret key with environment variable support
- **Input Validation**: Form validation and sanitization throughout the application
- **Access Control**: Role-based access with admin user privileges

## External Dependencies

### Python Packages
- **Flask**: Core web framework for routing and request handling
- **Flask-Mail**: Email sending capabilities for order confirmations
- **Werkzeug**: Password hashing and WSGI utilities

### Frontend Libraries
- **Bootstrap 5**: CSS framework loaded via CDN for responsive design
- **Font Awesome 6**: Icon library loaded via CDN for UI elements
- **Chart.js**: JavaScript charting library for admin analytics dashboard

### Email Service
- **SMTP Configuration**: Configurable mail server settings (defaults to Gmail SMTP)
- **Environment Variables**: MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER

### Image Resources
- **Pixabay**: External image hosting for product photos and bakery imagery
- **Stock Photos**: Placeholder images for products and promotional content

### Development Tools
- **Environment Configuration**: Development vs production settings via environment variables
- **Debug Mode**: Flask debug mode for development with hot reloading
- **Logging**: Python logging module for application monitoring and debugging