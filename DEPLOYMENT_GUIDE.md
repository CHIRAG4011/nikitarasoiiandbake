# NIKITA RASOI & BAKES - Deployment Guide

This guide provides step-by-step instructions for deploying the NIKITA RASOI & BAKES e-commerce website on different platforms.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Free Hosting Deployment](#free-hosting-deployment)
3. [Environment Variables](#environment-variables)
4. [Database Setup](#database-setup)
5. [Email Configuration](#email-configuration)

---

## Local Development Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL (optional, uses SQLite by default in development)
- Git

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd nikita-rasoi-bakes

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration

Create a `.env` file in the project root:

```env
# Basic Configuration
SESSION_SECRET=your-secret-key-here-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration (optional for development)
DATABASE_URL=postgresql://username:password@localhost:5432/nikita_rasoi_db

# Email Configuration (for order confirmations)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Step 3: Database Setup

```bash
# If using PostgreSQL, create database first
createdb nikita_rasoi_db

# Run the application (tables will be created automatically)
python main.py
```

### Step 4: Access the Application

- Open your browser and go to `http://localhost:5000`
- Default admin credentials: `admin` / `admin123`
- Change the admin password immediately after first login

---

## Free Hosting Deployment

### Option 1: InfinityFree Hosting

InfinityFree offers free PHP hosting, but doesn't support Python applications directly. For Python apps, consider these alternatives:

#### Alternative Free Platforms for Python:

1. **Render** (Recommended)
2. **Railway**
3. **PythonAnywhere**
4. **Heroku** (limited free tier)

### Deploying on Render (Free Tier)

#### Step 1: Prepare Your Code

1. Create `requirements.txt`:
```txt
Flask==3.0.0
Flask-Mail==0.9.1
Flask-SQLAlchemy==3.1.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
Werkzeug==3.0.1
```

2. Create `render.yaml`:
```yaml
services:
  - type: web
    name: nikita-rasoi-bakes
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT main:app
    envVars:
      - key: SESSION_SECRET
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: nikita-rasoi-db
          property: connectionString
      - key: MAIL_SERVER
        value: smtp.gmail.com
      - key: MAIL_PORT
        value: 587
      - key: MAIL_USERNAME
        value: your-email@gmail.com
      - key: MAIL_PASSWORD
        value: your-app-password
      - key: MAIL_DEFAULT_SENDER
        value: admin@nikitarasoi.com

databases:
  - name: nikita-rasoi-db
    plan: free
```

#### Step 2: Deploy to Render

1. Push your code to GitHub
2. Connect GitHub to Render
3. Create a new Web Service
4. Connect your repository
5. Configure environment variables
6. Deploy!

### Deploying on Railway

#### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

#### Step 2: Deploy

```bash
# Login to Railway
railway login

# Initialize project
railway init

# Add PostgreSQL database
railway add postgresql

# Deploy
railway up
```

#### Step 3: Configure Environment Variables

In Railway dashboard, add:
- `SESSION_SECRET`: Generate a secure random string
- `MAIL_*` variables for email functionality

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SESSION_SECRET` | Secret key for Flask sessions | `your-very-long-random-string` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |

### Optional Variables (Email)

| Variable | Description | Default |
|----------|-------------|---------|
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USERNAME` | Email username | `""` |
| `MAIL_PASSWORD` | Email password/app password | `""` |
| `MAIL_DEFAULT_SENDER` | Default sender email | `admin@nikitarasoi.com` |

---

## Database Setup

### PostgreSQL Setup

#### Local PostgreSQL Installation

**Windows:**
1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Install with default settings
3. Remember the password for 'postgres' user

**macOS:**
```bash
# Using Homebrew
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE nikita_rasoi_db;
CREATE USER nikita_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nikita_rasoi_db TO nikita_user;
\q
```

### Database Migration

The application automatically creates tables on startup. Default admin user is created with:
- Username: `admin`
- Password: `admin123`
- Email: `admin@nikitarasoi.com`

**Important**: Change the admin password immediately after deployment!

---

## Email Configuration

### Gmail Setup (Recommended)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Google Account Settings → Security → App passwords
   - Select "Mail" and generate password
3. Use the generated password (not your regular password) in `MAIL_PASSWORD`

### Environment Variables for Email

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=admin@nikitarasoi.com
```

---

## Production Checklist

### Security

- [ ] Change default admin password
- [ ] Set strong `SESSION_SECRET`
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS
- [ ] Configure proper CORS if needed

### Performance

- [ ] Use PostgreSQL in production
- [ ] Configure proper logging
- [ ] Set up monitoring
- [ ] Enable gzip compression
- [ ] Configure static file serving

### Backup

- [ ] Set up database backups
- [ ] Document backup/restore procedures
- [ ] Test backup restoration

---

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check `DATABASE_URL` format
   - Ensure PostgreSQL is running
   - Verify credentials

2. **Email Not Sending**
   - Check Gmail App Password
   - Verify SMTP settings
   - Check firewall/port restrictions

3. **Static Files Not Loading**
   - Check file paths in templates
   - Ensure static folder exists
   - Configure web server for static files

4. **Admin Access Issues**
   - Default admin: `admin` / `admin123`
   - Reset via database if needed:
   ```sql
   UPDATE users SET is_admin = true WHERE username = 'your_username';
   ```

### Support

For additional support:
1. Check application logs
2. Review error messages
3. Verify environment variables
4. Test database connectivity

---

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app/)

---

**Last Updated**: August 2025
**Version**: 1.0.0