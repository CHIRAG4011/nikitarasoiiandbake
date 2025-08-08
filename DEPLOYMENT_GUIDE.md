# NIKITA RASOI & BAKES - Deployment Guide

## Overview
This guide covers deploying the NIKITA RASOI & BAKES Flask e-commerce application both locally and on free hosting platforms.

## Local Development Setup

### Prerequisites
- Python 3.11 or higher
- Git (for cloning the repository)

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd nikita-rasoi-bakes

# Create virtual environment
python -m venv bakery_env

# Activate virtual environment
# On Windows:
bakery_env\Scripts\activate
# On macOS/Linux:
source bakery_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration
Create a `.env` file in the root directory:
```env
# Required Settings
SESSION_SECRET=your-super-secret-key-here-change-this

# Email Configuration (Optional - for order confirmations)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Development Settings
FLASK_ENV=development
DEBUG=True
```

### Step 3: Run Locally
```bash
# Start the application
python main.py

# Or use Gunicorn (production-like)
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

The application will be available at `http://localhost:5000`

### Default Admin Credentials
- **Username:** admin
- **Email:** admin@nikitarasoi.com
- **Password:** admin123

## Free Hosting Options

### Option 1: Replit (Recommended)
Replit provides excellent Python hosting with built-in environment management.

#### Setup on Replit:
1. Import your repository to Replit
2. Replit automatically detects Python projects
3. Set environment variables in the Secrets panel:
   - `SESSION_SECRET`: Generate a strong secret key
   - Email settings (if needed)
4. Run with the built-in deployment

#### Advantages:
- Zero configuration
- Automatic HTTPS
- Built-in database support
- Free tier available
- Great for development and small projects

### Option 2: Railway
Railway offers simple deployment with generous free tier.

#### Setup on Railway:
1. Connect your GitHub repository
2. Set environment variables:
   ```
   SESSION_SECRET=your-secret-key
   PORT=5000
   ```
3. Railway automatically builds and deploys

#### Deploy Command:
```bash
# Railway will use this automatically
gunicorn --bind 0.0.0.0:$PORT main:app
```

### Option 3: Render
Render provides free static and web service hosting.

#### Setup on Render:
1. Connect your GitHub repository
2. Choose "Web Service"
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT main:app`
4. Set environment variables in dashboard

### Option 4: Heroku (Limited Free Tier)
Note: Heroku discontinued their free tier but offers low-cost options.

#### Setup files needed:
Create `requirements.txt`:
```
Flask==3.0.0
Flask-Mail==0.9.1
Werkzeug==3.0.1
gunicorn==21.2.0
email-validator==2.1.0
```

Create `Procfile`:
```
web: gunicorn --bind 0.0.0.0:$PORT main:app
```

Create `runtime.txt`:
```
python-3.11.7
```

## Production Considerations

### Security Settings
For production deployments, ensure:

1. **Strong Session Secret:**
   ```python
   import secrets
   SESSION_SECRET = secrets.token_urlsafe(32)
   ```

2. **Environment Variables:**
   ```env
   FLASK_ENV=production
   DEBUG=False
   ```

3. **HTTPS Only:** Most free hosting platforms provide HTTPS automatically

### Database Considerations
The current application uses in-memory storage which is suitable for:
- Development
- Small-scale applications
- Demos and prototypes

For production with persistent data, consider:
- SQLite (file-based, simple)
- PostgreSQL (recommended for production)
- MySQL/MariaDB

### Email Configuration
For production email sending:
- Use environment-specific SMTP settings
- Consider email services like SendGrid, Mailgun
- Gmail requires "App Passwords" for SMTP

### Performance Optimization
1. **Static File Serving:**
   - Use CDN for static assets in production
   - Enable compression

2. **Caching:**
   - Implement Redis/Memcached for session storage
   - Cache frequently accessed data

3. **Database Connection Pooling:**
   - When using external databases
   - Configure appropriate pool sizes

## Monitoring and Maintenance

### Application Monitoring
- Monitor application logs
- Set up error tracking (Sentry, Rollbar)
- Monitor resource usage

### Backup Strategy
- Regular data backups (when using persistent storage)
- Code repository backups
- Configuration backups

### Updates and Maintenance
- Regular dependency updates
- Security patches
- Monitor for vulnerabilities

## Troubleshooting

### Common Issues

1. **Port Binding Issues:**
   ```python
   # Ensure proper port binding
   port = int(os.environ.get('PORT', 5000))
   app.run(host='0.0.0.0', port=port)
   ```

2. **Static Files Not Loading:**
   - Check static file paths
   - Verify STATIC_URL configuration

3. **Email Not Sending:**
   - Verify SMTP credentials
   - Check firewall/port restrictions
   - Enable "Less Secure Apps" or use App Passwords

4. **Session Issues:**
   - Verify SESSION_SECRET is set
   - Check session cookie configuration

### Environment-Specific Issues

#### Replit:
- Use 0.0.0.0 as host for external access
- Environment variables in Secrets panel
- Automatic port detection

#### Railway/Render:
- Ensure PORT environment variable is used
- Check build logs for errors
- Verify start command syntax

### Performance Issues
- Monitor memory usage (important for free tiers)
- Optimize database queries
- Use appropriate caching strategies

## Support and Resources

### Documentation
- Flask Documentation: https://flask.palletsprojects.com/
- Deployment guides for each platform
- Python deployment best practices

### Community Support
- Platform-specific communities
- Flask community forums
- Stack Overflow for specific issues

---

**Note:** This application is designed for educational and small business use. For large-scale production deployments, consider additional security measures, performance optimization, and infrastructure scaling.