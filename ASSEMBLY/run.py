#Certificate_Template.jpg = certicate template name
#list_of_names = Name List comes here 'name-data.txt'

import os #For Certificate Generator
import cv2 #For Certificate Generator

import qrcode #For QR Generator

from PIL import Image #For QR Paster

import img2pdf #For pdf out


#-- Certificate Generator Start --#
list_of_names = []

def delete_old_data():
   for i in os.listdir("generated-files/"):
      os.remove("generated-files/{}".format(i))

def cleanup_data():
   with open('name-data.txt') as f: #============== TO DO
      for line in f:
          list_of_names.append(line.strip())

def generate_certificates():

   for index, name in enumerate(list_of_names):
      certificate_template_image = cv2.imread("Certificate_Template.jpg")
      cv2.putText(certificate_template_image, name.strip(), (800,2420), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 250), 5, cv2.LINE_AA)
      cv2.imwrite("generated-files/{}.jpg".format(name.strip()), certificate_template_image)
      print("Processing {} / {}".format(index + 1,len(list_of_names)))
      
#-- Certificate Generator End --#

#-- QR Generator Start --#
def generate_qr():
   url = "https://verify.cpcglobal.org#"
   unique_number = "12345"  # Replace with your unique number ============ TO DO
   qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H)
   qr.add_data(f"{url}{unique_number}")
   qr.make(fit=True)
   img = qr.make_image(fill_color="black", back_color="transparent")
   img.save("generated-files/qrcode.png")
#-- QR Generator End --#

#-- QR Paster Start --#
def qr_paster():
   jpeg_img = Image.open('certificate-template.jpg')
   png_img = Image.open('qrcode.png')

   # Create a new image with the same size as the JPEG image
   result_img = Image.new('RGBA', jpeg_img.size, (255, 255, 255, 0))

   # Paste the JPEG image onto the new image
   result_img.paste(jpeg_img, (0, 0))

   # Paste the PNG image onto the new image at the top-right corner
   result_img.paste(png_img, (jpeg_img.width - png_img.width - 90, 90), mask=png_img)

   result_img = result_img.convert('RGB')
   # Save the resulting image
   result_img.save('output.jpg','JPEG')
#-- QR Paster Start --#


#-- jpgtopdf Start --#
def jpg_to_pdf(jpg_file, pdf_file):
    with open(jpg_file, 'rb') as f:
        img_bytes = f.read()
    pdf_bytes = img2pdf.convert(img_bytes)
    with open(pdf_file, 'wb') as f:
        f.write(pdf_bytes)

def output_pdf():
   jpg_file = 'Certificate_demo.jpg'
   pdf_file = 'output.pdf'
   jpg_to_pdf(jpg_file, pdf_file)
#-- jpgtopdf End --#


def main():
   delete_old_data()
   cleanup_data()
   generate_certificates()
   generate_qr()
   qr_paster()
   output_pdf()


if __name__ == '__main__':
   main()






