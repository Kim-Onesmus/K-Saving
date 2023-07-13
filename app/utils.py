from PIL import Image, ImageDraw, ImageFont
import os

def generate_default_profile_picture(user):
    initials = user.first_name[0] + user.last_name[0]
    size = (100, 100)  # Set the desired size of the image
    image = Image.new('RGB', size, 'green')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()  # You can customize the font and size
    text_size = draw.textsize(initials, font=font)
    position = ((size[0] - text_size[0]) / 2, (size[1] - text_size[1]) / 2)
    draw.text(position, initials, fill='white', font=font)
    
    # Save the generated image with a unique name
    filename = f'{user.first_name}_profile_pic.jpg'
    image.save(os.path.join('media', 'media', filename))
    return filename
