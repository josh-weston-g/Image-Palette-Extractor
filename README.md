# Image-Palette-Extractor

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg?logo=python&logoColor=ffffff)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A modular command-line tool that extracts dominant color palettes from images using K-means clustering. Perfect for designers, developers, or anyone who needs to pull colors from images quickly.

## What it does

This tool analyzes any image (local file or URL) and extracts its most dominant colors using K-means clustering with the option to filter out extremely dark/bright colors. The colors can be sorted by hue (rainbow order), saturation, or brightness, making it easy to create harmonious color schemes that suit your needs. You can export colors in multiple formats: RGB, Hex, or RGBA with custom opacity.

## Demo

### Original Image
![Test Image](Test_Images/test_image.jpg)

### Extracted Palette
![Image Palette Extractor Demo](screenshot.png)

*Extracting 7 dominant colors from the test image above*

## Project Structure

The codebase is organized into focused, reusable modules:

```
Image-Palette-Extractor/
├── main.py           # Entry point - orchestrates the application flow
├── cli.py            # Command-line interface and user interaction
├── color_utils.py    # Color conversion functions (RGB to Hue/Saturation/Brightness/Hex)
├── image_utils.py    # Image processing and K-means clustering
├── requirements.txt  # Python dependencies
└── Test_Images/      # Sample images for testing
```

This modular structure makes the code easy to maintain, test, and extend with new features.

## Features

- 🎨 **Extract 1-20 dominant colors** from any image
- 🌈 **Flexible color sorting** - sort by hue (rainbow order), saturation, or brightness
- 🎯 **Smart color filtering** - exclude very dark or very light colors from extraction
- 📋 **Multiple export formats**:
  - RGB values: `(224, 153, 195), (158, 79, 116), ...`
  - Hex codes: `#E099C3, #9E4F74, ...`
  - RGBA JSON: `["rgba(224, 153, 195, 0.15)", ...]`
- 📎 **Copy to clipboard** with one click (RGB or Hex)
- 🔄 **Reverse color order** if you need the palette backwards
- 🖼️ **Image preview in terminal** (if climage is installed)
- 🌐 **Supports URLs and local files**
- ⚡ **Fast processing** - images are automatically resized for speed

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/josh-weston-g/Image-Palette-Extractor.git
   cd Image-Palette-Extractor
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the program:
```bash
python main.py
```

**Tip:** The repository includes sample images in the `Test_Images/` directory that you can use to test the tool.

The tool will guide you through:
1. Enter an image path or URL
2. Choose how many colors to extract (1-20)
3. View your color palette (sorted by hue by default)
4. Choose what to do:
   - Reverse the color order
   - Sort by hue, saturation, or brightness
   - Filter dark/bright colors (exclude very dark or very light colors)
   - Copy RGB values to clipboard
   - Copy Hex values to clipboard
   - Convert to RGBA JSON format (with custom opacity)
   - Change the number of colors

## Examples

### Basic usage
```bash
python main.py
```
```
Enter path to image file or URL: https://example.com/wallpaper.jpg
Enter number of colors to reduce the image to (1-20): 5
```

### Local file
```bash
python main.py
```
```
Enter path to image file or URL: /path/to/your/image.png
Enter number of colors to reduce the image to (1-20): 7
```

### Output formats

**RGB format:**
```
(224, 153, 195), (158, 79, 116), (96, 33, 55), (53, 12, 25), (151, 27, 48)
```

**Hex format:**
```
#E099C3, #9E4F74, #602137, #350C19, #971B30
```

**RGBA JSON format:**
```json
[
  "rgba(224, 153, 195, 0.15)",
  "rgba(158, 79, 116, 0.15)",
  "rgba(96, 33, 55, 0.15)",
  "rgba(53, 12, 25, 0.15)",
  "rgba(151, 27, 48, 0.15)"
]
```

## Requirements

- Python 3.8+
- PIL (Pillow)
- NumPy
- scikit-learn
- requests
- pyperclip (optional - for clipboard functionality)
- climage (optional - for terminal image preview)

## Troubleshooting

### Clipboard not working
If you get an error when trying to copy colors to clipboard:
- **Linux:** Install `xclip` or `xsel`
  ```bash
  sudo apt-get install xclip
  ```
- **macOS:** Clipboard should work by default
- **Windows:** Clipboard should work by default

### Image preview not showing
The terminal image preview is optional and requires the `climage` package:
```bash
pip install climage
```
If you don't have it installed, the tool will still work - you just won't see the image preview.

### "Failed to load image" error
- Check that the file path is correct and the file exists
- For URLs, make sure you have an active internet connection
- Ensure the file is a valid image format (JPG, PNG, etc.)

### Module not found errors
Make sure you've activated your virtual environment and installed all dependencies:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! If you'd like to contribute:

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a Pull Request

Please ensure your code follows the existing style and test it with the sample images before submitting.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Josh Weston - [@josh-weston-g](https://github.com/josh-weston-g)
