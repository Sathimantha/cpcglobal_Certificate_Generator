from flask import Flask, request, jsonify, send_file, render_template
import os
import cv2
import qrcode
from PIL import Image
import img2pdf
import logging
import pandas as pd
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix
import ssl

# Initialize Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

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

# SSL certificate paths
cert_file = '/opt/bitnami/apache/conf/bitnami/certs/server.crt'
key_file = '/opt/bitnami/apache/conf/bitnami/certs/server.key'

# ... [Keep all the existing functions: obfuscate_email, obfuscate_phone, generate_certificate] ...

@app.route('/')
def home():
    return render_template('index.html')

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
    
    logging.info(f"Person found: {person_data}")
    return jsonify(person_data)

@app.route('/api/generate_certificate', methods=['POST'])
def generate_certificate_api():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    student_name = data.get('full_name')
    student_id = data.get('student_id')
    
    if not student_name or not student_id:
        return jsonify({"error": "Missing required fields: full_name or student_id"}), 400
    
    student_id = str(student_id)
    
    pdf_path = generate_certificate(student_name, student_id)
    
    if pdf_path is None:
        return jsonify({"error": "Failed to generate certificate. Check server logs for details."}), 500
    
    return jsonify({"message": "Certificate generated successfully", "pdf_path": pdf_path})

@app.route('/api/certificate/<student_id>', methods=['GET'])
def get_certificate(student_id):
    pdf_path = f"generated_files/{student_id}.pdf"
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')
    else:
        return jsonify({"error": "Certificate not found"}), 404

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    app.logger.error(f"Unhandled exception: {str(e)}")
    # Return JSON instead of HTML for HTTP errors
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        
        run_simple('0.0.0.0', 5000, app, ssl_context=context, use_reloader=False, use_debugger=False)
    except Exception as e:
        logging.error(f"Failed to start server: {str(e)}")
        print(f"Error: {str(e)}")