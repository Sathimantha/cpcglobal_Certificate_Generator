from flask import Flask, request, jsonify, send_file, render_template, url_for, session, redirect
from flask_cors import CORS
import os
import logging
import pandas as pd
from werkzeug.middleware.proxy_fix import ProxyFix
from certificate_generator import generate_certificate
from datetime import datetime
from admin_functions import load_data, refresh_data, toggle_caching, get_download_stats
from config import ADMIN_PASSWORD, SECRET_KEY

# Initialize Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Enable CORS for all routes and all origins
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load the DataFrame
try:
    df = pd.read_excel('file.xlsx')
except Exception as e:
    logging.error(f"Error loading Excel file: {str(e)}")
    df = None

# Set up template directory
template_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(template_dir, 'templates')
app.template_folder = template_dir

def obfuscate_email(email):
    if not email:
        return ""
    parts = email.split('@')
    if len(parts) != 2:
        return email  # Return original if it's not a valid email
    username, domain = parts
    return f"{username[:3]}{'*' * (len(username) - 3)}@{domain}"

def obfuscate_phone(phone):
    if not phone:
        return ""
    phone = str(phone)  # Convert to string in case it's stored as a number
    return f"{'*' * (len(phone) - 4)}{phone[-4:]}"

def log_certificate_download(student_id):
    log_file = 'certificate_downloads.xlsx'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if os.path.exists(log_file):
        log_df = pd.read_excel(log_file)
    else:
        log_df = pd.DataFrame(columns=['Timestamp', 'Student ID'])
    
    new_row = pd.DataFrame({'Timestamp': [timestamp], 'Student ID': [student_id]})
    log_df = pd.concat([log_df, new_row], ignore_index=True)
    
    log_df.to_excel(log_file, index=False)
    logging.info(f"Logged certificate download for student ID: {student_id}")

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")
        return jsonify({"error": "Failed to render template"}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/person', methods=['GET'])
def get_person():
    search_term = request.args.get('search')
    logging.info(f"Searching for: {search_term}")
    
    if df is None:
        return jsonify({"error": "Database not available"}), 500

    # Search in student_id, full_name, and Email columns
    person = df[
        (df['student_id'].astype(str).str.lower() == search_term.lower()) |
        (df['full_name'].str.lower() == search_term.lower()) |
        (df['Email'].str.lower() == search_term.lower())
    ]
    
    if person.empty:
        logging.info(f"No person found for search term: {search_term}")
        return jsonify({"error": "Person not found"}), 404
    
    person_data = person.iloc[0].to_dict()
    
    # Obfuscate sensitive information
    person_data['Email'] = obfuscate_email(person_data['Email'])
    person_data['phone_no'] = obfuscate_phone(person_data['phone_no'])
    
    # Add certificate download link
    person_data['certificate_link'] = url_for('get_certificate', student_id=person_data['student_id'])
    
    logging.info(f"Person found: {person_data}")
    return jsonify(person_data)

@app.route('/api/certificate/<student_id>', methods=['GET'])
def get_certificate(student_id):
    output_dir = "generated_files"
    pdf_path = os.path.join(output_dir, f"{student_id}.pdf")
    
    if not os.path.exists(pdf_path):
        # Create certificate if it doesn't exist
        person = df[df['student_id'].astype(str) == str(student_id)]
        if person.empty:
            return jsonify({"error": "Person not found"}), 404
        
        student_name = person.iloc[0]['full_name']
        pdf_path = generate_certificate(student_name, str(student_id))
        
        if pdf_path is None:
            return jsonify({"error": "Failed to create certificate"}), 500

    # Log the download
    log_certificate_download(student_id)

    return send_file(pdf_path, as_attachment=True, download_name=f"certificate_{student_id}.pdf", mimetype='application/pdf')

# ... (admin routes)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid password")
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    stats = get_download_stats()
    return render_template('admin.html', stats=stats)

@app.route('/api/refresh_data', methods=['POST'])
def api_refresh_data():
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    return refresh_data()

@app.route('/api/toggle_caching', methods=['POST'])
def api_toggle_caching():
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    return toggle_caching()


# ... (admin routes)


@app.errorhandler(404)
def not_found_error(error):
    logging.info(f"404 Error: {request.url}")
    return jsonify(error="Not Found"), 404

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify(error="Internal Server Error"), 500

if __name__ == '__main__':
    try:
        # Check if template exists
        if not os.path.exists(os.path.join(app.template_folder, 'index.html')):
            raise FileNotFoundError("index.html template not found in templates directory")
        
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Failed to start server: {str(e)}")
        print(f"Error: {str(e)}")