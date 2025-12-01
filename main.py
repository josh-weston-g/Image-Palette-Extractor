from PIL import Image
import numpy as np
import requests
from io import BytesIO
import json
import os

# Import functions from util files
from color_utils import rgb_to_hex, rgb_to_hue, rgb_to_saturation, rgb_to_brightness
from image_utils import display_image_in_terminal, get_clusters

# Try to import pyperclip for clipboard functionality
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

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
    current_sort = "hue" # Track current sort method
    colors = sorted(colors, key=rgb_to_hue)
    os.system('cls' if os.name == 'nt' else 'clear')

    # Main interaction loop
    while True:
        print(f"\nExtracted {num_colors} colors (sorted by {current_sort}):")
        hex_colors = rgb_to_hex(colors)
        for i, color in enumerate(colors):
            r, g, b = color
            h = rgb_to_hue(color)
            s = rgb_to_saturation(color)
            v = rgb_to_brightness(color)
            print(f"\033[48;2;{r};{g};{b}m    \033[0m RGB({r}, {g}, {b}) | Hex: {hex_colors[i]}")
            # Optional: print HSV values for debugging
            # print(f"\033[48;2;{r};{g};{b}m    \033[0m RGB({r}, {g}, {b}) | Hex: {hex_colors[i]} | H:{h:.2f} S:{s:.2f} V:{v:.2f}")
        
        # Provide options to copy values to clipboard or reverse order
        try:
            # Dynamically adjust options based on current sort method
            if current_sort == "hue":
                option2_text = "2. Sort by saturation"
                option3_text = "3. Sort by brightness"
            elif current_sort == "saturation":
                option2_text = "2. Sort by hue"
                option3_text = "3. Sort by brightness"
            elif current_sort == "brightness":
                option2_text = "2. Sort by saturation"
                option3_text = "3. Sort by hue"

            # Dynamically adjust options based on pyperclip availability
            option4_text = "4. Copy RGB values to clipboard" if PYPERCLIP_AVAILABLE else "4. Copy RGB values to clipboard \033[91m(not active)\033[0m"  # Red
            option5_text = "5. Copy Hex values to clipboard" if PYPERCLIP_AVAILABLE else "5. Copy Hex values to clipboard \033[91m(not active)\033[0m"  # Red

            options = input(f"\nOptions: \n\n\033[1m--- Color Manipulation ---\033[0m\n1. Reverse colour order \n{option2_text} \n{option3_text} \n\n\033[1m--- Export/Copy ---\033[0m\n{option4_text} \n{option5_text} \n6. Convert to RGBA JSON format \n\n\033[1m--- Modify Extraction ---\033[0m\n7. Change number of colours \n\nEnter choice (1-7) or press enter to continue: ")
            
            if options == '1':
                #* Reverse color order
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')
                colors = colors[::-1]
                print("\033[92m\nColor order reversed.\033[0m")  # Green
                continue
            
            elif options == '2':
                #* Sort by first alternative method
                if current_sort == "hue":
                    colors = sorted(colors, key=rgb_to_saturation)
                    current_sort = "saturation"
                elif current_sort == "saturation":
                    colors = sorted(colors, key=rgb_to_hue)
                    current_sort = "hue"
                elif current_sort == "brightness":
                    colors = sorted(colors, key=rgb_to_saturation)
                    current_sort = "saturation"
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"\033[92m\nColors sorted by {current_sort}.\033[0m")  # Green
                continue
            
            elif options == '3':
                #* Sort by second alternative method
                if current_sort == "hue":
                    colors = sorted(colors, key=rgb_to_brightness)
                    current_sort = "brightness"
                elif current_sort == "saturation":
                    colors = sorted(colors, key=rgb_to_brightness)
                    current_sort = "brightness"
                elif current_sort == "brightness":
                    colors = sorted(colors, key=rgb_to_hue)
                    current_sort = "hue"
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"\033[92m\nColors sorted by {current_sort}.\033[0m")  # Green
                continue
            
            elif options == '4':
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
            
            elif options == '5':
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
                    pyperclip.copy(", ".join(hex_colors))
                    print("\033[92m\nHex values copied to clipboard.\033[0m")  # Green
                except Exception as e:
                    print(f"\033[91mFailed to copy Hex values to clipboard: {e}\033[0m")  # Red
                continue

            elif options == "6":
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

            elif options == "7":
                #* Change number of colors
                while True:
                    try:
                        num_colors = int(input("\nEnter new number of colors to extract from the image (1-20): "))
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
                # Re-apply current sort method
                if current_sort == "hue":
                    colors = sorted(colors, key=rgb_to_hue)
                elif current_sort == "saturation":
                    colors = sorted(colors, key=rgb_to_saturation)
                elif current_sort == "brightness":
                    colors = sorted(colors, key=rgb_to_brightness)
                print("\033[92m\nNumber of colors updated.\033[0m")  # Green
                continue
            
            elif options == '':
                break
            
            else:
                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, 7 or press enter to skip.")
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