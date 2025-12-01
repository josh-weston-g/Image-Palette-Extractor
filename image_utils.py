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