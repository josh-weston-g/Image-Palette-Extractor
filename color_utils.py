import colorsys

# Function to convert RGB color to hue value for sorting
def rgb_to_hue(color):
    r, g, b = color
    # Normalize RGB values to 0-1 range (colorsys expects this)
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    # Convert to HSV and extract hue (h is between 0-1)
    h = colorsys.rgb_to_hsv(r, g, b)[0]
    return h

# Function to convert RGB to saturation value for sorting
def rgb_to_saturation(color):
    r, g, b = color
    # Normalize RGB values to 0-1 range (colorsys expects this)
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    # Convert to HSV and extract saturation (s is between 0-1)
    s = colorsys.rgb_to_hsv(r, g, b)[1]
    return s

# Function to convert RGB to brightness value for sorting
def rgb_to_brightness(color):
    r, g, b = color
    # Normalize RGB values to 0-1 range (colorsys expects this)
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    # Convert to HSV and extract value/brightness (v is between 0-1)
    v = colorsys.rgb_to_hsv(r, g, b)[2]
    return v

# Function to convert RGB to Hex
def rgb_to_hex(colors):
    hex_colors = []
    for color in colors:
        r, g, b = color
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        hex_colors.append(hex_color)
    return hex_colors

# Function to apply sort depending on current sort - used to re-apply sort after colours are modified
def apply_sort(colors, current_sort):
    if current_sort == "hue":
        return sorted(colors, key=rgb_to_hue)
    elif current_sort == "saturation":
        return sorted(colors, key=rgb_to_saturation)
    elif current_sort == "brightness":
        return sorted(colors, key=rgb_to_brightness)
    else:
        return colors # if no sort or unrecognized sort, return original order