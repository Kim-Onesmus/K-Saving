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
    
    # Save the generated image in the media directory
    filename = f'{user.first_name}_profile_pic.jpg'
    file_path = os.path.join(settings.MEDIA_ROOT, 'media', filename)
    image.save(file_path)
    
    # Return the relative URL of the saved image
    return os.path.join('media', filename)
