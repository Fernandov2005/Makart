import cv2
import torch
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from torchvision.transforms import Compose, ToTensor, Normalize
from moviepy.editor import ImageSequenceClip, CompositeVideoClip
import os
import sys
import random

class ParticleSystem:
    def __init__(self, width, height, max_particles=2000):
        self.width = width
        self.height = height
        self.max_particles = max_particles
        self.particles = []
        
    def add_particle(self, x, y, color, depth_val, frame_index):
        """Add a new particle with 3D properties"""
        # Particle properties based on depth
        z_distance = depth_val * 100  # Depth determines how far particles float
        velocity_x = random.uniform(-2, 2) * (1 + depth_val)
        velocity_y = random.uniform(-3, -1) * (1 + depth_val * 2)  # Float upward
        velocity_z = random.uniform(0.5, 2) * depth_val  # Forward movement
        
        particle = {
            'x': x,
            'y': y,
            'z': z_distance,
            'vx': velocity_x,
            'vy': velocity_y,
            'vz': velocity_z,
            'color': color,
            'size': random.uniform(2, 6) * (1 + depth_val),
            'life': random.uniform(60, 120),  # Particle lifetime
            'birth_frame': frame_index,
            'opacity': 255,
            'rotation': random.uniform(0, 360),
            'rotation_speed': random.uniform(-5, 5)
        }
        
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
    
    def update_particles(self, frame_index):
        """Update all particles for this frame"""
        updated_particles = []
        
        for particle in self.particles:
            age = frame_index - particle['birth_frame']
            
            if age < particle['life']:
                # Update position with 3D physics
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['z'] += particle['vz']
                
                # Add gravity and air resistance
                particle['vy'] += 0.1  # Slight gravity
                particle['vx'] *= 0.995  # Air resistance
                particle['vy'] *= 0.995
                particle['vz'] *= 0.99
                
                # Update visual properties
                particle['rotation'] += particle['rotation_speed']
                life_ratio = age / particle['life']
                particle['opacity'] = int(255 * (1 - life_ratio))
                
                # 3D size scaling based on z-distance
                scale_factor = 1 + (particle['z'] / 200)
                particle['current_size'] = particle['size'] * scale_factor
                
                updated_particles.append(particle)
        
        self.particles = updated_particles
    
    def render_particles(self, image):
        """Render all particles onto the image"""
        img_array = np.array(image)
        draw_img = Image.fromarray(img_array)
        draw = ImageDraw.Draw(draw_img, 'RGBA')
        
        # Sort particles by z-distance (far to near)
        sorted_particles = sorted(self.particles, key=lambda p: p['z'], reverse=True)
        
        for particle in sorted_particles:
            if 0 <= particle['x'] < self.width and 0 <= particle['y'] < self.height:
                # Create particle color with opacity
                r, g, b = particle['color']
                alpha = max(0, min(255, particle['opacity']))
                color = (r, g, b, alpha)
                
                # Draw particle as circle with size based on 3D distance
                size = max(1, int(particle['current_size']))
                x, y = int(particle['x']), int(particle['y'])
                
                # Add slight blur for depth effect
                if particle['z'] > 50:
                    # Far particles are more blurred
                    blur_size = max(1, int(particle['z'] / 30))
                    for i in range(blur_size):
                        offset = i - blur_size // 2
                        alpha_reduced = alpha // (blur_size + 1)
                        blur_color = (r, g, b, alpha_reduced)
                        draw.ellipse([
                            x + offset - size//2, y + offset - size//2,
                            x + offset + size//2, y + offset + size//2
                        ], fill=blur_color)
                else:
                    # Near particles are sharp
                    draw.ellipse([
                        x - size//2, y - size//2,
                        x + size//2, y + size//2
                    ], fill=color)
        
        return draw_img

class ArtisticStyleProcessor:
    def __init__(self, width=1024, height=1024):
        self.styles = {
            'ethereal': self.ethereal_style,
            'cyberpunk': self.cyberpunk_style,
            'impressionist': self.impressionist_style,
            'abstract': self.abstract_style,
            'dreamlike': self.dreamlike_style,
            'particle_powder': self.particle_powder_style
        }
        self.particle_system = ParticleSystem(width, height)
        self.color_cache = {}
    
    def extract_dominant_colors(self, image, depth_map, num_colors=8):
        """Extract dominant colors from different depth regions"""
        img_array = np.array(image)
        h, w, _ = img_array.shape
        
        # Divide into depth regions
        depth_regions = []
        for i in range(num_colors):
            depth_threshold = i / num_colors
            mask = (depth_map >= depth_threshold) & (depth_map < depth_threshold + 0.125)
            if np.any(mask):
                region_colors = img_array[mask]
                if len(region_colors) > 0:
                    avg_color = np.mean(region_colors, axis=0).astype(int)
                    depth_regions.append((depth_threshold, tuple(avg_color)))
        
        return depth_regions
    
    def particle_powder_style(self, image, depth_map, frame_index, total_frames):
        """Amazing 3D particle powder effect where colors float off canvas"""
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        
        # Extract colors for particles if not cached
        if not self.color_cache:
            self.color_cache = self.extract_dominant_colors(image, depth_map)
        
        # Create base image with subtle movement
        enhanced_img = img_array.copy()
        
        # Add particles based on depth and color intensity
        particle_spawn_rate = max(1, int(30 * (1 + np.sin(time_factor * 4 * np.pi))))
        
        for _ in range(particle_spawn_rate):
            # Random spawn location
            x = random.randint(0, w-1)
            y = random.randint(0, h-1)
            depth_val = depth_map[y, x]
            
            # Higher depth areas spawn more particles
            if random.random() < depth_val * 0.8:
                # Get color from original image at this location
                pixel_color = tuple(img_array[y, x].astype(int))
                
                # Add some color variation
                r, g, b = pixel_color
                r = max(0, min(255, r + random.randint(-20, 20)))
                g = max(0, min(255, g + random.randint(-20, 20)))
                b = max(0, min(255, b + random.randint(-20, 20)))
                
                self.particle_system.add_particle(x, y, (r, g, b), depth_val, frame_index)
        
        # Update particle system
        self.particle_system.update_particles(frame_index)
        
        # Create depth-based color extraction effect on canvas
        extraction_intensity = 0.3 + 0.2 * np.sin(time_factor * 2 * np.pi)
        
        for y in range(h):
            for x in range(w):
                depth_val = depth_map[y, x]
                
                # Areas with high depth lose color more (powder effect)
                if depth_val > 0.6:
                    fade_factor = 1 - (depth_val * extraction_intensity * 0.4)
                    enhanced_img[y, x] *= fade_factor
                    
                    # Add slight desaturation where color is extracted
                    gray_val = np.mean(enhanced_img[y, x])
                    blend_factor = depth_val * 0.2
                    enhanced_img[y, x] = enhanced_img[y, x] * (1 - blend_factor) + gray_val * blend_factor
        
        # Create subtle canvas movement
        wave_strength = 2
        for y in range(h):
            wave_offset = int(wave_strength * np.sin(time_factor * 2 * np.pi + y * 0.01))
            if wave_offset != 0:
                enhanced_img[y] = np.roll(enhanced_img[y], wave_offset, axis=0)
        
        # Convert back to PIL Image
        canvas_img = Image.fromarray(np.clip(enhanced_img, 0, 255).astype(np.uint8))
        
        # Render particles on top
        final_img = self.particle_system.render_particles(canvas_img)
        
        return np.array(final_img)
    
    def ethereal_style(self, image, depth_map, frame_index, total_frames):
        """Soft, ethereal, light-based effects like NEW BORN"""
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        
        # Create flowing light effects
        enhanced_img = img_array.copy()
        
        # Organic, breathing movement
        for y in range(h):
            for x in range(w):
                depth_val = depth_map[y, x]
                
                # Gentle, wave-like displacement
                wave_x = np.sin(time_factor * 2 * np.pi + y * 0.02 + x * 0.01) * depth_val * 8
                wave_y = np.cos(time_factor * 1.5 * np.pi + y * 0.015 + x * 0.02) * depth_val * 5
                
                new_x = max(0, min(w-1, x + int(wave_x)))
                new_y = max(0, min(h-1, y + int(wave_y)))
                
                enhanced_img[y, x] = img_array[new_y, new_x]
        
        # Add ethereal glow to bright areas
        brightness = np.mean(enhanced_img, axis=2)
        glow_mask = brightness > 180
        enhanced_img[glow_mask] *= 1.3
        
        # Soft color temperature shift
        enhanced_img[:, :, 0] *= 1.1  # Warmer tones
        enhanced_img[:, :, 2] *= 0.95  # Reduce blue slightly
        
        return np.clip(enhanced_img, 0, 255).astype(np.uint8)
    
    def cyberpunk_style(self, image, depth_map, frame_index, total_frames):
        """Futuristic, neon-inspired effects"""
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        
        enhanced_img = img_array.copy()
        
        # Sharp, geometric distortions
        for y in range(0, h, 2):
            for x in range(0, w, 2):
                depth_val = depth_map[y, x]
                
                # Angular displacement
                displacement = int(depth_val * 12 * np.sin(time_factor * 4 * np.pi))
                new_x = max(0, min(w-1, x + displacement))
                
                enhanced_img[y:y+2, x:x+2] = img_array[y:y+2, new_x:new_x+2]
        
        # Enhance neon colors
        enhanced_img[:, :, 0] *= 1.2  # More red
        enhanced_img[:, :, 1] *= 0.8   # Less green
        enhanced_img[:, :, 2] *= 1.4   # Much more blue
        
        return np.clip(enhanced_img, 0, 255).astype(np.uint8)
    
    def impressionist_style(self, image, depth_map, frame_index, total_frames):
        """Painterly, brush-stroke effects"""
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        
        enhanced_img = img_array.copy()
        
        # Brush-like strokes
        for y in range(0, h, 4):
            for x in range(0, w, 4):
                depth_val = depth_map[y, x]
                
                # Brush stroke direction based on depth
                stroke_length = int(depth_val * 6 + 2)
                angle = time_factor * np.pi + depth_val * np.pi
                
                dx = int(np.cos(angle) * stroke_length)
                dy = int(np.sin(angle) * stroke_length)
                
                new_x = max(0, min(w-1, x + dx))
                new_y = max(0, min(h-1, y + dy))
                
                enhanced_img[y:y+4, x:x+4] = img_array[new_y:new_y+4, new_x:new_x+4]
        
        # Soften colors
        enhanced_img *= 0.9
        enhanced_img[:, :, 1] *= 1.1  # Enhance greens
        
        return np.clip(enhanced_img, 0, 255).astype(np.uint8)
    
    def abstract_style(self, image, depth_map, frame_index, total_frames):
        """Abstract, geometric transformations"""
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        
        enhanced_img = img_array.copy()
        
        # Create abstract geometric patterns
        for y in range(h):
            for x in range(w):
                depth_val = depth_map[y, x]
                
                # Kaleidoscope-like effect
                center_x, center_y = w // 2, h // 2
                angle = np.arctan2(y - center_y, x - center_x) + time_factor * np.pi
                radius = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                
                new_angle = angle + depth_val * np.pi * 0.5
                new_x = int(center_x + np.cos(new_angle) * radius)
                new_y = int(center_y + np.sin(new_angle) * radius)
                
                new_x = max(0, min(w-1, new_x))
                new_y = max(0, min(h-1, new_y))
                
                enhanced_img[y, x] = img_array[new_y, new_x]
        
        return np.clip(enhanced_img, 0, 255).astype(np.uint8)
    
    def dreamlike_style(self, image, depth_map, frame_index, total_frames):
        """Soft, dream-like flowing effects"""
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        
        enhanced_img = img_array.copy()
        
        # Liquid-like flow
        for y in range(h):
            for x in range(w):
                depth_val = depth_map[y, x]
                
                # Multiple wave interference
                wave1 = np.sin(time_factor * 2 * np.pi + y * 0.03) * depth_val * 10
                wave2 = np.cos(time_factor * 1.5 * np.pi + x * 0.025) * depth_val * 8
                wave3 = np.sin(time_factor * 3 * np.pi + (x + y) * 0.01) * depth_val * 6
                
                total_wave_x = wave1 + wave2
                total_wave_y = wave2 + wave3
                
                new_x = max(0, min(w-1, x + int(total_wave_x)))
                new_y = max(0, min(h-1, y + int(total_wave_y)))
                
                enhanced_img[y, x] = img_array[new_y, new_x]
        
        # Dream-like color enhancement
        enhanced_img[:, :, 0] *= 1.05  # Slight warmth
        enhanced_img[:, :, 1] *= 1.1   # Enhanced greens
        enhanced_img[:, :, 2] *= 1.08  # Slight blue enhancement
        
        return np.clip(enhanced_img, 0, 255).astype(np.uint8)

def create_artistic_overlay(width, height, frame_index, total_frames, style='ethereal'):
    """Create artistic overlay elements"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    time_factor = frame_index / total_frames
    
    if style == 'ethereal':
        # Soft light rays
        alpha = int(30 + 20 * np.sin(time_factor * 2 * np.pi))
        for i in range(3):
            x = int(width * (0.2 + 0.6 * np.sin(time_factor * np.pi + i)))
            y = int(height * (0.3 + 0.4 * np.cos(time_factor * 1.5 * np.pi + i)))
            draw.ellipse([x-50, y-50, x+50, y+50], fill=(255, 255, 255, alpha))
    
    elif style == 'cyberpunk':
        # Neon grid lines
        alpha = int(40 + 30 * np.sin(time_factor * 4 * np.pi))
        for i in range(0, width, 80):
            draw.line([i, 0, i, height], fill=(0, 255, 255, alpha), width=2)
        for i in range(0, height, 80):
            draw.line([0, i, width, i], fill=(255, 0, 255, alpha), width=2)
    
    elif style == 'particle_powder':
        # Add magical sparkles around particles
        alpha = int(60 + 40 * np.sin(time_factor * 3 * np.pi))
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 8)
            sparkle_color = (255, 255, 255, alpha)
            draw.ellipse([x-size, y-size, x+size, y+size], fill=sparkle_color)
    
    return overlay

def main():
    # Configuration
    IMAGE_PATH = "IMG_7615.jpg"
    OUTPUT_VIDEO = "painting_3d_effect_premium.mp4"
    
    # Choose artistic style - NEW PARTICLE POWDER EFFECT!
    ARTISTIC_STYLE = 'particle_powder'  # Options: ethereal, cyberpunk, impressionist, abstract, dreamlike, particle_powder
    
    print(f"🎨 Creating gallery-quality animation with '{ARTISTIC_STYLE}' style")
    print(f"📸 Loading image: {IMAGE_PATH}")
    
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Error: Image file '{IMAGE_PATH}' not found!")
        sys.exit(1)
    
    try:
        # Load MiDaS model
        print("🧠 Loading depth estimation model...")
        midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
        midas.eval()
        transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
        print("✓ Model loaded")
        
        # Process image
        print("📸 Processing image...")
        img = Image.open(IMAGE_PATH).convert("RGB")
        
        # Optimize size
        if max(img.size) > 1200:
            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        
        img_np = np.array(img)
        img_input = transform(img_np)
        
        # Depth estimation
        print("🕳️ Analyzing depth...")
        with torch.no_grad():
            depth = midas(img_input).squeeze().cpu().numpy()
        
        h, w, _ = img_np.shape
        depth_resized = cv2.resize(depth, (w, h))
        depth_norm = cv2.normalize(depth_resized, None, 0, 1, cv2.NORM_MINMAX)
        
        # Initialize artistic processor with image dimensions
        processor = ArtisticStyleProcessor(w, h)
        
        # Create frames
        print(f"🎬 Generating {ARTISTIC_STYLE} animation...")
        frames = []
        num_frames = 240  # 8 seconds for particle effect
        
        for i in range(num_frames):
            if i % 20 == 0:
                print(f"✨ Frame {i+1}/{num_frames} - Particles: {len(processor.particle_system.particles)}")
            
            # Apply artistic style
            artistic_frame = processor.styles[ARTISTIC_STYLE](img, depth_norm, i, num_frames)
            frame_img = Image.fromarray(artistic_frame)
            
            # Add artistic enhancement
            time_factor = i / num_frames
            
            # Dynamic saturation
            saturation = 1.0 + 0.3 * np.sin(time_factor * 2 * np.pi)
            enhancer = ImageEnhance.Color(frame_img)
            frame_img = enhancer.enhance(saturation)
            
            # Dynamic contrast
            contrast = 1.0 + 0.2 * np.cos(time_factor * 1.5 * np.pi)
            enhancer = ImageEnhance.Contrast(frame_img)
            frame_img = enhancer.enhance(contrast)
            
            # Add overlay elements
            overlay = create_artistic_overlay(w, h, i, num_frames, ARTISTIC_STYLE)
            frame_img = Image.alpha_composite(frame_img.convert('RGBA'), overlay)
            frame_img = frame_img.convert('RGB')
            
            frames.append(frame_img)
        
        print("✓ All frames generated")
        
        # Export with maximum quality
        print(f"🎞️ Exporting premium video...")
        clip = ImageSequenceClip([np.array(f) for f in frames], fps=30)
        
        clip.write_videofile(
            OUTPUT_VIDEO,
            codec="libx264",
            audio=False,
            bitrate="12000k",  # Very high bitrate
            ffmpeg_params=["-crf", "15", "-preset", "slow"]  # Maximum quality
        )
        
        print(f"🌟 Gallery-quality video created: {OUTPUT_VIDEO}")
        print(f"🎯 Style: {ARTISTIC_STYLE} | Duration: 8.0s | Quality: Premium")
        print(f"✨ Particle Effect: Colors floating off canvas in 3D!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 