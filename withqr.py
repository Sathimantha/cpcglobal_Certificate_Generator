import cv2
import numpy as np

# Load the certificate template image
certificate_template_image = cv2.imread("certificate-template.jpg")

if certificate_template_image is None:
    print("Error: Unable to load certificate template image")
    exit(1)

# Load the QR code image
qr_code_image = cv2.imread("qrcode.png")

if qr_code_image is None:
    print("Error: Unable to load QR code image")
    exit(1)

# Resize the QR code image to fit on the certificate
qr_code_image = cv2.resize(qr_code_image, (150, 150))

# Create a mask for the QR code
mask = 255 * np.ones((150, 150, 3), dtype=np.uint8)

# Get the top right corner coordinates for the QR code
top, right = 50, certificate_template_image.shape[1] - 150
bottom, left = top + 150, right - 150

# Blend the QR code image with the certificate template image
blended_image = certificate_template_image.copy()
blended_image[top:bottom, left:right] = cv2.addWeighted(blended_image[top:bottom, left:right], 1, qr_code_image, 0.5, 0)

# Save the blended image
cv2.imwrite("certificate_with_qr_code.jpg", blended_image)