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
            print("\033[91mFile not found. Please enter a valid file path.\033[0m")
        except requests.exceptions.RequestException as e:
            print(f"\033[91mError downloading image: {e}. Please enter a valid URL.\033[0m")
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
            exit(0)
        except Exception as e:
            print(f"\033[91mAn error occurred: {e}. Please try again.\033[0m")

def get_color_count():
    # Prompt user for number of colors to extract
    while True:
        try:
            num_colors = int(input("Enter number of colors to extract (1-20): "))
            if num_colors < 1 or num_colors > 20:
                print("\033[91mPlease enter a number between 1 and 20.\033[0m")
                continue
            return num_colors
        except ValueError:
            print("\033[91mInvalid input. Please enter an integer between 1 and 20.\033[0m")
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
            exit(0)

def handle_color_options(colors, num_colors, pixels):
    # Display colors and handle user options menu.
    # Import dependencies inside function to avoid circular imports
    from color_utils import rgb_to_hex, rgb_to_hue, rgb_to_saturation, rgb_to_brightness, apply_sort
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

    # Store original colors for reversing filter
    original_colors = None
    is_filtered = False

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

            # Dynamically adjust options based on filter state
            if is_filtered:
                option8_text = "8. Remove color filtering"
            else:
                option8_text = "8. Filter dark/bright colours"

            options = input(f"\nOptions: \n\n\033[1m--- Color Manipulation ---\033[0m\n1. Reverse colour order \n{option2_text} \n{option3_text} \n\n\033[1m--- Export/Copy ---\033[0m\n{option4_text} \n{option5_text} \n6. Convert to RGBA JSON format \n\n\033[1m--- Modify Extraction ---\033[0m\n7. Change number of colours \n{option8_text} \n\nEnter choice (1-8) or press enter to continue: ")
            
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
                            print("\033[91mPlease enter a number between 0.0 and 1.0.\033[0m")
                            continue
                        break
                    except ValueError:
                        print("\033[91mInvalid opacity value. Please enter a number between 0.0 and 1.0.\033[0m")
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
                            print("\033[91mPlease enter a number between 1 and 20.\033[0m")
                            continue
                        break
                    except ValueError:
                        print("\033[91mInvalid input. Please enter a number between 1 and 20.\033[0m")
                    except KeyboardInterrupt:
                        print("\nProcess interrupted by user. Exiting.")
                        exit(0)
                clear_screen()
                # Regenerate colors with new number
                colors = get_clusters(pixels, num_colors)
                # Re-apply current sort method
                colors = apply_sort(colors, current_sort)
                print("\033[92m\nNumber of colors updated.\033[0m")
                continue

            elif options == "8":
                # Filter dark/bright colors
                # Remove filtering if already applied
                if is_filtered:
                    clear_screen()
                    colors = original_colors
                    is_filtered = False
                    print("\033[92m\nColor filtering removed. Original colors restored.\033[0m") # green
                    continue
                else:
                    # Store original colors before filtering
                    original_colors = colors

                    from image_utils import filter_extreme_pixels

                    while True:
                        try:
                            filter_choice = input("\nFilter options: \n1. Filter dark colors \n2. Filter bright colors \n3. Filter both dark and bright colors \n\nEnter choice (1-3): ")
                            if filter_choice not in ['1', '2', '3']:
                                print("\033[91mPlease enter 1, 2, or 3.\033[0m")
                                continue

                            # Get min and max brightness thresholds and validate user input - defaults 0.15 and 0.85 respectively
                            min_brightness = 0.15 # Default min brightness
                            max_brightness = 0.85 # Default max brightness

                            while True:
                                try:
                                    if filter_choice == '1':
                                        min_brightness = float(input("Enter minimum brightness for dark color filtering (0.0 to 1.0, default 0.15): ") or "0.15" )
                                    elif filter_choice == '2':
                                        max_brightness = float(input("Enter maximum brightness for bright color filtering (0.0 to 1.0, default 0.85): ") or "0.85")
                                    elif filter_choice == '3':
                                        min_brightness = float(input("Enter minimum brightness for dark color filtering (0.0 to 1.0, default 0.15): ") or "0.15")
                                        max_brightness = float(input("Enter maximum brightness for bright color filtering (0.0 to 1.0, default 0.85): ") or "0.85")
                                except ValueError:
                                    print("\033[91mInvalid input. Please enter a number between 0.0 and 1.0.\033[0m")
                                    continue
                                except KeyboardInterrupt:
                                    print("\nProcess interrupted by user. Exiting.")
                                    exit(0)
                                # Validate brightness values are between 0.0 and 1.0 and min < max
                                if not (0.0 <= min_brightness <= 1.0) or not (0.0 <= max_brightness <= 1.0):
                                    print("\033[91mBrightness values must be between 0.0 and 1.0.\033[0m") # red
                                    continue
                                if min_brightness >= max_brightness:
                                    print("\033[91mMinimum brightness must be less than maximum brightness.\033[0m") # red
                                    continue
                                break

                            break
                        except KeyboardInterrupt:
                            print("\nProcess interrupted by user. Exiting.")
                            exit(0)
                        
                    clear_screen()
                    if filter_choice == '1':
                        filtered_pixels = filter_extreme_pixels(pixels, filter_dark=True, filter_light=False, min_brightness=min_brightness, max_brightness=max_brightness)
                    elif filter_choice == '2':
                        filtered_pixels = filter_extreme_pixels(pixels, filter_dark=False, filter_light=True, min_brightness=min_brightness, max_brightness=max_brightness)
                    elif filter_choice == '3':
                        filtered_pixels = filter_extreme_pixels(pixels, filter_dark=True, filter_light=True, min_brightness=min_brightness, max_brightness=max_brightness)
                    colors = get_clusters(filtered_pixels, num_colors)
                    # Re-apply current sort method
                    colors = apply_sort(colors, current_sort)
                    is_filtered = True
                    print("\033[92m\nColors filtered and updated.\033[0m")
                    continue
            
            elif options == '':
                # User pressed enter - exit options menu
                return
            
            else:
                clear_screen()
                print("\033[91mInvalid choice. Please enter 1, 2, 3, 4, 5, 6, 7, 8 or press enter to skip.\033[0m")
                
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