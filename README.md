# Certificate Generator Web Application

This web application allows users to generate and verify custom certificates based on student information stored in a database.

## Features

- Search for students by ID, name, or email
- Generate personalized certificates for students
- Download certificates as PDF files
- Verify the authenticity of certificates using a unique student ID
- QR code integration for easy certificate verification

## Prerequisites

- Python 3.7+
- Flask
- MariaDB
- OpenCV
- qrcode
- Pillow
- img2pdf
- pandas
- Gunicorn (for production deployment)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/certificate-generator.git
   cd certificate-generator
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up the MariaDB database and update the `config.py` file with your database credentials. Then create database and data tables by running `mysql/create-database-sql.sql` 

4. Place your certificate template image in the root directory as `Certificate_Template.jpg`.

5. Prepare an Excel file named `file.xlsx` with student information and place it in the root directory. (On the first run of the program, data will be read from the file and written to the database)

## Usage

### Development Environment

1. Start the application:
   ```
   python app.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`.

3. Use the search function to find a student and generate their certificate.

4. To verify a certificate, use the verification page or scan the QR code on the certificate.

### Production Environment

For production deployment, it's recommended to use a WSGI server like Gunicorn. Here's an example of how to run the application using Gunicorn:

1. Install Gunicorn if you haven't already:
   ```
   pip install gunicorn
   ```

2. Run the application with Gunicorn:
   ```
   gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
   ```

   This command starts Gunicorn with 4 worker processes, binding to all network interfaces on port 8000.

3. For HTTPS support, you can use the following command (replace paths with your actual certificate and key locations):
   ```
   gunicorn --workers 4 --bind 0.0.0.0:443 --certfile=/path/to/certfile.pem --keyfile=/path/to/keyfile.pem app:app
   ```

Note: In a production environment, it's recommended to use a reverse proxy server like Nginx in front of Gunicorn for better performance and security.

## File Structure

- `app.py`: Main Flask application
- `config.py`: Configuration file for database and application settings
- `database.py`: Database operations
- `certificate_generator.py`: Certificate generation logic
- `templates/`: HTML templates for the web interface
- `generated_files/`: Directory where generated certificates are stored

## Security Considerations

- Sensitive information (email and phone number) is obfuscated in the API responses.
- Use HTTPS in production to secure data transmission.
- Implement rate limiting to prevent abuse of the certificate generation and verification APIs.
- Ensure proper file permissions are set in the production environment.
- Regularly update all dependencies to their latest secure versions.

## Customization

- To customize the certificate design, replace the `Certificate_Template.jpg` file with your own template.
- Adjust the text positioning in the `certificate_generator.py` file to match your template design.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.