[Português (pt-BR)](README.pt-BR.md)

#  REST API - Service Appointment Management System

A complete application developed with Django REST Framework for managing clients, service appointments, and tracking daily metrics. This system is designed to facilitate business control for companies working with appointments, such as clinics, beauty salons, offices, and service providers in general.

##  What is this application?

This is a **RESTful API** (Application Programming Interface) that allows you to manage:

- **Clients**: Complete registration with contact information, documents, and notes
- **Appointments**: Control of scheduled services with times, locations, and status
- **Dashboard**: Daily reports with attendance and revenue metrics

###  What is it for?

The system was developed to solve common problems of businesses working with appointments:

1- Organize client information in a centralized way  
2- Schedule services avoiding time conflicts at the same location  
3- Control appointment status (Scheduled, Confirmed, Canceled, Completed)  
4- Manage multiple units/service locations  
5- Register payment methods and amounts  
6- View daily metrics of appointments and revenue  

##  Application Architecture

The application uses modern and professional technologies:

- **Django 5.2.8**: Robust and secure web framework
- **Django REST Framework**: For building the RESTful API
- **PostgreSQL 17**: Professional and reliable database
- **Docker**: Containerization to facilitate installation and deployment
- **Python 3.11.14**: Modern programming language

###  Data Structure

**Customer Model (`Customer`)**
- Full name, phone, email, and document
- Notes field for important observations
- Active/inactive status
- Creation date

**Appointment Model (`Appointment`)**
- Linked to a customer
- Service name provided
- Location (Unit 1, 2, 3, or 4)
- Start and end date/time
- Status (Scheduled, Confirmed, Canceled, Completed)
- Service price
- Payment method (Cash, PIX, Card, Transfer)

###  API Endpoints

The API offers the following endpoints:

**Clients:**
- `GET /api/customers/` - List all clients (with search by name, phone, or email using `?q=term`)
- `POST /api/customers/` - Create new client
- `GET /api/customers/{id}/` - Get details of a specific client
- `PUT/PATCH /api/customers/{id}/` - Update client data
- `DELETE /api/customers/{id}/` - Deactivate a client (soft delete)

**Appointments:**
- `GET /api/appointment/` - List all appointments (with filters by date, client, and status)
- `POST /api/appointment/` - Create new appointment
- `GET /api/appointment/{id}/` - Get appointment details
- `PUT/PATCH /api/appointment/{id}/` - Update an appointment
- `DELETE /api/appointment/{id}/` - Cancel an appointment

**Dashboard:**
- `GET /api/dashboard/daily-summary/?date=YYYY-MM-DD` - Get daily summary with metrics

##  Project Structure

```
.
├── djangoapp/                 # Main Django application
│   ├── api_rest/             # REST API app
│   │   ├── models.py         # Data models (Customer, Appointment)
│   │   ├── serializers.py    # Data serialization to JSON
│   │   ├── views.py          # API endpoints logic
│   │   ├── urls.py           # API routes
│   │   └── migrations/       # Database migrations
│   ├── project/              # Django settings
│   │   ├── settings.py       # Main settings
│   │   └── urls.py           # Project main routes
│   ├── manage.py             # Django command-line utility
│   └── requirements.txt      # Python dependencies
├── scripts/                   # Helper scripts
│   ├── commands.sh           # Initialization commands orchestrator
│   ├── wait_psql.sh          # Wait for PostgreSQL to be ready
│   ├── collectstatic.sh      # Collect static files
│   ├── makemigrations.sh     # Generate database migrations
│   ├── migrate.sh            # Apply database migrations
│   └── runserver.sh          # Start development server
├── dotenv_files/             # Environment configuration files
│   └── .env                  # Environment variables (create this file)
├── data/                     # Persistent data (automatically created)
│   └── postgres/data/        # PostgreSQL data
├── docker-compose.yml        # Docker services configuration
├── Dockerfile                # Django container definition
└── readme.md                 # This file
```

##  How to Initialize the Application

### Prerequisites

Before you begin, you need to have the following installed on your computer:

- **Docker**: Containerization platform - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: Tool to orchestrate multiple containers - [Install Docker Compose](https://docs.docker.com/compose/install/)

> **💡 What is Docker?** Docker is a tool that allows you to run applications in "containers" - isolated environments that contain everything the application needs to run. This eliminates problems like "it works on my machine but not on yours".

### Step 1: Configure Environment Variables

First, you need to create a configuration file that contains sensitive information such as database passwords.

1. **Create the folder** `dotenv_files` if it doesn't exist
2. **Create a file** named `.env` inside the `dotenv_files` folder
3. **Add the following content** to the `.env` file:

```bash
# PostgreSQL Database Configuration
POSTGRES_DB=appointments_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_secure_password_here

# Django Configuration
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

> ** Important:** Change `your_secure_password_here` and `your-django-secret-key-here` to secure values before using in production.

### Step 2: Build and Start the Containers

Open a terminal in the project root folder (where the `docker-compose.yml` file is located) and run:

```bash
docker-compose up --build
```

**What this command does:**

1.  Builds the Django Docker image
2.  Downloads the PostgreSQL 17 image
3.  Starts the `djangoapp` and `psql` containers
4.  Waits for PostgreSQL to be ready
5.  Collects Django static files
6.  Creates database tables (migrations)
7.  Starts the development server on port 8001

**Wait for the message:**
```
Starting development server at http://0.0.0.0:8000/
```

When this message appears, your application is running! 

**Access the application at:** http://localhost:8001

### Step 3: Create a Superuser (Administrator)

To access the Django admin panel and manage data through the graphical interface, you need to create an administrator user.

**In a new terminal**, run:

```bash
docker-compose exec djangoapp python manage.py createsuperuser
```

The system will request the following information:

```
Username (leave blank to use 'duser'): admin
Email address: your-email@example.com
Password: ********
Password (again): ********
```

> ** Tip:** The password must be at least 8 characters long and cannot be too common.

After creating the superuser, access the admin panel at: **http://localhost:8001/admin**

### Step 4: Testing the API

You can test the API endpoints using tools like:

- **Web Browser**: For simple GET requests
- **Postman**: Graphical tool for testing APIs - [Download Postman](https://www.postman.com/downloads/)
- **cURL**: Command-line tool (already installed on Linux/Mac)

**Browser test example:**
- Access http://localhost:8001/api/customers/ to see the list of clients

**cURL test example:**
```bash
# List clients
curl http://localhost:8001/api/customers/

# Create a new client
curl -X POST http://localhost:8001/api/customers/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "phone": "(11) 98765-4321",
    "email": "john.doe@email.com",
    "id_document": "123.456.789-00"
  }'
```

##  Useful Commands

### Container Management

```bash
# Start the application (first time or after changes)
docker-compose up --build

# Start the application in "background" mode
docker-compose up -d

# Stop the application
docker-compose down

# Stop and REMOVE all data ( warning: deletes the database)
docker-compose down -v

# View application logs in real-time
docker-compose logs -f djangoapp

# View database logs
docker-compose logs -f psql
```

### Django Commands

All Django commands must be executed **inside the container** using the prefix `docker-compose exec djangoapp`:

```bash
# Create a superuser (administrator)
docker-compose exec djangoapp python manage.py createsuperuser

# Access Django shell (interactive Python console)
docker-compose exec djangoapp python manage.py shell

# Create migrations after modifying models.py
docker-compose exec djangoapp python manage.py makemigrations

# Apply migrations to the database
docker-compose exec djangoapp python manage.py migrate

# Collect static files
docker-compose exec djangoapp python manage.py collectstatic

# Run tests
docker-compose exec djangoapp python manage.py test

# Access container terminal
docker-compose exec djangoapp sh
```

##  Main Features

### 1. Client Management

The system stores complete client information:
- Contact data (name, phone, email)
- Identification documents
- Notes field for observations
- Active/inactive status (soft delete)
- Unique email validation

**Smart search**: Use the `?q=` parameter to search for clients by name, phone, or email.

### 2. Appointment System

Complete appointment control with:
- **Conflict prevention**: The system prevents simultaneous appointments at the same location
- **Multiple statuses**: Track the lifecycle (Scheduled → Confirmed → Completed/Canceled)
- **Multiple units**: Support for up to 4 different locations
- **Financial control**: Recording of amounts and payment methods
- **Automatic validations**: 
  - End time must be after start time
  - Client must be active to schedule

### 3. Metrics Dashboard

The dashboard endpoint provides a complete daily summary:
- Total appointments
- Quantity by status (Scheduled, Confirmed, Canceled, Completed)
- Total revenue from completed services

**Usage example:**
```
GET /api/dashboard/daily-summary/?date=2026-01-08
```

##  Security

### Implemented Best Practices

✅ Non-root user in Docker container (`duser`)  
✅ Data validation in serializers  
✅ Soft delete for clients (preserved data)  
✅ Appointment conflict validation  
✅ Required fields and model validations  

###  Before Using in Production

- [ ] Change Django `SECRET_KEY`
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS` correctly
- [ ] Use strong database passwords
- [ ] Implement HTTPS
- [ ] Add JWT or Token authentication
- [ ] Configure automatic database backup
- [ ] Implement rate limiting
- [ ] Review permissions and authorizations

##  Production Deployment with Nginx on VPS

This section provides a complete and didactic guide for deploying the application on a VPS (Virtual Private Server) using Nginx as a reverse proxy.

###  What You'll Need

- **VPS**: A virtual server (e.g., DigitalOcean, AWS EC2, Linode, Contabo)
- **Operating System**: Ubuntu 20.04+ or Debian 11+ (Ubuntu recommended)
- **Domain**: A domain name pointing to your VPS IP (optional, but recommended)
- **SSH Access**: To connect to the server

###  Deployment Process Flowchart

```
┌─────────────────────────────────────────────────────────┐
│  1. PREPARE THE VPS SERVER                              │
│  ├─ Connect via SSH                                     │
│  ├─ Update operating system                            │
│  └─ Install dependencies (Docker, Docker Compose, Git) │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  2. CLONE AND CONFIGURE APPLICATION                     │
│  ├─ Clone project repository                           │
│  ├─ Configure environment variables (.env)             │
│  └─ Adjust security settings                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  3. CONFIGURE DOCKER FOR PRODUCTION                     │
│  ├─ Modify docker-compose.yml                          │
│  ├─ Build and start containers                         │
│  └─ Create Django superuser                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  4. INSTALL AND CONFIGURE NGINX                         │
│  ├─ Install Nginx                                       │
│  ├─ Create site configuration file                     │
│  ├─ Configure reverse proxy for Django                 │
│  └─ Activate configuration                             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  5. CONFIGURE SSL/HTTPS (CERTBOT)                       │
│  ├─ Install Certbot                                     │
│  ├─ Obtain free SSL certificate                        │
│  └─ Configure automatic renewal                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  6. TEST AND MONITOR                                    │
│  ├─ Test access via HTTPS                              │
│  ├─ Check logs                                         │
│  └─ Configure monitoring                               │
└─────────────────────────────────────────────────────────┘
```

###  Detailed Step-by-Step Guide

#### **Step 1: Prepare the VPS Server**

**1.1 - Connect to the server via SSH**

On your local computer, open the terminal and connect to the server:

```bash
ssh user@YOUR_SERVER_IP

# Example:
# ssh root@192.168.1.100
```

**1.2 - Update the operating system**

```bash
# Update package list
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y
```

**1.3 - Install Docker**

```bash
# Install dependencies
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list again
sudo apt update

# Install Docker
sudo apt install docker-ce docker-ce-cli containerd.io -y

# Check if it's running
sudo systemctl status docker
```

**1.4 - Install Docker Compose**

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Give execution permission
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

**1.5 - Install Git**

```bash
sudo apt install git -y
```

#### **Step 2: Clone and Configure the Application**

**2.1 - Create directory for applications**

```bash
# Create folder for projects
sudo mkdir -p /var/www
cd /var/www
```

**2.2 - Clone the repository**

```bash
# Clone your project (replace with your repository URL)
sudo git clone https://github.com/your-username/django-api-rest.git
cd django-api-rest
```

**2.3 - Configure environment variables**

```bash
# Create dotenv_files folder if it doesn't exist
sudo mkdir -p dotenv_files

# Create .env file
sudo nano dotenv_files/.env
```

Add the following **production** configurations:

```bash
# PostgreSQL Database Configuration
POSTGRES_DB=appointments_prod
POSTGRES_USER=admin_prod
POSTGRES_PASSWORD=YourSuperSecurePassword123!@#

# Django Configuration (PRODUCTION)
SECRET_KEY=your-super-long-and-complex-secret-key-here-12345678
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_VPS_IP
```

> ** IMPORTANT:** 
> - Change `YourSuperSecurePassword123!@#` to a strong password
> - Generate a new unique `SECRET_KEY` (use: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
> - Set `DEBUG=False` in production
> - Replace `yourdomain.com` with your actual domain

To save in nano: `Ctrl+O`, `Enter`, `Ctrl+X`

#### **Step 3: Configure Docker for Production**

**3.1 - Adjust docker-compose.yml**

Edit the file to change the port:

```bash
sudo nano docker-compose.yml
```

Modify the port line to:

```yaml
ports:
  - "127.0.0.1:8000:8000"  # Local only, Nginx will proxy
```

**3.2 - Start the application**

```bash
# Build and start containers in background
sudo docker-compose up --build -d

# Check if containers are running
sudo docker-compose ps

# View logs
sudo docker-compose logs -f
```

**3.3 - Create superuser**

```bash
sudo docker-compose exec djangoapp python manage.py createsuperuser
```

#### **Step 4: Install and Configure Nginx**

**4.1 - Install Nginx**

```bash
sudo apt install nginx -y

# Check status
sudo systemctl status nginx
```

**4.2 - Create site configuration**

```bash
# Create configuration file
sudo nano /etc/nginx/sites-available/django-api
```

Add the following configuration:

```nginx
# Nginx configuration for Django REST API
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;  # Replace with your domain

    # Logs
    access_log /var/log/nginx/django_access.log;
    error_log /var/log/nginx/django_error.log;

    # Maximum upload size
    client_max_body_size 100M;

    # Proxy to Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Static files (if needed)
    location /static/ {
        alias /var/www/django-api-rest/data/web/static/;
    }

    # Media files (if needed)
    location /media/ {
        alias /var/www/django-api-rest/data/web/media/;
    }
}
```

> ** Explanation:**
> - `listen 80`: Nginx listens on port 80 (HTTP)
> - `server_name`: Your domain (or server IP)
> - `proxy_pass`: Redirects requests to Django on port 8000
> - `proxy_set_header`: Preserves original request information
> - `location /static/` and `/media/`: Serve static files directly through Nginx (more efficient)

To save: `Ctrl+O`, `Enter`, `Ctrl+X`

**4.3 - Activate configuration**

```bash
# Create symbolic link to activate the site
sudo ln -s /etc/nginx/sites-available/django-api /etc/nginx/sites-enabled/

# Remove default configuration (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

**4.4 - Configure Firewall (UFW)**

```bash
# Allow Nginx Full (HTTP and HTTPS)
sudo ufw allow 'Nginx Full'

# Allow SSH (important to not lose access!)
sudo ufw allow OpenSSH

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

**At this point, your application should be accessible via:** `http://yourdomain.com`

#### **Step 5: Configure SSL/HTTPS with Certbot**

HTTPS is **essential** for production security. We'll use Let's Encrypt (free).

**5.1 - Install Certbot**

```bash
# Install Certbot and Nginx plugin
sudo apt install certbot python3-certbot-nginx -y
```

**5.2 - Obtain SSL certificate**

```bash
# Obtain and configure certificate automatically
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# During the process, you'll be asked:
# - Email: Your email for notifications
# - Terms: Accept terms of service
# - Redirect: Choose option 2 (redirect HTTP to HTTPS)
```

> **Certbot will:**
> - Obtain SSL certificate for free
> - Automatically modify Nginx configuration
> - Configure HTTP to HTTPS redirection

**5.3 - Test automatic renewal**

```bash
# Test renewal (without actually renewing)
sudo certbot renew --dry-run

# If it passes, automatic renewal is configured!
```

Certbot automatically configures a cronjob to renew certificates before they expire (every 90 days).

**5.4 - Check final Nginx configuration**

```bash
sudo nano /etc/nginx/sites-available/django-api
```

After Certbot, your file should have something like:

```nginx
server {
    server_name yourdomain.com www.yourdomain.com;

    # ... your previous configurations ...

    listen 443 ssl;  # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;  # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;  # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf;  # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;  # managed by Certbot
}

# Redirect HTTP to HTTPS
server {
    if ($host = www.yourdomain.com) {
        return 301 https://$host$request_uri;
    }

    if ($host = yourdomain.com) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 404;
}
```

#### **Step 6: Test and Monitor**

**6.1 - Test the application**

Access in browser:
- `https://yourdomain.com/api/customers/` 
- `https://yourdomain.com/admin/` 

**6.2 - Check logs**

```bash
# Nginx logs
sudo tail -f /var/log/nginx/django_access.log
sudo tail -f /var/log/nginx/django_error.log

# Django logs
cd /var/www/django-api-rest
sudo docker-compose logs -f djangoapp
```

**6.3 - Useful management commands**

```bash
# Restart Nginx
sudo systemctl restart nginx

# Restart Django application
sudo docker-compose restart

# Check container status
sudo docker-compose ps

# Backup database
sudo docker-compose exec psql pg_dump -U admin_prod appointments_prod > backup_$(date +%Y%m%d).sql

# Update application (after git pull)
cd /var/www/django-api-rest
sudo git pull
sudo docker-compose up --build -d
sudo docker-compose exec djangoapp python manage.py migrate
sudo docker-compose exec djangoapp python manage.py collectstatic --noinput
sudo systemctl reload nginx
```

###  Final Deployment Checklist

- [ ] VPS server provisioned and updated
- [ ] Docker and Docker Compose installed
- [ ] Application cloned and configured
- [ ] Environment variables configured (DEBUG=False)
- [ ] SECRET_KEY changed to unique value
- [ ] Docker containers running correctly
- [ ] Nginx installed and configured
- [ ] Firewall (UFW) configured
- [ ] SSL certificate installed via Certbot
- [ ] HTTPS working correctly
- [ ] HTTP → HTTPS redirect active
- [ ] Django Admin accessible
- [ ] API endpoints working
- [ ] Logs being generated correctly
- [ ] Database backup configured

###  Additional Security Tips

1. **Change default SSH port**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change: Port 22 to Port 2222
   sudo systemctl restart sshd
   ```

2. **Configure fail2ban** (protects against brute force attacks)
   ```bash
   sudo apt install fail2ban -y
   sudo systemctl enable fail2ban
   ```

3. **Disable root login via SSH**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # PermitRootLogin no
   ```

4. **Configure automatic backups**
   ```bash
   # Create backup script
   sudo nano /usr/local/bin/backup-django.sh
   ```

###  Monitoring and Maintenance

**Configure rotating logs:**
```bash
sudo nano /etc/logrotate.d/django-api
```

```
/var/log/nginx/django_*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
}
```

**Check resource usage:**
```bash
# CPU and memory
htop

# Disk space
df -h

# Container status
sudo docker stats
```

###  Common Problem Resolution

**Problem: Nginx returns 502 Bad Gateway**
```bash
# Check if Django is running
sudo docker-compose ps
sudo docker-compose logs djangoapp

# Check connectivity
curl http://127.0.0.1:8000
```

**Problem: SSL certificate doesn't renew automatically**
```bash
# Force renewal
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

**Problem: Slow application**
```bash
# Check resources
sudo docker stats

# Increase Django workers (if needed)
# Add Gunicorn to project for better performance
```

##  Docker Configuration Details

### Services

**djangoapp**
- **Base image**: Python 3.11.14 Alpine
- **Exposed port**: 8001 → 8000 (container)
- **Volumes**: Application code, static and media files
- **User**: duser (non-root)

**psql**
- **Image**: postgres:17-alpine
- **Persistent volume**: `./data/postgres/data`
- **Port**: 5432 (internal only)

### Docker Volumes

- `static_volume`: Django static files (CSS, JS, images)
- `media_volume`: User-uploaded files
- `./data/postgres/data`: PostgreSQL database data

##  Technologies and Concepts

### What is a REST API?

REST (Representational State Transfer) is an architectural style for APIs that uses:
- **HTTP as protocol**: Methods GET, POST, PUT, PATCH, DELETE
- **URLs as resources**: Each URL represents a resource (clients, appointments)
- **JSON as format**: Data travels in JSON format (JavaScript Object Notation)
- **Stateless**: Each request is independent

### Why Django REST Framework?

- Mature and stable framework
- Automatic API documentation
- Automatic data serialization
- Robust validation
- Support for authentication and permissions
- Widely used in the industry

### Why PostgreSQL?

- Robust and reliable relational database
- ACID transaction support
- High-scale performance
- Open source and widely used
- Excellent integration with Django

##  Troubleshooting

### Application doesn't start

1. Check if Docker is running: `docker --version`
2. Check if `.env` file exists in `dotenv_files/.env`
3. Check logs: `docker-compose logs`

### Database connection error

1. Wait a few seconds - PostgreSQL may take time to start
2. Check if PostgreSQL container is running: `docker-compose ps`
3. Restart containers: `docker-compose restart`

### Error "port is already in use"

Port 8001 is already being used by another program:
1. Stop the program using the port
2. Or change the port in `docker-compose.yml` (line `ports: - 127.0.0.1:8001:8000`)

### How to reset the database

```bash
#  WARNING: This deletes all data!
docker-compose down -v
docker-compose up --build
```

##  Support

For questions or issues:

**Developer:** Ygor Lima  
**Email:** ygor.limarsx@gmail.com

---

**Educational Note:** This project was developed following best practices of modern web development, using industry standards and professional architecture. It's an excellent foundation for learning and building real appointment management systems.
