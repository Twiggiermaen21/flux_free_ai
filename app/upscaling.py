import os
from PIL import Image

def upscale_image(input_path, output_path):
  
   
    output_dir = 'upscaled_images'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, os.path.basename(output_path))
    # Open and resize image
    image = Image.open(input_path)
    new_size = (image.width * 2, image.height * 2)
    upscaled_image = image.resize(new_size, Image.LANCZOS)

    # Save the upscaled image with 300 DPI
    dpi = (300, 300)
    upscaled_image.save(output_path, dpi=dpi)
    print(f"Zapisano obraz z upscalingiem i 300 DPI jako {output_path}")