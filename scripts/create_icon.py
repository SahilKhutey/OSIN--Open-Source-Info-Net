import sys
import os
from PIL import Image

def convert_to_ico(input_path, output_path):
    """Converts a PNG/JPG to a multi-size Windows .ico file"""
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return False
    
    try:
        img = Image.open(input_path)
        # Use a high-quality resampling for the multiple sizes Windows expects
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # We'll create the ico from the image
        img.save(output_path, format='ICO', sizes=icon_sizes)
        print(f"Success: Icon created at {output_path}")
        return True
    except Exception as e:
        print(f"Failed to convert icon: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_icon.py <input_png> <output_ico>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_to_ico(input_file, output_file)
