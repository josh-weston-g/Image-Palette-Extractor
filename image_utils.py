from io import BytesIO
from sklearn.cluster import KMeans

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