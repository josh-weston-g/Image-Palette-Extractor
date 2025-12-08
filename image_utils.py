from io import BytesIO
from sklearn.cluster import KMeans
import numpy as np

# Try to import climage for terminal image display
try:
    from climage import convert
    CLIMAGE_AVAILABLE = True
except ImportError:
    CLIMAGE_AVAILABLE = False

def display_image_in_terminal(img):
    if CLIMAGE_AVAILABLE:
        try:
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            output = convert(buffer, width=60, is_unicode=True)
            print("Resized image preview:")
            print(output)
        except Exception as e:
            print(f"Could not display image in terminal: {e}")
    else:
        print("climage module not available. Install climage with: pip install climage")

# Function to filter out near-white and/or near-black colors
def filter_extreme_pixels(pixels, filter_dark=True, filter_light=True, min_brightness=0.15, max_brightness=0.85):
    """
    Filter out pixels that are too dark or too light based on brightness.
    
    Args:
        pixels: numpy array of RGB pixels
        filter_dark: whether to filter very dark pixels
        filter_light: whether to filter very light pixels  
        min_brightness: threshold for dark pixels (0-1), default 0.15
        max_brightness: threshold for light pixels (0-1), default 0.85
    
    Returns:
        Filtered numpy array of pixels, or original if insufficient pixels remain
    """
    from color_utils import rgb_to_brightness
    filtered_pixels = []
    for pixel in pixels:
        brightness = rgb_to_brightness(pixel)
        
        # Check if pixel should be excluded
        too_dark = filter_dark and (brightness < min_brightness)
        too_light = filter_light and (brightness > max_brightness)

        if not (too_dark or too_light):
            filtered_pixels.append(pixel)

    # If we filtered out too many pixels, return original
    if len(filtered_pixels) < 100: # Need at least some pixels to cluster
        print("\033[91mWarning: \033[0mToo many pixels filtered out. Using original pixel set for clustering.") # red
        return pixels
        
    return np.array(filtered_pixels)