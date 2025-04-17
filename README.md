# Collecting workspace information# Installation and Deployment Guide for Solar Energy Training Platform

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (for version control)

## Local Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd SolarTraining
   ```

2. Create a virtual environment:
   - Using Command Palette in VS Code: **View > Command Palette > Python: Create Environment**
   - Or manually:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows:

   ```bash
   .venv\Scripts\activate
   ```

   - macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Initialize the database:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser (for admin access):

   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:

   ```bash
   python manage.py runserver
   ```

   Or using VS Code's Run and Debug view (F5)

## Production Deployment

### Option 1: Server Deployment (Apache/Nginx)

1. Install additional requirements:

   ```bash
   pip install gunicorn
   ```

2. Configure settings for production in settings.py:

   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   
   # Configure static files collection
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   ```

3. Collect static files:

   ```bash
   python manage.py collectstatic
   ```

4. Set up a production database (PostgreSQL recommended):

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'solartraining_db',
           'USER': 'db_user',
           'PASSWORD': 'db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. Configure web server (Nginx example):

   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;
       
       location /static/ {
           alias /path/to/solartraining/staticfiles/;
       }
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

6. Run with Gunicorn:

   ```bash
   gunicorn web_django.wsgi:application --bind 127.0.0.1:8000
   ```

### Option 2: Container Deployment

1. Create a Dockerfile in the project root:

   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   RUN python manage.py collectstatic --noinput
   
   EXPOSE 8000
   
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "web_django.wsgi:application"]
   ```

2. Build and run the Docker container:

   ```bash
   docker build -t solar-training-platform .
   docker run -p 8000:8000 solar-training-platform
   ```

### Option 3: Platform-as-a-Service (PaaS)

For deployment on platforms like Heroku, Railway, or PythonAnywhere, follow their specific Django deployment guides.

## Testing

Run tests to ensure everything is working properly:

```bash
python manage.py test
```

## Regular Maintenance

1. Update dependencies regularly:

   ```bash
   pip install -U -r requirements.txt
   ```

2. Backup your database periodically:

   ```bash
   python manage.py dumpdata > backup.json
   ```

3. Monitor server logs for errors and performance issues.
