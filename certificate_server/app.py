import os
from flask import Flask, request, jsonify, send_file, render_template

# Initialize Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set up template directory
template_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(template_dir, 'templates')
app.template_folder = template_dir

# ... (rest of the imports and configurations)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering template: {str(e)}")
        return jsonify({"error": "Failed to render template"}), 500

# ... (rest of the routes and functions)

if __name__ == '__main__':
    try:
        # Check if template exists
        if not os.path.exists(os.path.join(app.template_folder, 'index.html')):
            raise FileNotFoundError("index.html template not found in templates directory")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        
        run_simple('0.0.0.0', 5000, app, ssl_context=context, use_reloader=False, use_debugger=False)
    except Exception as e:
        logging.error(f"Failed to start server: {str(e)}")
        print(f"Error: {str(e)}")