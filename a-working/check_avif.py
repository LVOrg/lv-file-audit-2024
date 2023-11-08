from PIL import Image
import pillow_avif
def convert_avif_to_webp(avif_file_path, webp_file_path):
    # Open the AVIF image
    avif_image = Image.open(avif_file_path)

    # Convert the AVIF image to WebP format
    webp_image = avif_image.convert('P')

    # Save the WebP image
    webp_image.save(webp_file_path)
avif_file_path = '/home/vmadmin/python/cy-py/a-working/test.avif'
webp_file_path = '/home/vmadmin/python/cy-py/a-working/test.avif.webp'

convert_avif_to_webp(avif_file_path, webp_file_path)