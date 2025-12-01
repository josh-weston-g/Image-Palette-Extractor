import os
from PIL import Image
import requests
from io import BytesIO

def clear_screen():
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

def get_image_from_user():
    # Prompt user for image path or URL
    while True:
        try:
            image_path = input("\nEnter image file path or URL: ")
            # Check if input is a URL
            if image_path.startswith(("https://", "http://")):
                print("\nDownloading image from URL...")
                response = requests.get(image_path)
                response.raise_for_status() # Raise error for bad responses
                im = Image.open(BytesIO(response.content))
            else:
                im = Image.open(image_path)
            return im
        except FileNotFoundError:
            print("File not found. Please enter a valid file path.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}. Please enter a valid URL.")
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
            exit(0)
        except Exception as e:
            print(f"An error occurred: {e}. Please try again.")

def get_color_count():
    # Prompt user for number of colors to extract
    while True:
        try:
            num_colors = int(input("Enter number of colors to extract (1-20): "))
            if num_colors < 1 or num_colors > 20:
                print("Please enter a number between 1 and 20.")
                continue
            return num_colors
        except ValueError:
            print("Invalid input. Please enter an integer between 1 and 20.")
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
            exit(0)

def handle_color_options(colors, num_colors, pixels):
    # Display colors and handle user options menu.
    # Import dependencies inside function to avoid circular imports
    from color_utils import rgb_to_hex, rgb_to_hue, rgb_to_saturation, rgb_to_brightness
    from image_utils import get_clusters
    import json
    
    # Check for pyperclip availability
    try:
        import pyperclip
        PYPERCLIP_AVAILABLE = True
    except ImportError:
        PYPERCLIP_AVAILABLE = False

    # Initial sort of colors by hue
    current_sort = "hue"
    colors = sorted(colors, key=rgb_to_hue)

    # Clear the screen before displaying options
    clear_screen()
    
    while True:
        print(f"\nExtracted {num_colors} colors (sorted by {current_sort}):")
        hex_colors = rgb_to_hex(colors)
        for i, color in enumerate(colors):
            r, g, b = color
            h = rgb_to_hue(color)
            s = rgb_to_saturation(color)
            v = rgb_to_brightness(color)
            print(f"\033[48;2;{r};{g};{b}m    \033[0m RGB({r}, {g}, {b}) | Hex: {hex_colors[i]}")
        
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
            option4_text = "4. Copy RGB values to clipboard" if PYPERCLIP_AVAILABLE else "4. Copy RGB values to clipboard \033[91m(not active)\033[0m"
            option5_text = "5. Copy Hex values to clipboard" if PYPERCLIP_AVAILABLE else "5. Copy Hex values to clipboard \033[91m(not active)\033[0m"

            options = input(f"\nOptions: \n\n\033[1m--- Color Manipulation ---\033[0m\n1. Reverse colour order \n{option2_text} \n{option3_text} \n\n\033[1m--- Export/Copy ---\033[0m\n{option4_text} \n{option5_text} \n6. Convert to RGBA JSON format \n\n\033[1m--- Modify Extraction ---\033[0m\n7. Change number of colours \n\nEnter choice (1-7) or press enter to continue: ")
            
            if options == '1':
                # Reverse color order
                clear_screen()
                colors = colors[::-1]
                print("\033[92m\nColor order reversed.\033[0m")
                continue
            
            elif options == '2':
                # Sort by first alternative method
                if current_sort == "hue":
                    colors = sorted(colors, key=rgb_to_saturation)
                    current_sort = "saturation"
                elif current_sort == "saturation":
                    colors = sorted(colors, key=rgb_to_hue)
                    current_sort = "hue"
                elif current_sort == "brightness":
                    colors = sorted(colors, key=rgb_to_saturation)
                    current_sort = "saturation"
                clear_screen()
                print(f"\033[92m\nColors sorted by {current_sort}.\033[0m")
                continue
            
            elif options == '3':
                # Sort by second alternative method
                if current_sort == "hue":
                    colors = sorted(colors, key=rgb_to_brightness)
                    current_sort = "brightness"
                elif current_sort == "saturation":
                    colors = sorted(colors, key=rgb_to_brightness)
                    current_sort = "brightness"
                elif current_sort == "brightness":
                    colors = sorted(colors, key=rgb_to_hue)
                    current_sort = "hue"
                clear_screen()
                print(f"\033[92m\nColors sorted by {current_sort}.\033[0m")
                continue
            
            elif options == '4':
                # Copy RGB values to clipboard
                if not PYPERCLIP_AVAILABLE:
                    clear_screen()
                    print("\033[91mpyperclip module not available. Install pyperclip with: pip install pyperclip\033[0m")
                    continue
                clear_screen()
                try:
                    colors_list = [f"({color[0]}, {color[1]}, {color[2]})" for color in colors]
                    pyperclip.copy(", ".join(colors_list))
                    print("\033[92m\nRGB values copied to clipboard.\033[0m")
                except Exception as e:
                    print(f"\033[91mFailed to copy RGB values to clipboard: {e}\033[0m")
                continue
            
            elif options == '5':
                # Copy Hex values to clipboard
                if not PYPERCLIP_AVAILABLE:
                    clear_screen()
                    print("\033[91mpyperclip module not available. Install pyperclip with: pip install pyperclip\033[0m")
                    continue
                clear_screen()
                try:
                    pyperclip.copy(", ".join(hex_colors))
                    print("\033[92m\nHex values copied to clipboard.\033[0m")
                except Exception as e:
                    print(f"\033[91mFailed to copy Hex values to clipboard: {e}\033[0m")
                continue

            elif options == "6":
                # Convert to RGBA JSON format
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
                clear_screen()
                colors_list = [f"rgba({color[0]}, {color[1]}, {color[2]}, {opacity})" for color in colors]
                print("\n\033[96mExtracted colors (RGBA):")
                print(json.dumps(colors_list, indent=2))
                print("\033[0m")
                continue

            elif options == "7":
                # Change number of colors
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
                clear_screen()
                # Regenerate colors with new number
                colors = get_clusters(pixels, num_colors)
                # Re-apply current sort method
                if current_sort == "hue":
                    colors = sorted(colors, key=rgb_to_hue)
                elif current_sort == "saturation":
                    colors = sorted(colors, key=rgb_to_saturation)
                elif current_sort == "brightness":
                    colors = sorted(colors, key=rgb_to_brightness)
                print("\033[92m\nNumber of colors updated.\033[0m")
                continue
            
            elif options == '':
                # User pressed enter - exit options menu
                return
            
            else:
                clear_screen()
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, 7 or press enter to skip.")
                
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
            exit(0)

def ask_continue():
    # Ask user if they want to process another image
    try:
        continue_choice = input("\nProcess another image? (y/n): ").lower()
        if continue_choice != 'y':
            return False
        return True
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")
        exit(0)