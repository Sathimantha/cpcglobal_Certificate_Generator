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
app.template_folder = template_dir

# SSL certificate paths
cert_file = '/opt/bitnami/apache/conf/bitnami/certs/server.crt'
key_file = '/opt/bitnami/apache/conf/bitnami/certs/server.key'

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

def generate_certificate(student_name, student_id):
    try:
        # Certificate generation
        template_path = "Certificate_Template.jpg"
        if not os.path.exists(template_path):
            logging.error(f"Certificate template not found at {template_path}")
            return None

        certificate_template_image = cv2.imread(template_path)
        if certificate_template_image is None:
            logging.error(f"Failed to load certificate template from {template_path}")
            return None

        cv2.putText(certificate_template_image, student_name, (800, 2420), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 250), 5, cv2.LINE_AA)
        
        output_dir = "generated_files"
        os.makedirs(output_dir, exist_ok=True)
        
        cv2.imwrite(f"{output_dir}/{student_id}.jpg", certificate_template_image)

        # QR code generation
        url = "https://verify.cpcglobal.org#"
        qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(f"{url}{student_id}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="transparent")
        img.save(f"{output_dir}/{student_id}_qr.png")

        # Paste QR code onto certificate
        jpeg_img = Image.open(f"{output_dir}/{student_id}.jpg")
        png_img = Image.open(f"{output_dir}/{student_id}_qr.png")

        result_img = Image.new('RGBA', jpeg_img.size, (255, 255, 255, 0))
        result_img.paste(jpeg_img, (0, 0))
        result_img.paste(png_img, (jpeg_img.width - png_img.width - 90, 90), mask=png_img)

        result_img = result_img.convert('RGB')
        result_img.save(f"{output_dir}/{student_id}_with_qr.jpg", 'JPEG')

        # Convert to PDF
        with open(f"{output_dir}/{student_id}_with_qr.jpg", 'rb') as f:
            img_bytes = f.read()
        pdf_bytes = img2pdf.convert(img_bytes)
        pdf_path = f"{output_dir}/{student_id}.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)

        # Clean up temporary files
        os.remove(f"{output_dir}/{student_id}.jpg")
        os.remove(f"{output_dir}/{student_id}_qr.png")
        os.remove(f"{output_dir}/{student_id}_with_qr.jpg")

        logging.info(f"Certificate generated successfully for student ID: {student_id}")
        return pdf_path

    except Exception as e:
        logging.error(f"Error generating certificate for student ID {student_id}: {str(e)}")
        return None

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
            raise FileNotFoundError("index.html template not found")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        
        run_simple('0.0.0.0', 5000, app, ssl_context=context, use_reloader=False, use_debugger=False)
    except Exception as e:
        logging.error(f"Failed to start server: {str(e)}")
        print(f"Error: {str(e)}")