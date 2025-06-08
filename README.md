# Coffee Lab Checklist Application

This is a Flask web application for managing store inspections and checklists for Coffee Lab stores.

## Deployment to Render

### Prerequisites

1. Create a [Render](https://render.com/) account if you don't have one
2. Create a [Cloudinary](https://cloudinary.com/) account if you don't have one (the app already has Cloudinary credentials configured)

### Step 1: Create a PostgreSQL Database on Render

1. Log in to your Render dashboard
2. Click on "New" and select "PostgreSQL"
3. Fill in the required details:
   - Name: `checklist-app-db` (or any name you prefer)
   - Database: `checklist_app`
   - User: (Render will generate this)
   - Region: Choose one close to your users
4. Click "Create Database"
5. After creation, note the "Internal Database URL" - you'll need this in the next step

### Step 2: Prepare Your Repository

Before deploying to Render, make sure your build.sh file is executable:

1. If you're using Git Bash or a Unix-like terminal:
   ```bash
   chmod +x build.sh
   git add build.sh
   git commit -m "Make build.sh executable"
   git push
   ```

2. If you're using Windows without Git Bash:
   - Make sure the build.sh file has Unix-style line endings (LF, not CRLF)
   - You can use a text editor like VS Code to change the line endings
   - In VS Code, look at the bottom right corner of the editor window and click on "CRLF" to change it to "LF"

### Step 3: Deploy the Web Service

1. From your Render dashboard, click on "New" and select "Web Service"
2. Connect your GitHub repository or use the "Deploy from GitHub" option
3. Fill in the required details:
   - Name: `checklist-app` (or any name you prefer)
   - Environment: Python
   - Build Command: `bash ./build.sh` (using bash explicitly helps avoid permission issues)
   - Start Command: `gunicorn run:app`
4. Add the following environment variables:
   - `DATABASE_URL`: (paste the Internal Database URL from Step 1)
   - `SECRET_KEY`: (generate a random string for security)
   - `RENDER`: `true`
5. Click "Create Web Service"

### Step 4: First Login

1. After deployment is complete, access your application at the URL provided by Render
2. Log in with the default admin credentials:
   - Username: `admin`
   - Password: `admin123`
3. **Important**: Immediately change the admin password after first login

## Local Development

### Prerequisites

1. Python 3.8 or higher
2. MySQL database

### Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a MySQL database named `checklist_app`
6. Update the database connection string in `run.py` if needed
7. Initialize the database: `python init_db.py`
8. Run the application: `python run.py`
9. Access the application at http://localhost:5000

## Application Structure

- `run.py`: Main application file
- `models_def.py`: Database models
- `extensions.py`: Flask extensions
- `routes.py`: Application routes (not used, routes are in run.py)
- `storage.py`: File storage utilities
- `init_db.py`: Database initialization script
- `templates/`: HTML templates
- `static/`: Static files (CSS, JavaScript, images)

## Features

- User authentication with role-based access control
- Store management
- Comprehensive checklist system
- PDF report generation
- Cloud storage for reports
