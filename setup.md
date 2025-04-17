# Hosting Your Django Solar Training Platform on cPanel

To deploy your Django application on cPanel, follow these steps:

## 1. Prerequisites

- A cPanel hosting account with Python support
- SSH access (recommended)
- Access to the cPanel file manager

## 2. Set Up Python Environment

1. Log in to cPanel
2. Find the "Setup Python App" section (or similar, depends on host)
3. Create a new Python application:
   - Choose Python 3.11+ as the version
   - Set application root to your Django project folder
   - Set application URL to your domain or subdomain
   - Set application startup file to `passenger_wsgi.py` (we'll create this)

## 3. Upload Your Project

### Option 1: Using File Manager

1. In cPanel, open File Manager
2. Navigate to your Python app directory
3. Upload all project files from your local django-template folder

### Option 2: Using Git

1. Connect to your server via SSH
2. Navigate to your Python app directory
3. Clone your repository or upload files with SFTP

## 4. Set Up Virtual Environment

1. Connect via SSH to your server
2. Navigate to your project directory
3. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

## 5. Configure Settings

1. Edit settings.py:

   ```python
   # Change debug to False
   DEBUG = False
   
   # Add your domain to allowed hosts
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   
   # Configure database (if needed)
   # For MySQL (common on cPanel):
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'your_db_name',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   
   # Update static and media settings
   STATIC_URL = '/static/'
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   MEDIA_URL = '/media/'
   MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
   ```

## 6. Create WSGI Configuration

Create a `passenger_wsgi.py` file in your project root:

```python
import os
import sys

# Add your project directory to the sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variable for Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_django.settings")

# Create application object
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 7. Set Up Database

1. In cPanel, go to MySQL Databases or PostgreSQL Databases
2. Create a new database
3. Create a database user and add them to the database
4. Update your settings.py with the database credentials
5. Run migrations through SSH:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

## 8. Collect Static Files

```bash
python manage.py collectstatic
```

## 9. Configure Media Folder Permissions

```bash
mkdir -p media/badge_images
chmod -R 755 media
```

## 10. Final Configuration

1. If your cPanel has Passenger or uWSGI:
   - Restart your Python application from cPanel

2. If using Apache (common):
   - Make sure your `.htaccess` file is properly set up (usually automatic)

3. Test your deployment by visiting your domain

## Troubleshooting

- Check the error logs in cPanel
- Make sure your SECRET_KEY is properly set (use environment variables)
- Ensure database connection is working
- Verify static files are properly served
- Check Python version compatibility

This specific application has multiple connected apps and uses features like image uploads and user authentication, so make sure all permissions and configurations are properly set up.
