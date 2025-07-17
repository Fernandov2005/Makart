#!/usr/bin/env python3
"""
Gallery-Quality Painting Animation Style Selector
Inspired by digital art exhibitions like NEW BORN by Hakan & Süleyman Yılmaz
"""

import os
import sys
import subprocess

class StyleSelector:
    def __init__(self):
        self.styles = {
            '1': ('ethereal', 'Soft, light-based effects with organic breathing movements - Like NEW BORN'),
            '2': ('cyberpunk', 'Futuristic neon effects with geometric distortions'),
            '3': ('impressionist', 'Painterly brush-stroke effects with artistic flow'),
            '4': ('abstract', 'Geometric kaleidoscope transformations'),
            '5': ('dreamlike', 'Liquid, dream-like flowing effects with wave interference'),
            '6': ('particle_powder', '🌟 NEW! Colors float off canvas as 3D powder particles - AMAZING!')
        }
        
        self.durations = {
            '1': ('short', 90, '3 seconds - Quick preview'),
            '2': ('medium', 150, '5 seconds - Standard length'),
            '3': ('long', 180, '6 seconds - Gallery quality'),
            '4': ('extended', 240, '8 seconds - Exhibition piece'),
            '5': ('epic', 300, '10 seconds - Epic particle showcase')
        }
        
        self.qualities = {
            '1': ('draft', '4000k', '20', 'Draft quality - Fast export'),
            '2': ('good', '8000k', '18', 'Good quality - Balanced'),
            '3': ('premium', '12000k', '15', 'Premium quality - Gallery ready'),
            '4': ('exhibition', '16000k', '12', 'Exhibition quality - Maximum detail')
        }

    def display_banner(self):
        print("\n" + "="*60)
        print("🎨 GALLERY-QUALITY PAINTING ANIMATION STUDIO 🎨")
        print("   Inspired by NEW BORN - Hakan & Süleyman Yılmaz")
        print("="*60)

    def select_style(self):
        print("\n🎭 Choose your artistic style:")
        for key, (style, description) in self.styles.items():
            print(f"  {key}. {style.upper():<15} - {description}")
        
        while True:
            choice = input("\nEnter style number (1-6): ").strip()
            if choice in self.styles:
                return self.styles[choice][0]
            print("❌ Invalid choice. Please enter 1-6.")

    def select_duration(self):
        print("\n⏱️ Choose animation duration:")
        for key, (name, frames, description) in self.durations.items():
            print(f"  {key}. {description}")
        
        while True:
            choice = input("\nEnter duration number (1-5): ").strip()
            if choice in self.durations:
                return self.durations[choice][1]
            print("❌ Invalid choice. Please enter 1-5.")

    def select_quality(self):
        print("\n💎 Choose export quality:")
        for key, (name, bitrate, crf, description) in self.qualities.items():
            print(f"  {key}. {description}")
        
        while True:
            choice = input("\nEnter quality number (1-4): ").strip()
            if choice in self.qualities:
                return self.qualities[choice][1], self.qualities[choice][2]
            print("❌ Invalid choice. Please enter 1-4.")

    def create_custom_script(self, style, num_frames, bitrate, crf):
        """Generate a custom animation script with selected parameters"""
        script_content = f"""import cv2
import torch
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from torchvision.transforms import Compose, ToTensor, Normalize
from moviepy.editor import ImageSequenceClip
import os
import sys
import random

# AUTO-GENERATED CUSTOM SCRIPT
# Style: {style}
# Frames: {num_frames}
# Quality: {bitrate} bitrate, CRF {crf}

class ParticleSystem:
    def __init__(self, width, height, max_particles=2000):
        self.width = width
        self.height = height
        self.max_particles = max_particles
        self.particles = []
        
    def add_particle(self, x, y, color, depth_val, frame_index):
        z_distance = depth_val * 100
        velocity_x = random.uniform(-2, 2) * (1 + depth_val)
        velocity_y = random.uniform(-3, -1) * (1 + depth_val * 2)
        velocity_z = random.uniform(0.5, 2) * depth_val
        
        particle = {{
            'x': x, 'y': y, 'z': z_distance,
            'vx': velocity_x, 'vy': velocity_y, 'vz': velocity_z,
            'color': color,
            'size': random.uniform(2, 6) * (1 + depth_val),
            'life': random.uniform(60, 120),
            'birth_frame': frame_index,
            'opacity': 255,
            'rotation': random.uniform(0, 360),
            'rotation_speed': random.uniform(-5, 5)
        }}
        
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
    
    def update_particles(self, frame_index):
        updated_particles = []
        for particle in self.particles:
            age = frame_index - particle['birth_frame']
            if age < particle['life']:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['z'] += particle['vz']
                particle['vy'] += 0.1
                particle['vx'] *= 0.995
                particle['vy'] *= 0.995
                particle['vz'] *= 0.99
                particle['rotation'] += particle['rotation_speed']
                life_ratio = age / particle['life']
                particle['opacity'] = int(255 * (1 - life_ratio))
                scale_factor = 1 + (particle['z'] / 200)
                particle['current_size'] = particle['size'] * scale_factor
                updated_particles.append(particle)
        self.particles = updated_particles
    
    def render_particles(self, image):
        img_array = np.array(image)
        draw_img = Image.fromarray(img_array)
        draw = ImageDraw.Draw(draw_img, 'RGBA')
        sorted_particles = sorted(self.particles, key=lambda p: p['z'], reverse=True)
        
        for particle in sorted_particles:
            if 0 <= particle['x'] < self.width and 0 <= particle['y'] < self.height:
                r, g, b = particle['color']
                alpha = max(0, min(255, particle['opacity']))
                color = (r, g, b, alpha)
                size = max(1, int(particle['current_size']))
                x, y = int(particle['x']), int(particle['y'])
                
                if particle['z'] > 50:
                    blur_size = max(1, int(particle['z'] / 30))
                    for i in range(blur_size):
                        offset = i - blur_size // 2
                        alpha_reduced = alpha // (blur_size + 1)
                        blur_color = (r, g, b, alpha_reduced)
                        draw.ellipse([x + offset - size//2, y + offset - size//2,
                                    x + offset + size//2, y + offset + size//2], fill=blur_color)
                else:
                    draw.ellipse([x - size//2, y - size//2, x + size//2, y + size//2], fill=color)
        return draw_img

class ArtisticStyleProcessor:
    def __init__(self, width=1024, height=1024):
        self.styles = {{
            'ethereal': self.ethereal_style,
            'cyberpunk': self.cyberpunk_style,
            'impressionist': self.impressionist_style,
            'abstract': self.abstract_style,
            'dreamlike': self.dreamlike_style,
            'particle_powder': self.particle_powder_style
        }}
        self.particle_system = ParticleSystem(width, height)
        self.color_cache = {{}}
    
    def particle_powder_style(self, image, depth_map, frame_index, total_frames):
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        enhanced_img = img_array.copy()
        
        particle_spawn_rate = max(1, int(30 * (1 + np.sin(time_factor * 4 * np.pi))))
        
        for _ in range(particle_spawn_rate):
            x = random.randint(0, w-1)
            y = random.randint(0, h-1)
            depth_val = depth_map[y, x]
            
            if random.random() < depth_val * 0.8:
                pixel_color = tuple(img_array[y, x].astype(int))
                r, g, b = pixel_color
                r = max(0, min(255, r + random.randint(-20, 20)))
                g = max(0, min(255, g + random.randint(-20, 20)))
                b = max(0, min(255, b + random.randint(-20, 20)))
                self.particle_system.add_particle(x, y, (r, g, b), depth_val, frame_index)
        
        self.particle_system.update_particles(frame_index)
        
        extraction_intensity = 0.3 + 0.2 * np.sin(time_factor * 2 * np.pi)
        for y in range(h):
            for x in range(w):
                depth_val = depth_map[y, x]
                if depth_val > 0.6:
                    fade_factor = 1 - (depth_val * extraction_intensity * 0.4)
                    enhanced_img[y, x] *= fade_factor
                    gray_val = np.mean(enhanced_img[y, x])
                    blend_factor = depth_val * 0.2
                    enhanced_img[y, x] = enhanced_img[y, x] * (1 - blend_factor) + gray_val * blend_factor
        
        wave_strength = 2
        for y in range(h):
            wave_offset = int(wave_strength * np.sin(time_factor * 2 * np.pi + y * 0.01))
            if wave_offset != 0:
                enhanced_img[y] = np.roll(enhanced_img[y], wave_offset, axis=0)
        
        canvas_img = Image.fromarray(np.clip(enhanced_img, 0, 255).astype(np.uint8))
        final_img = self.particle_system.render_particles(canvas_img)
        return np.array(final_img)
    
    def ethereal_style(self, image, depth_map, frame_index, total_frames):
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        enhanced_img = img_array.copy()
        
        for y in range(h):
            for x in range(w):
                depth_val = depth_map[y, x]
                wave_x = np.sin(time_factor * 2 * np.pi + y * 0.02 + x * 0.01) * depth_val * 8
                wave_y = np.cos(time_factor * 1.5 * np.pi + y * 0.015 + x * 0.02) * depth_val * 5
                
                new_x = max(0, min(w-1, x + int(wave_x)))
                new_y = max(0, min(h-1, y + int(wave_y)))
                enhanced_img[y, x] = img_array[new_y, new_x]
        
        brightness = np.mean(enhanced_img, axis=2)
        glow_mask = brightness > 180
        enhanced_img[glow_mask] *= 1.3
        enhanced_img[:, :, 0] *= 1.1
        enhanced_img[:, :, 2] *= 0.95
        return np.clip(enhanced_img, 0, 255).astype(np.uint8)
    
    def cyberpunk_style(self, image, depth_map, frame_index, total_frames):
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        enhanced_img = img_array.copy()
        
        for y in range(0, h, 2):
            for x in range(0, w, 2):
                depth_val = depth_map[y, x]
                displacement = int(depth_val * 12 * np.sin(time_factor * 4 * np.pi))
                new_x = max(0, min(w-1, x + displacement))
                enhanced_img[y:y+2, x:x+2] = img_array[y:y+2, new_x:new_x+2]
        
        enhanced_img[:, :, 0] *= 1.2
        enhanced_img[:, :, 1] *= 0.8
        enhanced_img[:, :, 2] *= 1.4
        return np.clip(enhanced_img, 0, 255).astype(np.uint8)
    
    def impressionist_style(self, image, depth_map, frame_index, total_frames):
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        enhanced_img = img_array.copy()
        
        for y in range(0, h, 4):
            for x in range(0, w, 4):
                depth_val = depth_map[y, x]
                stroke_length = int(depth_val * 6 + 2)
                angle = time_factor * np.pi + depth_val * np.pi
                
                dx = int(np.cos(angle) * stroke_length)
                dy = int(np.sin(angle) * stroke_length)
                
                new_x = max(0, min(w-1, x + dx))
                new_y = max(0, min(h-1, y + dy))
                
                enhanced_img[y:y+4, x:x+4] = img_array[new_y:new_y+4, new_x:new_x+4]
        
        enhanced_img *= 0.9
        enhanced_img[:, :, 1] *= 1.1
        return np.clip(enhanced_img, 0, 255).astype(np.uint8)
    
    def abstract_style(self, image, depth_map, frame_index, total_frames):
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        enhanced_img = img_array.copy()
        
        for y in range(h):
            for x in range(w):
                depth_val = depth_map[y, x]
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
        img_array = np.array(image).astype(np.float32)
        h, w, c = img_array.shape
        time_factor = frame_index / total_frames
        enhanced_img = img_array.copy()
        
        for y in range(h):
            for x in range(w):
                depth_val = depth_map[y, x]
                wave1 = np.sin(time_factor * 2 * np.pi + y * 0.03) * depth_val * 10
                wave2 = np.cos(time_factor * 1.5 * np.pi + x * 0.025) * depth_val * 8
                wave3 = np.sin(time_factor * 3 * np.pi + (x + y) * 0.01) * depth_val * 6
                
                total_wave_x = wave1 + wave2
                total_wave_y = wave2 + wave3
                
                new_x = max(0, min(w-1, x + int(total_wave_x)))
                new_y = max(0, min(h-1, y + int(total_wave_y)))
                enhanced_img[y, x] = img_array[new_y, new_x]
        
        enhanced_img[:, :, 0] *= 1.05
        enhanced_img[:, :, 1] *= 1.1
        enhanced_img[:, :, 2] *= 1.08
        return np.clip(enhanced_img, 0, 255).astype(np.uint8)

def main():
    IMAGE_PATH = "IMG_7615.jpg"
    OUTPUT_VIDEO = "painting_3d_effect_{style}.mp4"
    
    print(f"🎨 Creating {style.upper()} style animation...")
    
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Error: Image file '{{IMAGE_PATH}}' not found!")
        sys.exit(1)
    
    try:
        print("🧠 Loading depth estimation model...")
        midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
        midas.eval()
        transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
        
        print("📸 Processing image...")
        img = Image.open(IMAGE_PATH).convert("RGB")
        
        if max(img.size) > 1200:
            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        
        img_np = np.array(img)
        img_input = transform(img_np)
        
        print("🕳️ Analyzing depth...")
        with torch.no_grad():
            depth = midas(img_input).squeeze().cpu().numpy()
        
        h, w, _ = img_np.shape
        depth_resized = cv2.resize(depth, (w, h))
        depth_norm = cv2.normalize(depth_resized, None, 0, 1, cv2.NORM_MINMAX)
        
        processor = ArtisticStyleProcessor(w, h)
        
        print(f"🎬 Generating {{num_frames}} frames...")
        frames = []
        
        for i in range({num_frames}):
            if i % 20 == 0:
                particle_count = len(processor.particle_system.particles) if hasattr(processor, 'particle_system') else 0
                print(f"✨ Frame {{i+1}}/{num_frames} - Particles: {{particle_count}}")
            
            artistic_frame = processor.styles['{style}'](img, depth_norm, i, {num_frames})
            frame_img = Image.fromarray(artistic_frame)
            
            time_factor = i / {num_frames}
            saturation = 1.0 + 0.4 * np.sin(time_factor * 2 * np.pi)
            enhancer = ImageEnhance.Color(frame_img)
            frame_img = enhancer.enhance(saturation)
            
            contrast = 1.0 + 0.3 * np.cos(time_factor * 1.5 * np.pi)
            enhancer = ImageEnhance.Contrast(frame_img)
            frame_img = enhancer.enhance(contrast)
            
            frames.append(frame_img)
        
        print(f"🎞️ Exporting {style} video...")
        clip = ImageSequenceClip([np.array(f) for f in frames], fps=30)
        
        clip.write_videofile(
            OUTPUT_VIDEO,
            codec="libx264",
            audio=False,
            bitrate="{bitrate}",
            ffmpeg_params=["-crf", "{crf}", "-preset", "slow"]
        )
        
        duration = {num_frames}/30
        print(f"🌟 {{OUTPUT_VIDEO}} created!")
        print(f"🎯 Style: {style} | Duration: {{duration:.1f}}s | Quality: {bitrate}")
        
    except Exception as e:
        print(f"❌ Error: {{str(e)}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
        
        filename = f"custom_{style}_animation.py"
        with open(filename, 'w') as f:
            f.write(script_content)
        
        return filename

    def run(self):
        self.display_banner()
        
        print("\n🖼️  Image: IMG_7615.jpg")
        if not os.path.exists("IMG_7615.jpg"):
            print("❌ Error: IMG_7615.jpg not found!")
            return
        
        style = self.select_style()
        num_frames = self.select_duration()
        bitrate, crf = self.select_quality()
        
        print(f"\n✨ Configuration:")
        print(f"   Style: {style.upper()}")
        print(f"   Duration: {num_frames/30:.1f} seconds")
        print(f"   Quality: {bitrate} bitrate, CRF {crf}")
        
        if style == 'particle_powder':
            print(f"\n🌟 PARTICLE POWDER EFFECT SELECTED!")
            print(f"   • Colors will float off canvas as 3D particles")
            print(f"   • Up to 2000 particles with realistic physics")
            print(f"   • Depth-based spawning and movement")
            print(f"   • Canvas will gradually fade where particles escape")
        
        proceed = input("\n🎬 Create animation? (y/n): ").strip().lower()
        if proceed not in ['y', 'yes']:
            print("Animation cancelled.")
            return
        
        # Create and run custom script
        script_file = self.create_custom_script(style, num_frames, bitrate, crf)
        
        print(f"\n🎨 Generated custom script: {script_file}")
        print("🚀 Starting animation generation...")
        
        try:
            result = subprocess.run([sys.executable, script_file], check=True)
            print("\n🎉 Animation completed successfully!")
            
            # Clean up custom script
            os.remove(script_file)
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error during animation: {e}")
        except KeyboardInterrupt:
            print("\n⏹️  Animation cancelled by user")
            if os.path.exists(script_file):
                os.remove(script_file)

if __name__ == "__main__":
    selector = StyleSelector()
    selector.run() 