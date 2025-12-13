from cli import clear_screen, load_image, get_color_count, handle_color_options
from image_palette import ImagePalette

# Main app loop
while True:
    clear_screen()
    print("=== Image Color Palette Extractor ===")

    # Get image from user
    image = load_image()
    
    # Now get color count and create palette
    num_colors = get_color_count()
    palette = ImagePalette(image, num_colors)

    # Handle color options menu
    handle_color_options(palette)