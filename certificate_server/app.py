from flask import Flask, request, jsonify, send_file, render_template, url_for
from flask_cors import CORS
import os
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
from certificate_generator import generate_certificate
from config import SECRET_KEY
from database import get_person, log_certificate_download

# Initialize Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = SECRET_KEY

# Enable CORS for all routes and all origins
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

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

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")
        return jsonify({"error": "Failed to render template"}), 500

@app.route('/verify')
def verify_page():
    return render_template('verify.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/person', methods=['GET'])
def get_person_api():
    search_term = request.args.get('search')
    logging.info(f"Searching for: {search_term}")
    
    person = get_person(search_term)
    
    if not person:
        logging.info(f"No person found for search term: {search_term}")
        return jsonify({"error": "Person not found"}), 404
    
    # Obfuscate sensitive information
    person['Email'] = obfuscate_email(person['Email'])
    person['phone_no'] = obfuscate_phone(person['phone_no'])
    
    # Add certificate download link
    person['certificate_link'] = url_for('get_certificate', student_id=person['student_id'])
    
    logging.info(f"Person found: {person}")
    return jsonify(person)

@app.route('/api/certificate/<student_id>', methods=['GET'])
def get_certificate(student_id):
    output_dir = "generated_files"
    pdf_path = os.path.join(output_dir, f"{student_id}.pdf")
    
    if not os.path.exists(pdf_path):
        # Create certificate if it doesn't exist
        person = get_person(student_id)
        if not person:
            return jsonify({"error": "Person not found"}), 404
        
        student_name = person['full_name']
        pdf_path = generate_certificate(student_name, str(student_id))
        
        if pdf_path is None:
            return jsonify({"error": "Failed to create certificate"}), 500

    # Log the download
    log_certificate_download(student_id)

    return send_file(pdf_path, as_attachment=True, download_name=f"certificate_{student_id}.pdf", mimetype='application/pdf')

@app.route('/api/verify/<student_id>', methods=['GET'])
def verify_student(student_id):
    person = get_person(student_id)
    
    if not person:
        return jsonify({"error": "Student not found"}), 404
    
    return jsonify({"full_name": person['full_name']})

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