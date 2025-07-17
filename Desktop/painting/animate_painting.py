import cv2
import torch
import numpy as np
from PIL import Image
from torchvision.transforms import Compose, ToTensor, Normalize
from moviepy.editor import ImageSequenceClip
import os
import sys

def main():
    # ---- CONFIGURATION ----
    IMAGE_PATH = "IMG_7615.jpg"  # Replace with your image path
    OUTPUT_VIDEO = "painting_3d_effect.mp4"
    
    # Check if image file exists
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image file '{IMAGE_PATH}' not found!")
        sys.exit(1)
    
    print(f"Loading image: {IMAGE_PATH}")
    
    try:
        # ---- LOAD MiDaS DEPTH MODEL ----
        print("Loading MiDaS depth estimation model...")
        # Use the smaller MiDaS model for faster download and processing
        midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
        midas.eval()
        transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
        print("✓ Model loaded successfully")
        
        # Load and preprocess image
        print("Processing image...")
        img = Image.open(IMAGE_PATH).convert("RGB")
        # Convert PIL image to numpy array for the transform
        img_np_input = np.array(img)
        img_input = transform(img_np_input)
        
        # Depth estimation
        print("Estimating depth...")
        with torch.no_grad():
            depth = midas(img_input).squeeze().cpu().numpy()
        
        # Convert original image to numpy
        img_np = np.array(img)
        h, w, _ = img_np.shape
        
        # Resize depth map to match original image dimensions
        depth_resized = cv2.resize(depth, (w, h))
        
        # Normalize depth to [0,1]
        depth_norm = cv2.normalize(depth_resized, None, 0, 1, cv2.NORM_MINMAX)
        
        # ---- CREATE FRAMES WITH PARALLAX ----
        print("Generating frames with parallax effect...")
        frames = []
        num_frames = 120  # ~5 sec at 24 fps
        
        for i in range(num_frames):
            if i % 10 == 0:  # Progress indicator
                print(f"Processing frame {i+1}/{num_frames}")
                
            shift = int((i / num_frames) * 40)  # max shift
            parallax = img_np.copy()
            
            # Apply depth-based displacement
            for y in range(h):
                offset = int(depth_norm[y, 0] * shift)
                parallax[y] = np.roll(parallax[y], offset, axis=0)
            
            frames.append(Image.fromarray(parallax))
        
        print("✓ All frames generated")
        
        # ---- EXPORT VIDEO ----
        print(f"Exporting video to {OUTPUT_VIDEO}...")
        clip = ImageSequenceClip([np.array(f) for f in frames], fps=24)
        clip.write_videofile(OUTPUT_VIDEO, codec="libx264", audio=False)
        print(f"✓ Video exported successfully: {OUTPUT_VIDEO}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()