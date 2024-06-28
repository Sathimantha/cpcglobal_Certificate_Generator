import qrcode

url = "https://verify.cpcglobal.org#"
unique_number = "12345"  # Replace with your unique number
qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H)
qr.add_data(f"{url}{unique_number}")
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="transparent")
img.save("qrcode.png")