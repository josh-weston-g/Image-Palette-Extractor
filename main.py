from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import requests
from io import BytesIO
import colorsys
import json
import os

# Try to import pyperclip for clipboard functionality
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

# Try to import climage for terminal image display
try:
    from climage import convert
    CLIMAGE_AVAILABLE = True
except ImportError:
    CLIMAGE_AVAILABLE = False

# Function to convert RGB color to hue value for sorting
def rgb_to_hue(color):
    r, g, b = color
    # Normalize RGB values to 0-1 range (colorsys expects this)
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    # Convert to HSV and extract hue (h is between 0-1)
    h = colorsys.rgb_to_hsv(r, g, b)[0]
    return h

# Function to convert RGB to Hex
def rgb_to_hex(colors):
    hex_colors = []
    for color in colors:
        r, g, b = color
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        hex_colors.append(hex_color)
    return hex_colors

# Function to display image in terminal if climage is available
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

# Function to generate clusters - currently sorting colors in this function, might move outside later
def get_clusters(pixels, num_colors):
    # Perform KMeans clustering to reduce the number of colors
    kmeans = KMeans(n_clusters=num_colors, random_state=42).fit(pixels)
    # Get the cluster centers (the representative colors) as integers (normally returns floats)
    colors = kmeans.cluster_centers_.astype(int)
    # Sort colors by hue to create rainbow order
    colors = sorted(colors, key=rgb_to_hue)
    return colors

# Main app loop
while True:
    # Clear the terminal at the start of each loop
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== Image Color Extractor ===")
    # Open image file
    while True:
        try:
            image_path = input("\nEnter path to image file or URL:")
            # Check if input is a URL
            if image_path.startswith(("http://", "https://")):
                print("\nDownloading image from URL...")
                response = requests.get(image_path, timeout=10)
                response.raise_for_status()  # Raise an error for bad responses
                im = Image.open(BytesIO(response.content))
            else:
                im = Image.open(image_path)
            break
        except FileNotFoundError:
            print("File not found. Please enter a valid file path.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}. Please try again.")
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
            exit(0)
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
            print("Conversion successful.\n")
        except Exception as e:
            print(f"An error occurred during conversion: {e}. Please use a different image. Exiting.")
            exit(1)

    # Display image in terminal if possible
    display_image_in_terminal(im)

    # Get list of pixels from image
    # Returns a list of tuples representing each RGB value
    pixels_list = list(im.getdata())

    # Convert list of tuples to a 2D numpy array
    pixels = np.array(pixels_list)

    # Number of colors to reduce the image to
    while True:
        try:
            num_colors = int(input("Enter number of colors to reduce the image to (1-20): "))
            if num_colors < 1 or num_colors > 20:
                print("Please enter a number between 1 and 20.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 20.")
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
            exit(0)

    # Get the clustered colors
    colors = get_clusters(pixels, num_colors)
    # Clear the terminal before printing the extracted colors and their values
    os.system('cls' if os.name == 'nt' else 'clear')

    # Main interaction loop
    while True:
        print(f"\nExtracted {num_colors} colors:")
        hex_colors = rgb_to_hex(colors)
        for i, color in enumerate(colors):
            r, g, b = color
            print(f"\033[48;2;{r};{g};{b}m    \033[0m RGB({r}, {g}, {b}) | Hex: {hex_colors[i]}")
        
        # Provide options to copy values to clipboard or reverse order
        try:
            # Dynamically adjust options based on pyperclip availability
            option1_text = "1. Copy RGB values to clipboard" if PYPERCLIP_AVAILABLE else "1. Copy RGB values to clipboard \033[91m(not active)\033[0m"  # Red
            option2_text = "2. Copy Hex values to clipboard" if PYPERCLIP_AVAILABLE else "2. Copy Hex values to clipboard \033[91m(not active)\033[0m"  # Red
            options = input(f"\nOptions: \n{option1_text} \n{option2_text} \n3. Reverse colour order \n4. Convert to RGBA JSON format \n5. Change number of colours \n\nEnter choice (1-5) or press enter to continue: ")
            
            if options == '1':
                #* Copy RGB values to clipboard
                # Error message if pyperclip not installed
                if not PYPERCLIP_AVAILABLE:
                    # Clear the console
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\033[91mpyperclip module not available. Install pyperclip with: pip install pyperclip\033[0m")  # Red
                    continue
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')
                try:
                    # Convert to list of strings for clipboard
                    colors_list = [f"({color[0]}, {color[1]}, {color[2]})" for color in colors]
                    # Join the list into a single string separated by commas
                    pyperclip.copy(", ".join(colors_list))
                    print("\033[92m\nRGB values copied to clipboard.\033[0m")  # Green
                except Exception as e:
                    print(f"\033[91mFailed to copy RGB values to clipboard: {e}\033[0m")  # Red
                continue
            
            elif options == '2':
                #* Copy Hex values to clipboard
                # Error message if pyperclip not installed
                if not PYPERCLIP_AVAILABLE:
                    # Clear the console
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\033[91mpyperclip module not available. Install pyperclip with: pip install pyperclip\033[0m")  # Red
                    continue
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')
                try:
                    hex_colors = rgb_to_hex(colors)   # We already have this but re-calculate in case colors were modified
                    pyperclip.copy(", ".join(hex_colors))
                    print("\033[92m\nHex values copied to clipboard.\033[0m")  # Green
                except Exception as e:
                    print(f"\033[91mFailed to copy Hex values to clipboard: {e}\033[0m")  # Red
                continue
            
            elif options == '3':
                #* Reverse color order
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')
                colors = colors[::-1]
                print("\033[92m\nColor order reversed.\033[0m")  # Green
                continue
            
            elif options == '4':
                #* Convert to RGBA JSON format
                while True:
                    try:
                        opacity = float(input("\nEnter opacity value (0.0 to 1.0, default 0.15): ") or 0.15)
                        if opacity < 0.0 or opacity > 1.0:
                            print("Please enter a number between 0.0 and 1.0.")
                            continue
                        break
                    except ValueError:
                        print("Invalid opacity value. Please enter a number between 0.0 and 1.0.")
                    except KeyboardInterrupt:
                        print("\nProcess interrupted by user. Exiting.")
                        exit(0)
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')
                # Convert to rgba string format
                colors_list = [f"rgba({color[0]}, {color[1]}, {color[2]}, {opacity})" for color in colors]
                print("\n\033[96mExtracted colors (RGBA):")  # Cyan
                print(json.dumps(colors_list, indent=2))
                print("\033[0m")  # Reset color
                continue
            
            elif options == '5':
                #* Change number of colors
                while True:
                    try:
                        num_colors = int(input("\nEnter new number of colors to extract from the image to (1-20): "))
                        if num_colors < 1 or num_colors > 20:
                            print("Please enter a number between 1 and 20.")
                            continue
                        break
                    except ValueError:
                        print("Invalid input. Please enter a number between 1 and 20.")
                    except KeyboardInterrupt:
                        print("\nProcess interrupted by user. Exiting.")
                        exit(0)
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')
                # Regenerate colors with new number
                colors = get_clusters(pixels, num_colors)
                print("\033[92m\nNumber of colors updated.\033[0m")  # Green
                continue
            
            elif options == '':
                break
            
            else:
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, or press enter to skip.")
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
            exit(0)

    # Ask if user wants to process another image
    try:
        continue_choice = input("\nProcess another image? (y/n): ").lower()
        if continue_choice != 'y':
            print("Exiting program.")
            break
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")
        exit(0)