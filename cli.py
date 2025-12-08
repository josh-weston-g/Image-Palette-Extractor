import os
from PIL import Image
import requests
from io import BytesIO

def clear_screen():
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

def load_image():
    """
    Prompt user for image path/URL and load the image.
    Handles validation and retries on error.

    :return: PIL Image object.
    """
    while True:
        try:
            image_source = input("\nEnter image file path or URL: ")
            
            # Check if image is a URL
            if image_source.startswith(("http://", "https://", "ftp://")):
                print("\nDownloading image from URL...")
                response = requests.get(image_source)
                response.raise_for_status() # Raise error for bad responses
                return Image.open(BytesIO(response.content))
            else:
                # Load image from local file path
                return Image.open(image_source)
                
        except FileNotFoundError:
            print(f"\033[91mImage file not found: {image_source}\033[0m")
        except requests.exceptions.RequestException as e:
            print(f"\033[91mError downloading image: {e}\033[0m")
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
            exit(0)
        except Exception as e:
            print(f"\033[91mError loading image: {e}\033[0m")

def get_color_count():
    # Prompt user for number of colors to extract
    while True:
        try:
            num_colors = int(input("\nEnter number of colors to extract (1-20): "))
            if num_colors < 1 or num_colors > 20:
                print("\033[91mPlease enter a number between 1 and 20.\033[0m")
                continue
            return num_colors
        except ValueError:
            print("\033[91mInvalid input. Please enter an integer between 1 and 20.\033[0m")
        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
            exit(0)

def handle_color_options(palette):
    # Display colors and handle user options menu using ImagePalette object
    # Import dependencies inside function to avoid circular imports
    import json
    
    # Check for pyperclip availability
    try:
        import pyperclip
        PYPERCLIP_AVAILABLE = True
    except ImportError:
        PYPERCLIP_AVAILABLE = False

    # Clear the screen before displaying options
    clear_screen()
    
    while True:
        print(f"\nExtracted {palette.num_colors} colors (sorted by {palette.current_sort}):")
        hex_colors = palette.get_hex_list()
        for i, color in enumerate(palette.colors):
            r, g, b = color
            print(f"\033[48;2;{r};{g};{b}m    \033[0m RGB({r}, {g}, {b}) | Hex: {hex_colors[i]}")
        
        try:
            # Dynamically adjust options based on current sort method
            if palette.current_sort == "hue":
                option2_text = "2. Sort by saturation"
                option3_text = "3. Sort by brightness"
            elif palette.current_sort == "saturation":
                option2_text = "2. Sort by hue"
                option3_text = "3. Sort by brightness"
            elif palette.current_sort == "brightness":
                option2_text = "2. Sort by saturation"
                option3_text = "3. Sort by hue"

            # Dynamically adjust options based on complementary state
            option4_text = "4. Restore original colors" if palette.is_complementary else "4. Convert to complementary colors"

            # Dynamically adjust options based on pyperclip availability
            option5_text = "5. Copy RGB values to clipboard" if PYPERCLIP_AVAILABLE else "5. Copy RGB values to clipboard \033[91m(not active)\033[0m"
            option6_text = "6. Copy Hex values to clipboard" if PYPERCLIP_AVAILABLE else "6. Copy Hex values to clipboard \033[91m(not active)\033[0m"

            # Dynamically adjust options based on filter state
            option9_text = "9. Remove color filtering" if palette.is_filtered else "9. Filter dark/bright colours"

            options = input(f"\nOptions: \n\n\033[1m--- Color Manipulation ---\033[0m\n1. Reverse colour order \n{option2_text} \n{option3_text} \n{option4_text} \n\n\033[1m--- Export/Copy ---\033[0m\n{option5_text} \n{option6_text} \n7. Convert to RGBA JSON format \n\n\033[1m--- Modify Extraction ---\033[0m\n8. Change number of colours \n{option9_text} \n\nEnter choice (1-9) or press enter to continue: ")
            
            if options == '1':
                # Reverse color order
                clear_screen()
                palette.reverse()
                print("\033[92m\nColor order reversed.\033[0m")
                continue
            
            elif options == '2':
                # Sort by first alternative method
                if palette.current_sort == "hue":
                    palette.sort_by("saturation")
                elif palette.current_sort == "saturation":
                    palette.sort_by("hue")
                elif palette.current_sort == "brightness":
                    palette.sort_by("saturation")
                clear_screen()
                print(f"\033[92m\nColors sorted by {palette.current_sort}.\033[0m")
                continue
            
            elif options == '3':
                # Sort by second alternative method
                if palette.current_sort == "hue":
                    palette.sort_by("brightness")
                elif palette.current_sort == "saturation":
                    palette.sort_by("brightness")
                elif palette.current_sort == "brightness":
                    palette.sort_by("hue")
                clear_screen()
                print(f"\033[92m\nColors sorted by {palette.current_sort}.\033[0m")
                continue
            
            elif options == '4':
                # Toggle complementary colors
                clear_screen()
                if palette.is_complementary:
                    palette.remove_complementary()
                    print("\033[92m\nRestored original colors.\033[0m")
                else:
                    palette.to_complementary()
                    print("\033[92m\nConverted to complementary colors.\033[0m")
                continue
            
            elif options == '5':
                # Copy RGB values to clipboard
                if not PYPERCLIP_AVAILABLE:
                    clear_screen()
                    print("\033[91mpyperclip module not available. Install pyperclip with: pip install pyperclip\033[0m")
                    continue
                clear_screen()
                try:
                    colors_list = [f"({r}, {g}, {b})" for r, g, b in palette.get_rgb_list()]
                    pyperclip.copy(", ".join(colors_list))
                    print("\033[92m\nRGB values copied to clipboard.\033[0m")
                except Exception as e:
                    print(f"\033[91mFailed to copy RGB values to clipboard: {e}\033[0m")
                continue
            
            elif options == '6':
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

            elif options == "7":
                # Convert to RGBA JSON format
                while True:
                    try:
                        opacity = input("\nEnter opacity value (0.0 to 1.0, default 0.15) or 'c' to cancel: ") or 0.15
                        # Check for cancel
                        if opacity == "c":
                            break
                        opacity = float(opacity)
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
                if opacity == "c":
                    continue
                colors_list = palette.get_rgba_list(opacity)
                print("\n\033[96mExtracted colors (RGBA):")
                print(json.dumps(colors_list, indent=2))
                print("\033[0m")
                continue

            elif options == "8":
                # Change number of colors
                while True:
                    try:
                        num_colors = input("\nEnter new number of colors to extract from the image (1-20) or 'c' to cancel: ")
                        # Check for cancel
                        if num_colors == "c":
                            break
                        num_colors = int(num_colors)
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
                if num_colors == "c":
                    continue
                # Regenerate colors with new number
                palette.extract_palette(num_colors)
                print("\033[92m\nNumber of colors updated.\033[0m")
                continue

            elif options == "9":
                # Filter dark/bright colors
                # Remove filtering if already applied
                if palette.is_filtered:
                    clear_screen()
                    palette.remove_filter()
                    print("\033[92m\nColor filtering removed. Original colors restored.\033[0m")
                    continue
                else:
                    # Get filter choice
                    filter_choice = None  # Initialize to track if user cancelled
                    while True:
                        try:
                            filter_choice = input("\nFilter options: \n1. Filter dark colors \n2. Filter bright colors \n3. Filter both dark and bright colors \n\nEnter choice (1-3) or 'c' to cancel: ")
                            if filter_choice == 'c':
                                break #exit this loop
                            elif filter_choice not in ['1', '2', '3']:
                                print("\033[91mPlease enter 1, 2, or 3.\033[0m")
                                continue
                            break
                        except KeyboardInterrupt:
                            print("\nProcess interrupted by user. Exiting.")
                            exit(0)
        
                    # If user cancelled, skip to next iteration of main options loop
                    if filter_choice == 'c':
                        clear_screen()
                        continue
                        
                    # Get min and max brightness thresholds
                    min_brightness = 0.15
                    max_brightness = 0.85
                    filter_dark = False
                    filter_light = False
                    
                    brightness_cancelled = False  # Flag to track cancellation
                    while True:
                        try:
                            if filter_choice == '1':
                                brightness_input = input("Enter minimum brightness for dark color filtering (0.0 to 1.0, default 0.15) or 'c' to cancel: ") or "0.15"
                                if brightness_input == 'c':
                                    brightness_cancelled = True
                                    break
                                min_brightness = float(brightness_input)
                                filter_dark = True
                            elif filter_choice == '2':
                                brightness_input = input("Enter maximum brightness for light color filtering (0.0 to 1.0, default 0.85) or 'c' to cancel: ") or "0.85"
                                if brightness_input == 'c':
                                    brightness_cancelled = True
                                    break
                                max_brightness = float(brightness_input)
                                filter_light = True
                            elif filter_choice == '3':
                                min_input = input("Enter minimum brightness for dark color filtering (0.0 to 1.0, default 0.15) or 'c' to cancel: ") or "0.15"
                                if min_input == 'c':

                                    brightness_cancelled = True
                                    break
                                min_brightness = float(min_input)
                                
                                max_input = input("Enter maximum brightness for light color filtering (0.0 to 1.0, default 0.85) or 'c' to cancel: ") or "0.85"
                                if max_input == 'c':
                                    brightness_cancelled = True
                                    break
                                max_brightness = float(max_input)
                                filter_dark = True
                                filter_light = True
                        except ValueError:
                            print("\033[91mInvalid input. Please enter a number between 0.0 and 1.0.\033[0m")
                            continue
                        except KeyboardInterrupt:
                            print("\nProcess interrupted by user. Exiting.")
                            exit(0)
                        
                        # Validate brightness values
                        if not (0.0 <= min_brightness <= 1.0) or not (0.0 <= max_brightness <= 1.0):
                            print("\033[91mBrightness values must be between 0.0 and 1.0.\033[0m")
                            continue
                        if min_brightness >= max_brightness:
                            print("\033[91mMinimum brightness must be less than maximum brightness.\033[0m")
                            continue
                        break
                    
                    # If user cancelled brightness input, skip filtering
                    if brightness_cancelled:
                        clear_screen()
                        continue
                    
                    # Filter colors using palette method
                    clear_screen()
                    palette.filter_colors(filter_dark=filter_dark, filter_light=filter_light, min_brightness=min_brightness, max_brightness=max_brightness)
                    print("\033[92m\nColors filtered and updated.\033[0m")
                    continue
            
            elif options == '':
                # User pressed enter - exit options menu
                return
            
            else:
                clear_screen()
                print("\033[91mInvalid choice. Please enter 1, 2, 3, 4, 5, 6, 7, 8, 9 or press enter to skip.\033[0m")
                
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