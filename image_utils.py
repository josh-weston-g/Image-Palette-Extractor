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

# Function to generate clusters
def get_clusters(pixels, num_colors):
    # Perform KMeans clustering to reduce the number of colors
    kmeans = KMeans(n_clusters=num_colors, random_state=42).fit(pixels)
    # Get the cluster centers (the representative colors) as integers (normally returns floats)
    colors = kmeans.cluster_centers_.astype(int)
    return colors

# Function to process image for clustering - display info, resize, convert to RGB and display in terminal
def process_image(im):
    # Display image format, size and mode
    print(f"\nFile type: {im.format} \nImage size: {im.size} \nImage mode: {im.mode}")

    # Resize image to speed up cluster processing - we use thumbnail to maintain aspect ratio
    # Longest side will be 200 pixels
    im.thumbnail((200, 200))
    print(f"Resized image size: {im.size}\n")

    # Convert image to RGB if not already in that mode
    if im.mode != "RGB":
        print(f"Converting image from {im.mode} to RGB mode for processing...\n")
        try:
            im = im.convert("RGB")
            print("Conversion successful.\n")
        except Exception as e:
            print(f"Conversion failed: {e}. Please use a different image. Exiting.\n")
            exit(1)

    # Display image in terminal if possible
    display_image_in_terminal(im)

    return im

def extract_pixels(im):
    # Extract pixel data from image and reshape for clustering
    pixels_list = list(im.getdata())
    pixels = np.array(pixels_list)
    return pixels

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