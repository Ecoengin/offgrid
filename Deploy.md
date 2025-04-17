# Deploying Your Solar Training Platform to cPanel

Based on your project structure, here's a comprehensive guide to deploy your Django application on cPanel:

## 1. Prepare Your Project

1. Modify [web_django/settings.py](c:\Users\efokp\OneDrive\Hp-15-file\kentronic-energy-ltd\Ecoengin\SolarTraining\django-template\web_django\settings.py) for production:

```python
# Change Debug to False
DEBUG = False

# Add your domain to allowed hosts
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Generate a new secret key for production
SECRET_KEY = 'your-new-secure-secret-key'  # Better to use environment variable

# Configure static and media settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

2. Create a `passenger_wsgi.py` file in your project root:

```python
import os
import sys

# Add the project directory to system path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variable for Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_django.settings")

# Import and create the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 2. Set Up Python Application in cPanel

1. Log in to your cPanel account
2. Look for "Setup Python App" or "Python" section
3. Click "Create Application"
4. Configure your application:
   - Python Version: 3.11 or 3.12
   - Application Root: `/home/username/solar_training` (your domain's document root)
   - Application URL: Your domain or subdomain
   - Application Entry Point: `passenger_wsgi.py`
   - Application Startup File: `passenger_wsgi.py`

## 3. Upload Your Files

1. Use File Manager in cPanel or FTP to upload your files to the application root
2. Maintain the same directory structure as your local project

## 4. Set Up Virtual Environment and Install Dependencies

Connect via SSH to your server and run:

```bash
cd ~/solar_training
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install additional production packages
pip install mysqlclient gunicorn
```

## 5. Configure Database

1. In cPanel, go to "MySQL Databases"
2. Create a new database (e.g., `username_solardb`)
3. Create a database user and password
4. Add the user to the database with all privileges

5. Update your database settings in [web_django/settings.py](c:\Users\efokp\OneDrive\Hp-15-file\kentronic-energy-ltd\Ecoengin\SolarTraining\django-template\web_django\settings.py):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'username_solardb',
        'USER': 'username_dbuser',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
```

## 6. Run Migrations and Create Superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

## 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## 8. Set Up File Permissions

```bash
# Set appropriate permissions for media and static files
mkdir -p media/badge_images
mkdir -p media/profile_images
mkdir -p media/course_images
chmod -R 755 media staticfiles
```

## 9. Configure .htaccess File

Create an `.htaccess` file in your application root:

```apache
# Serve static and media files directly
RewriteEngine On
RewriteRule ^static/(.*)$ /staticfiles/$1 [L]
RewriteRule ^media/(.*)$ /media/$1 [L]

# Pass all non-static requests to Python application
RewriteCond %{REQUEST_URI} !^/static/
RewriteCond %{REQUEST_URI} !^/media/
RewriteRule ^(.*)$ passenger_wsgi.py/$1 [QSA,L]
```

## 10. Restart Application

1. In cPanel, go back to "Setup Python App"
2. Find your application and click "Restart"

## 11. Additional Configuration

### Session Management

For better session management, consider adding:

```python
# In settings.py
SESSION_COOKIE_SECURE = True  # For HTTPS
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds
```

### Email Configuration

To enable email functionality (for password resets, etc.):

```python
# In settings.py
EMAIL_HOST = 'mail.yourdomain.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@yourdomain.com'
EMAIL_HOST_PASSWORD = 'your_email_password'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Solar Training <noreply@yourdomain.com>'
```

### Security

Add additional security headers:

```python
# In settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
CSRF_COOKIE_SECURE = True  # For HTTPS
```

## Troubleshooting

If you encounter issues:

1. Check cPanel error logs
2. Verify permissions on your Python files
3. Look for issues in your MySQL connection
4. Ensure your domain is correctly configured in ALLOWED_HOSTS
5. Check that your virtual environment is properly set up

Remember that your application has multiple connected components (courses, badges, user tracking) so testing thoroughly after deployment is crucial.
