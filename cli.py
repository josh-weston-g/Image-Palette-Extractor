import os
from PIL import Image
import requests
from io import BytesIO
import questionary
from questionary import Style

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

    # Sort rotation mappings
    SORT_NEXT = {
        "hue": {"option2": "saturation", "option3": "brightness"},
        "saturation": {"option2": "hue", "option3": "brightness"},
        "brightness": {"option2": "saturation", "option3": "hue"}
    }

    # Clear the screen before displaying options
    clear_screen()
    
    # Custom style for questionary
    custom_style = Style([
        ('separator', 'bold fg:ansibrightmagenta'),
        ('pointer', 'fg:ansibrightcyan bold'),
        ('highlighted', 'fg:ansibrightcyan bold'),
        ('selected', 'fg:ansigreen'),
        ('disabled', 'fg:ansired'),  # Add this for disabled items
    ])

    while True:
        print(f"\nExtracted {palette.num_colors} colors (sorted by {palette.current_sort}):")
        hex_colors = palette.get_hex_list()
        for i, color in enumerate(palette.colors):
            r, g, b = color
            print(f"\033[48;2;{r};{g};{b}m    \033[0m RGB({r}, {g}, {b}) | Hex: {hex_colors[i]}")
        
        # Options menu choices - some dynamically change based on state
        CHOICES = [
            questionary.Separator("\n--- Color Manipulation ---"),
            questionary.Choice("Reverse colour order", value="reverse"),
            questionary.Choice(f"Sort by {SORT_NEXT[palette.current_sort]['option2']}", value="sort2"),
            questionary.Choice(f"Sort by {SORT_NEXT[palette.current_sort]['option3']}", value="sort3"),
            questionary.Choice("Restore original colors" if palette.is_complementary else "Convert to complementary colors", value="complementary"),
            questionary.Separator("\n--- Export/Copy ---"),
            questionary.Choice("Copy Hex values to clipboard", value="copy_hex") if PYPERCLIP_AVAILABLE else questionary.Choice("Copy Hex values to clipboard", value="copy_hex", disabled="Pyperclip not installed"),
            questionary.Choice("Copy RGB values to clipboard", value="copy_rgb") if PYPERCLIP_AVAILABLE else questionary.Choice("Copy RGB values to clipboard", value="copy_rgb", disabled="Pyperclip not installed"),
            questionary.Choice("Convert to RGBA JSON format", value="rgba_json"),
            questionary.Separator("\n--- Modify Extraction ---"),
            questionary.Choice("Change number of colours", value="change_num"),
            questionary.Choice("Remove color filtering" if palette.is_filtered else "Filter dark/bright colours", value="filter_colors"),
            questionary.Separator("    "),
            questionary.Choice("Continue", value="continue")
        ]

        # Print empty line for spacing
        print()
        options = questionary.select(
            "Select an option:",
            choices=CHOICES,
            style=custom_style,
        ).ask()

        if options == 'reverse':
            # Reverse color order
            clear_screen()
            palette.reverse()
            print("\033[92m\nColor order reversed.\033[0m")
            continue
        
        elif options == 'sort2':
            next_sort = SORT_NEXT[palette.current_sort]['option2']
            palette.sort_by(next_sort)
            clear_screen()
            print(f"\033[92m\nColors sorted by {palette.current_sort}.\033[0m")
            continue
        
        elif options == 'sort3':
            next_sort = SORT_NEXT[palette.current_sort]['option3']
            palette.sort_by(next_sort)
            clear_screen()
            print(f"\033[92m\nColors sorted by {palette.current_sort}.\033[0m")
            continue
        
        elif options == 'complementary':
            # Toggle complementary colors
            clear_screen()
            if palette.is_complementary:
                palette.remove_complementary()
                print("\033[92m\nRestored original colors.\033[0m")
            else:
                palette.to_complementary()
                print("\033[92m\nConverted to complementary colors.\033[0m")
            continue
        
        elif options == 'copy_rgb':
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
        
        elif options == 'copy_hex':
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

        elif options == "rgba_json":
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

        elif options == "change_num":
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

        elif options == "filter_colors":
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
        
        elif options == 'continue':
            # User pressed enter - exit options menu
            return
            
        # Handle keyboard interrupt - questionary handles it internally and returns None
        elif options is None:
            print("\nExiting the program. Goodbye!")
            exit(0)

def ask_continue():
    # Ask user if they want to process another image
    return questionary.confirm("Do you want to process another image?").ask()