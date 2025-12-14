import numpy as np
from sklearn.cluster import KMeans

class ImagePalette:
    """
    A class to represent an image and its extracted color palette.

    This class handles loading an image, extracting its dominant colors,
    and providing methods to manipulate and export the color palette.
    """

    def __init__(self, image, num_colors):
        """
        Initialize the ImagePalette with a PIL Image and number of colors.

        :param image: PIL Image object.
        :param num_colors: Number of dominant colors to extract.
        """
        # Store number of colors
        self.num_colors = num_colors
        # Store the image
        self.image = image
        # Process image (resize, convert to RGB, display)
        self.image = self._process_image()
        # Extract pixel data as numpy array
        self.pixels = self._extract_pixels()
        # Extract the color palette using KMeans clustering
        self.colors = self._extract_colors(self.pixels, self.num_colors)
        # Set default sort method (hue)
        self.current_sort = "hue"
        # Apply initial sort
        self.sort_by("hue")
        # Initialise state tracking for: filtering, complementary colors and show HSV values
        self.is_filtered = False
        self.is_complementary = False
        self.original_unfiltered_colors = None # For filter restoration
        self.show_hsv = False

    def _process_image(self):
        """
        Process the loaded image: resize, convert to RGB, and display
        
        :return: Processed PIL Image object in RGB mode
        """
        from image_utils import display_image_in_terminal

        # Display image info
        print(f"\nFile type: {self.image.format}")
        print(f"Image size: {self.image.size}")
        print(f"Image mode: {self.image.mode}")

        # Resize image to speed up processing
        self.image.thumbnail((200, 200))
        print(f"Resized image size: {self.image.size}\n")

        # Convert to RGB if necessary
        if self.image.mode != "RGB":
            print(f"Converting image from {self.image.mode} to RGB mode for processing...\n")
            try:
                self.image = self.image.convert("RGB")
                print("Conversion successful.\n")
            except Exception as e:
                raise Exception(f"Conversion failed: {e}. Please use a different image.")
            
        # Display image in terminal if possible
        display_image_in_terminal(self.image)
        try:
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            print("\nExiting the program. Goodbye!")
            exit(0)

        return self.image
    
    def _extract_pixels(self):
        """
        Extract pixel data from the image as a numpy array.

        :return: Numpy array of RGB pixel values.
        """
        pixel_list = list(self.image.getdata())
        pixels = np.array(pixel_list)
        return pixels
    
    def _extract_colors(self, pixels, num_colors):
        """
        Extract dominant colors from pixel data using KMeans clustering.
        
        :param pixels: Numpy array of RGB pixel values.
        :param num_colors: Number of dominant colors to extract.

        :return: Numpy array of RGB color values (cluster centers).
        """
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=num_colors, random_state=42).fit(pixels)
        # Get cluster centers as integers
        colors = kmeans.cluster_centers_.astype(int)
        return colors
    
    def sort_by(self, method):
        """
        Sort colors by the specific method

        :param method: Sort method - "hue", "saturation", "brightness"
        """
        from color_utils import rgb_to_hue, rgb_to_saturation, rgb_to_brightness
        if method == "hue":
            self.colors = sorted(self.colors, key=rgb_to_hue)
        elif method == "saturation":
            self.colors = sorted(self.colors, key=rgb_to_saturation)
        elif method == "brightness":
            self.colors = sorted(self.colors, key=rgb_to_brightness)

        # Update current sort method
        self.current_sort = method
    
    def reverse(self):
        """
        Reverse the order of the colors in the palette.
        """
        self.colors = self.colors[::-1]

    def get_hex_list(self):
        """
        Get the list of colors in hexadecimal format.

        :return: List of hex color strings.
        """
        from color_utils import rgb_to_hex
        return rgb_to_hex(self.colors)
    
    def get_rgb_list(self):
        """
        Get the list of colors in RGB format.

        :return: List of RGB color tuples.
        """
        # Convert numpy array to list of tuples
        return [tuple(color) for color in self.colors]
    
    def get_rgba_list(self, opacity=0.15):
        """
        Get the list of colors in RGBA format with specified opacity.

        :param opacity: Opacity value between 0 and 1 (default is 0.15).

        :return: List of RGBA strings (e.g., ['rgba(255, 87, 51, 0.15)'])        
        """
        rgba_list = []
        for color in self.colors:
            r, g, b = color
            rgba_list.append(f"rgba({r}, {g}, {b}, {opacity})")
        return rgba_list
    
    def extract_palette(self, num_colors):
        """
        Re-extract the color palette with a different number of colors.

        :param num_colors: New number of dominant colors to extract.
        """
        self.num_colors = num_colors
        self.colors = self._extract_colors(self.pixels, self.num_colors)
        # Re-apply current sort
        self.sort_by(self.current_sort)

        # Remove any filtering if active and complementary state
        if self.is_filtered:
            self.is_filtered = False
            self.original_unfiltered_colors = None
        if self.is_complementary:
            self.is_complementary = False

    def filter_colors(self, filter_dark=True, filter_light=True, min_brightness=0.15, max_brightness=0.85):
        """
        Filter out near-black and/or near-white colors from the pixel data
        and re-extract the color palette.

        :param filter_dark: Whether to filter very dark colors.
        :param filter_light: Whether to filter very light colors.
        :param min_brightness: Brightness threshold for dark colors (0-1).
        :param max_brightness: Brightness threshold for light colors (0-1).
        """
        from image_utils import filter_extreme_pixels

        # If complementary is active, turn it off and restore original colors
        if self.is_complementary:
            self.to_complementary()

        if not self.is_filtered:
            # Store original pixels before filtering
            self.original_unfiltered_colors = self.colors.copy()

        # Filter pixels
        filtered_pixels = filter_extreme_pixels(
            self.pixels,
            filter_dark=filter_dark,
            filter_light=filter_light,
            min_brightness=min_brightness,
            max_brightness=max_brightness
        )

        # Re-extract colors from filtered pixels
        self.colors = self._extract_colors(filtered_pixels, self.num_colors)
        # Re-apply current sort
        self.sort_by(self.current_sort)

        # Mark as filtered
        self.is_filtered = True

    def remove_filter(self):
        """
        Remove any applied filters and restore the original color palette.
        """
        if self.is_filtered and self.original_unfiltered_colors is not None:
            self.colors = self.original_unfiltered_colors
            self.sort_by(self.current_sort)
            self.is_filtered = False
            self.original_unfiltered_colors = None
            # Also reset complementary state
            self.is_complementary = False

    def to_complementary(self):
        """
        Convert the current colors to their complementary colors.
        Used to toggle complementary colors on and off.
        """
        from color_utils import rgb_to_complement
        # Convert each color to its complementary color and convert back to numpy array
        self.colors = np.array([rgb_to_complement(color) for color in self.colors])
        # Re-apply current sort
        self.sort_by(self.current_sort)
        self.is_complementary = not self.is_complementary