import os
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

# Dracula Colors
BG = '#282a36'
PURPLE = '#bd93f9'
GREEN = '#50fa7b'
PINK = '#ff79c6'

def create_icon_image(size):
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle background
    padding = size // 10
    rect = [padding, padding, size - padding, size - padding]
    radius = size // 5
    draw.rounded_rectangle(rect, radius=radius, fill=BG, outline=PURPLE, width=size//40)
    
    # Draw "E" text or symbol
    # Since we might not have a specific font, let's draw geometric shapes for "E" and "G" (ExifGeek)
    
    # Draw E
    # Vertical bar
    bar_width = size // 8
    start_x = size // 3
    start_y = size // 3
    height = size // 2.5
    
    draw.rectangle(
        [start_x, start_y, start_x + bar_width, start_y + height], 
        fill=GREEN
    )
    
    # Horizontal bars
    arm_len = size // 4
    arm_height = size // 12
    
    # Top
    draw.rectangle(
        [start_x, start_y, start_x + arm_len, start_y + arm_height],
        fill=GREEN
    )
    # Middle
    draw.rectangle(
        [start_x, start_y + height//2 - arm_height//2, start_x + arm_len * 0.8, start_y + height//2 + arm_height//2],
        fill=GREEN
    )
    # Bottom
    draw.rectangle(
        [start_x, start_y + height - arm_height, start_x + arm_len, start_y + height],
        fill=GREEN
    )
    
    # Add a little "Geek" dot
    dot_size = size // 10
    draw.ellipse(
        [size - 2.5*padding, size - 2.5*padding, size - 2.5*padding + dot_size, size - 2.5*padding + dot_size],
        fill=PINK
    )

    return img

def main():
    iconset_dir = 'ExifGeek.iconset'
    if os.path.exists(iconset_dir):
        shutil.rmtree(iconset_dir)
    os.makedirs(iconset_dir)
    
    # Standard icon sizes
    sizes = [16, 32, 128, 256, 512]
    
    for s in sizes:
        # Standard resolution (1x)
        img = create_icon_image(s)
        img.save(os.path.join(iconset_dir, f'icon_{s}x{s}.png'))
        
        # High resolution (2x)
        img_2x = create_icon_image(s * 2)
        img_2x.save(os.path.join(iconset_dir, f'icon_{s}x{s}@2x.png'))

    print(f"Generated PNGs in {iconset_dir}")
    
    # Convert to icns using iconutil
    try:
        subprocess.run(['iconutil', '-c', 'icns', iconset_dir, '-o', 'icon.icns'], check=True)
        print("Successfully created icon.icns")
        # Cleanup
        shutil.rmtree(iconset_dir)
    except Exception as e:
        print(f"Failed to create icns: {e}")

if __name__ == '__main__':
    main()
