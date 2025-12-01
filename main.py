# Import functions from util files
from image_utils import get_clusters, process_image, extract_pixels
from cli import clear_screen, get_image_from_user, get_color_count, handle_color_options, ask_continue

# Main app loop
while True:
    # Clear the terminal at the start of each loop
    clear_screen()
    print("=== Image Color Extractor ===")
    
    # Get image from user (file path or URL)
    im = get_image_from_user()

    # Process the image (display info -> resize -> convert to RGB -> display resized image in terminal)
    im = process_image(im)

    # Extract pixel data from image
    pixels = extract_pixels(im)

    # Get number of colors to reduce the image to
    num_colors = get_color_count()

    # Get the clustered colors
    colors = get_clusters(pixels, num_colors)
    
    # Handle color options menu
    handle_color_options(colors, num_colors, pixels)

    # Ask user if they want to process another image
    if not ask_continue():
        print("Exiting the program. Goodbye!")
        break