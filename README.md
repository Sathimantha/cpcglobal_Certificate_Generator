# Certificate Generator Web Application

This Flask-based web application allows users to search for individuals and generate personalized certificates.

## Features

- Search for individuals by name, student ID, or email
- Generate personalized certificates with QR codes
- Privacy-focused: obfuscates sensitive information in search results
- Optional SSL support for secure deployment

## Requirements

- Python 3.7+
- Flask
- OpenCV (cv2)
- qrcode
- Pillow (PIL)
- img2pdf
- pandas

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/certificate-generator.git
cd certificate-generator
```

2. Install required packages:

```
pip install flask opencv-python qrcode Pillow img2pdf pandas
```
3. Prepare your data:
- Place your Excel file with student data in the project root as `file.xlsx`
- Put your certificate template image in the project root as `Certificate_Template.jpg`

## Usage

1. Run the application:
- Without SSL:
  ```
  python3 app.py
  ```
- With SSL:
  ```
  python3 app.py --ssl
  ```

2. Access the application:
- Without SSL: `http://127.0.0.1:5000`
- With SSL: `https://127.0.0.1:5000`

## SSL Configuration

To use SSL:

1. Ensure you have SSL certificate files:
- Certificate: `/opt/bitnami/apache/conf/bitnami/certs/server.crt`
- Key: `/opt/bitnami/apache/conf/bitnami/certs/server.key`

2. Run the application with the `--ssl` flag as shown above.

## Project Structure
certificate-generator/
├── app.py
├── file.xlsx
├── Certificate_Template.jpg
├── templates/
│   └── index.html
└── generated_files/
└── (generated PDFs will be stored here)

## Customization

- Modify `file.xlsx` to update student data
- Replace `Certificate_Template.jpg` with your own template design
- Adjust certificate generation parameters in `app.py` as needed

## Security Notes

- This application obfuscates sensitive information in search results
- Use SSL in production environments for secure data transmission
- Ensure proper access controls are in place for the application and generated certificates

## Support

For issues or feature requests, please open an issue on the GitHub repository.