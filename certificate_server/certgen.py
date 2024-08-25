import os
import logging
from certificate_generator import generate_certificate
from database import get_person  # Import the get_person function from your database module

# Configure logging
logging.basicConfig(level=logging.INFO)

def generate_certificates_batch(start_id, end_id):
    for student_id in range(start_id, end_id + 1):
        # Get person data from the database
        person = get_person(str(student_id))
        
        if person:
            student_name = person['full_name']
            pdf_path = generate_certificate(student_name, str(student_id))
            
            if pdf_path:
                logging.info(f"Certificate generated for Student ID {student_id} ({student_name}): {pdf_path}")
            else:
                logging.error(f"Failed to generate certificate for Student ID {student_id} ({student_name})")
        else:
            logging.warning(f"No data found for Student ID {student_id}")

if __name__ == "__main__":
    # Ensure the output directory exists
    output_dir = "generated_files"
    os.makedirs(output_dir, exist_ok=True)

    # Generate certificates for student IDs 1 through 50
    generate_certificates_batch(1, 50)

    logging.info("Certificate generation process completed.")