from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import os
import time
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'tamilnadu-pride-secret-key-2024'
app.static_folder = 'static'

# Global variable to track if database is initialized
database_initialized = False

def wait_for_database():
    """Wait for database to be ready before connecting"""
    logger.info("🕒 Waiting for database to be ready...")
    time.sleep(20)  # Wait 20 seconds for PostgreSQL to fully start
    logger.info("✅ Database should be ready now")

def get_db_connection():
    """Create connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="postgres-service",        # ← K8s service name
            database="tamilnadu_contacts",
            user="postgres",
            password="postgres", 
            port="5432",
            connect_timeout=10
        )
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise e

def create_table():
    """Create contacts table if it doesn't exist"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Attempting to create table (attempt {attempt + 1})...")
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tbl_contacts (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
            logger.info("✅ Table 'tbl_contacts' created successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Table creation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5  # Increasing wait time
                logger.info(f"🔄 Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error("💥 All table creation attempts failed!")
                return False
    return False

def initialize_database():
    """Initialize database when app starts"""
    global database_initialized
    if not database_initialized:
        wait_for_database()
        if create_table():
            database_initialized = True
        else:
            logger.error("🚨 Database initialization failed!")

# Home page - About Tamilnadu
@app.route('/')
def index():
    return render_template('index.html')

# Contact form page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Handle contact form submission
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    # Initialize database on first form submission
    initialize_database()
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO tbl_contacts (name, email, phone, message) VALUES (%s, %s, %s, %s)',
                (name, email, phone, message)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            flash('🎉 Your message has been sent successfully! We will contact you soon.', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            flash(f'❌ Error sending message: {str(e)}', 'error')
            return redirect(url_for('contact'))

# View all contacts (admin page)
@app.route('/contact_list')
def contact_list():
    # Initialize database when viewing contacts
    initialize_database()
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT id, name, email, phone, message, created_at 
            FROM tbl_contacts 
            ORDER BY created_at DESC
        ''')
        contacts = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('contact_list.html', contacts=contacts)
    except Exception as e:
        flash(f'❌ Error retrieving contacts: {str(e)}', 'error')
        return redirect(url_for('index'))

# Simple health check route
@app.route('/health')
def health():
    try:
        initialize_database()
        return "✅ Application is healthy and database is ready!"
    except Exception as e:
        return f"❌ Health check failed: {e}"

if __name__ == '__main__':
    # Don't initialize database here - let it happen on first request
    logger.info("🚀 Starting Tamil Nadu Pride Flask Application...")
    app.run(host='0.0.0.0', port=5000, debug=True)