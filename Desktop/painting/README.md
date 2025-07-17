# Gallery-Quality Painting Animation Studio

This project creates stunning, gallery-quality 3D animations from static images using advanced depth estimation and artistic effects. Inspired by digital art exhibitions like **NEW BORN** by Hakan & Süleyman Yılmaz at [Acıbadem Art Gallery](https://www.acibadem.com.tr/sanat/).

## ✨ Features

- **5 Artistic Styles**: Ethereal, Cyberpunk, Impressionist, Abstract, and Dreamlike
- **Gallery-Quality Output**: Professional video encoding with customizable quality
- **Advanced Depth Mapping**: Uses MiDaS AI for precise depth analysis
- **Organic Animations**: Breathing, flowing effects that bring paintings to life
- **Interactive Style Selector**: Easy-to-use interface for choosing effects
- **Multiple Export Options**: From quick previews to exhibition-quality pieces

## 🎨 Artistic Styles

### 1. Ethereal (Inspired by NEW BORN)
- Soft, light-based effects with organic breathing movements
- Warm color temperature with ethereal glow effects
- Perfect for portraits and serene landscapes

### 2. Cyberpunk
- Futuristic neon effects with geometric distortions
- Enhanced blues and reds for sci-fi aesthetics
- Sharp, angular movements

### 3. Impressionist
- Painterly brush-stroke effects
- Soft color enhancements
- Direction-based depth movements

### 4. Abstract
- Kaleidoscope-like geometric transformations
- Radial distortions from center point
- Perfect for creating surreal effects

### 5. Dreamlike
- Liquid, wave-like flowing effects
- Multiple wave interference patterns
- Soft color enhancements for dream-like quality

## 🚀 Quick Start

### Basic Usage
```bash
# Activate virtual environment
source venv/bin/activate

# Run basic animation
python animate_painting.py

# Run premium version with ethereal style
python animate_painting_premium.py
```

### Interactive Style Selector
```bash
# Launch the interactive studio
python style_selector.py
```

The style selector allows you to:
- Choose from 5 artistic styles
- Select duration (3-8 seconds)
- Pick quality level (Draft to Exhibition)
- Generate custom animations

## 🛠️ Installation

1. **Clone and setup**:
```bash
git clone <your-repo>
cd painting
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Add your image**:
   - Place your image as `IMG_7615.jpg` or modify the `IMAGE_PATH` in the scripts

3. **Run**:
```bash
python style_selector.py
```

## 📁 Project Structure

```
painting/
├── animate_painting.py          # Enhanced basic version
├── animate_painting_premium.py  # Premium version with all styles
├── style_selector.py           # Interactive style selection
├── requirements.txt            # Dependencies
├── IMG_7615.jpg               # Your input image
├── README.md                  # This file
└── venv/                      # Virtual environment
```

## 🎯 Output Quality Options

- **Draft**: Fast export, good for testing (4000k bitrate)
- **Good**: Balanced quality and speed (8000k bitrate)
- **Premium**: Gallery-ready quality (12000k bitrate)
- **Exhibition**: Maximum detail for professional display (16000k bitrate)

## 🎬 Animation Durations

- **Quick Preview**: 3 seconds (90 frames)
- **Standard**: 5 seconds (150 frames)
- **Gallery Quality**: 6 seconds (180 frames)
- **Exhibition Piece**: 8 seconds (240 frames)

## ⚙️ Configuration

### Custom Image
```python
IMAGE_PATH = "your_image.jpg"  # Change in any script
```

### Style Customization
You can modify parameters in the `ArtisticStyleProcessor` class:
- Wave frequencies and amplitudes
- Color enhancement factors
- Displacement strengths
- Time-based effect intensities

## 🎨 Artistic Inspiration

This project draws inspiration from contemporary digital art exhibitions, particularly the ethereal and organic qualities found in works like NEW BORN by Hakan & Süleyman Yılmaz. The animations aim to capture the same sense of life and movement that makes gallery pieces so captivating.

## 🔧 Requirements

- Python 3.8+
- CUDA-compatible GPU (recommended)
- 4GB+ RAM for processing
- ~2GB storage for models and outputs

## 📊 Performance Tips

- **GPU**: Significantly faster depth estimation
- **Image Size**: Resize large images for faster processing
- **Quality vs Speed**: Use Draft quality for testing, Premium/Exhibition for final output
- **Memory**: Reduce frame count if you encounter memory issues

## 🎭 Gallery Examples

The project creates videos suitable for:
- Digital art galleries
- Social media art accounts
- Personal art collections
- Commercial art displays
- Interactive exhibitions

## 🤝 Contributing

Feel free to contribute new artistic styles, effects, or optimizations. The modular design makes it easy to add new styles to the `ArtisticStyleProcessor` class.

## 📄 License

This project is inspired by and created for artistic purposes. Please credit when sharing or exhibiting the created works.

---

*"Every painting has a soul waiting to breathe. This studio helps it come alive."* 