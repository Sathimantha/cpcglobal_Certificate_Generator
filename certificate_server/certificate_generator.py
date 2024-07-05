import os
import cv2
import qrcode
from PIL import Image
import img2pdf
import logging

logging.basicConfig(level=logging.INFO)

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