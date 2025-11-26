from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

# Open image file
while True:
    imagePath = input("Enter path to image file: ")
    try:
        im = Image.open(imagePath)
        break
    except FileNotFoundError:
        print("File not found. Please enter a valid file path.")
    except Exception as e:
        print(f"An error occurred: {e}. Please try again.")

# Display image format, size, and mode - used for debugging
print(f"\nFile type: {im.format} \nImage size: {im.size} \nImage mode: {im.mode}")

# Show the image - used for debugging
# im.show()

# Resize image to speed up cluster processing - we use thumbnail to maintain aspect ratio
# Longest side will be 200 pixels
im.thumbnail((200, 200))
print(f"Resized image size: {im.size}\n")

# Convert image to RGB if it is in a different mode (e.g., RGBA, P)
if im.mode != "RGB":
    print(f"Converting image from {im.mode} to RGB mode...\n")
    try:
        im = im.convert("RGB")
    except Exception as e:
        print(f"An error occurred during conversion: {e}. Please use a different image. Exiting.")
        exit(1)

# Get list of pixels from image
# Returns a list of tuples representing each RGB value
pixelsList = list(im.getdata())

# Convert list of tuples to a 2D numpy array
pixels = np.array(pixelsList)

# Number of colors to reduce the image to
while True:
    try:
        numColors = int(input("Enter number of colors to redudce the image to (1-20): "))
        if numColors < 1 or numColors > 20:
            print("Please enter a number between 1 and 20.")
            continue
        break
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 20.")

# Perform KMeans clustering to reduce the number of colors
kmeans = KMeans(n_clusters=numColors, random_state=42).fit(pixels)
# Get the cluster centers (the representative colors) as integers (normally returns floats)
colors = kmeans.cluster_centers_.astype(int)
# Print the extracted colors and their values
print("\nExtracted colors:")
for color in colors:
    r, g, b = color
    print(f"\033[48;2;{r};{g};{b}m    \033[0m RGB({r}, {g}, {b})")