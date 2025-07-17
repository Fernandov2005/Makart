# Painting 3D Animation

This project creates a 3D parallax effect from a static image using depth estimation. It analyzes the depth in an image and generates frames with a parallax effect to create a video with a 3D-like appearance.

## Features

- Uses MiDaS depth estimation model for accurate depth mapping
- Creates smooth parallax animation effects
- Exports high-quality MP4 video
- Progress indicators and error handling

## Requirements

- Python 3.8+
- CUDA-compatible GPU (recommended for faster processing)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the image file `IMG_7615.jpg` in the project directory

## Usage

Run the script:
```bash
python animate_painting.py
```

The script will:
1. Load the MiDaS depth estimation model (this may take a few minutes on first run)
2. Process your image to estimate depth
3. Generate 120 frames with parallax effects
4. Export the final video as `painting_3d_effect.mp4`

## Configuration

You can modify the following parameters in `animate_painting.py`:

- `IMAGE_PATH`: Path to your input image
- `OUTPUT_VIDEO`: Name of the output video file
- `num_frames`: Number of frames to generate (affects video length)
- `shift`: Maximum parallax shift amount

## Output

The script generates a 5-second video (24 fps) with a 3D parallax effect based on the depth information in your image.

## Troubleshooting

- If you get memory errors, try reducing the `num_frames` value
- Make sure your image file exists and is readable
- For better performance, use a CUDA-compatible GPU
- If the model download fails, check your internet connection 