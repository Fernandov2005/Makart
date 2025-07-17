import cv2
import torch
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from torchvision.transforms import Compose, ToTensor, Normalize
from moviepy.editor import ImageSequenceClip
import os
import sys

def apply_artistic_filter(image, depth_map, frame_index, total_frames):
    """Apply artistic effects based on depth and time"""
    img_array = np.array(image).astype(np.float32)
    h, w, c = img_array.shape
    
    # Create time-based animation parameter
    time_factor = frame_index / total_frames
    wave = np.sin(time_factor * 2 * np.pi)
    
    # Enhanced depth-based displacement with artistic curves
    enhanced_img = img_array.copy()
    
    for y in range(h):
        for x in range(w):
            # Get depth value for this pixel
            depth_val = depth_map[y, x]
            
            # Create flowing, organic displacement
            displacement_x = int(depth_val * 15 * np.sin(time_factor * 4 * np.pi + y * 0.1))
            displacement_y = int(depth_val * 8 * np.cos(time_factor * 3 * np.pi + x * 0.05))
            
            # Apply displacement with bounds checking
            new_x = max(0, min(w-1, x + displacement_x))
            new_y = max(0, min(h-1, y + displacement_y))
            
            enhanced_img[y, x] = img_array[new_y, new_x]
    
    # Color enhancement based on depth
    for y in range(h):
        for x in range(w):
            depth_val = depth_map[y, x]
            
            # Enhance colors based on depth - foreground more vibrant
            if depth_val > 0.7:  # Foreground
                enhanced_img[y, x] *= 1.2  # Increase brightness
                enhanced_img[y, x, 0] *= 1.1  # Slightly more red
            elif depth_val > 0.4:  # Mid-ground
                enhanced_img[y, x, 2] *= 1.15  # Slightly more blue
            else:  # Background
                enhanced_img[y, x] *= 0.85  # Slightly darker
                enhanced_img[y, x, 1] *= 1.1  # Slightly more green
    
    # Clip values to valid range
    enhanced_img = np.clip(enhanced_img, 0, 255).astype(np.uint8)
    
    return Image.fromarray(enhanced_img)

def add_artistic_effects(image, frame_index, total_frames):
    """Add sophisticated artistic effects"""
    # Convert to PIL for easier manipulation
    img = image
    
    # Time-based parameters
    time_factor = frame_index / total_frames
    
    # Subtle saturation breathing effect
    saturation_factor = 1.0 + 0.3 * np.sin(time_factor * 2 * np.pi)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation_factor)
    
    # Subtle contrast enhancement
    contrast_factor = 1.0 + 0.2 * np.sin(time_factor * 1.5 * np.pi)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast_factor)
    
    # Very subtle blur for dreamy effect on certain frames
    if frame_index % 20 < 5:  # Every 20 frames, blur for 5 frames
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    return img

def create_depth_visualization(depth_map, original_image):
    """Create an artistic depth visualization overlay"""
    # Normalize depth for visualization
    depth_colored = cv2.applyColorMap((depth_map * 255).astype(np.uint8), cv2.COLORMAP_PLASMA)
    depth_colored = cv2.cvtColor(depth_colored, cv2.COLOR_BGR2RGB)
    
    # Blend with original image
    original_np = np.array(original_image)
    blended = cv2.addWeighted(original_np, 0.7, depth_colored, 0.3, 0)
    
    return Image.fromarray(blended)

def main():
    # ---- CONFIGURATION ----
    IMAGE_PATH = "IMG_7615.jpg"
    OUTPUT_VIDEO = "painting_3d_effect.mp4"
    
    # Check if image file exists
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image file '{IMAGE_PATH}' not found!")
        sys.exit(1)
    
    print(f"🎨 Loading image: {IMAGE_PATH}")
    
    try:
        # ---- LOAD MiDaS DEPTH MODEL ----
        print("🧠 Loading MiDaS depth estimation model...")
        midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
        midas.eval()
        transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
        print("✓ Model loaded successfully")
        
        # Load and preprocess image
        print("📸 Processing image...")
        img = Image.open(IMAGE_PATH).convert("RGB")
        
        # Resize image for better processing if too large
        original_size = img.size
        if max(original_size) > 1024:
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            print(f"🔄 Resized image from {original_size} to {img.size}")
        
        img_np_input = np.array(img)
        img_input = transform(img_np_input)
        
        # Depth estimation
        print("🕳️  Estimating depth...")
        with torch.no_grad():
            depth = midas(img_input).squeeze().cpu().numpy()
        
        # Convert original image to numpy
        img_np = np.array(img)
        h, w, _ = img_np.shape
        
        # Resize depth map to match original image dimensions
        depth_resized = cv2.resize(depth, (w, h))
        depth_norm = cv2.normalize(depth_resized, None, 0, 1, cv2.NORM_MINMAX)
        
        # Create artistic depth visualization
        print("🎭 Creating artistic depth visualization...")
        depth_vis = create_depth_visualization(depth_norm, img)
        
        # ---- CREATE ARTISTIC FRAMES ----
        print("🎬 Generating artistic animation frames...")
        frames = []
        num_frames = 150  # Longer animation for more artistic effect
        
        for i in range(num_frames):
            if i % 15 == 0:  # Progress indicator
                print(f"🎨 Creating artistic frame {i+1}/{num_frames}")
            
            # Apply artistic depth-based transformation
            artistic_frame = apply_artistic_filter(img, depth_norm, i, num_frames)
            
            # Add additional artistic effects
            artistic_frame = add_artistic_effects(artistic_frame, i, num_frames)
            
            # Every 30th frame, blend in depth visualization for artistic effect
            if i % 30 < 3:
                frame_np = np.array(artistic_frame)
                depth_np = np.array(depth_vis)
                blended = cv2.addWeighted(frame_np, 0.8, depth_np, 0.2, 0)
                artistic_frame = Image.fromarray(blended)
            
            frames.append(artistic_frame)
        
        print("✓ All artistic frames generated")
        
        # ---- EXPORT ARTISTIC VIDEO ----
        print(f"🎞️  Exporting artistic video to {OUTPUT_VIDEO}...")
        clip = ImageSequenceClip([np.array(f) for f in frames], fps=30)  # Higher FPS for smoother motion
        
        # Add more sophisticated video encoding
        clip.write_videofile(
            OUTPUT_VIDEO, 
            codec="libx264", 
            audio=False,
            bitrate="8000k",  # Higher bitrate for better quality
            ffmpeg_params=["-crf", "18"]  # High quality encoding
        )
        print(f"✨ Artistic video exported successfully: {OUTPUT_VIDEO}")
        print(f"🎯 Duration: {num_frames/30:.1f} seconds at 30 FPS")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()