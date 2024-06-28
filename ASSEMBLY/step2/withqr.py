from PIL import Image

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