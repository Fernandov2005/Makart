import cv2
import torch
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from torchvision.transforms import Compose, ToTensor, Normalize
from moviepy.editor import ImageSequenceClip, CompositeVideoClip
import os
import sys
import random
import math

class AdvancedParticleSystem:
    def __init__(self, width, height, image_array, depth_map):
        self.width = width
        self.height = height
        self.particles = []
        self.original_image = image_array.copy()
        self.depth_map = depth_map
        self.canvas_bounds = {'left': 0, 'right': width, 'top': 0, 'bottom': height}
        self.expanded_bounds = {
            'left': -width//2, 'right': width + width//2,
            'top': -height//2, 'bottom': height + height//2
        }
        self.initialize_particles()
        
    def initialize_particles(self):
        """Convert the ENTIRE painting into particles - every pixel becomes a particle"""
        print("🎨 Converting entire painting to particles...")
        
        # Sample every 2nd pixel to create dense particle coverage
        step = 1  # Smaller step = more particles
        particle_id = 0
        
        for y in range(0, self.height, step):
            for x in range(0, self.width, step):
                # Get pixel color and depth
                pixel_color = tuple(self.original_image[y, x].astype(int))
                depth_val = self.depth_map[y, x]
                
                # Create particle with original position tracking
                particle = {
                    'id': particle_id,
                    'original_x': x,
                    'original_y': y,
                    'x': float(x),
                    'y': float(y),
                    'z': 0.0,
                    'vx': 0.0,
                    'vy': 0.0,
                    'vz': 0.0,
                    'color': pixel_color,
                    'depth': depth_val,
                    'size': random.uniform(1.5, 4.0),
                    'opacity': 255,
                    'phase': 'expanding',  # expanding, organized, returning
                    'formation_angle': random.uniform(0, 2 * math.pi),
                    'formation_radius': random.uniform(50, 200),
                    'orbit_speed': random.uniform(0.02, 0.08),
                    'return_speed': 0.0
                }
                
                self.particles.append(particle)
                particle_id += 1
        
        print(f"✨ Created {len(self.particles)} particles from the entire painting!")
    
    def get_organized_movement(self, particle, frame_index, total_frames):
        """Calculate organized movement patterns"""
        time_factor = frame_index / total_frames
        
        # Different movement patterns based on depth and position
        center_x, center_y = self.width // 2, self.height // 2
        
        # 1. Spiral movement for foreground particles
        if particle['depth'] > 0.6:
            spiral_radius = 100 + 50 * math.sin(time_factor * 2 * math.pi)
            spiral_angle = particle['formation_angle'] + time_factor * 4 * math.pi
            target_x = center_x + spiral_radius * math.cos(spiral_angle)
            target_y = center_y + spiral_radius * math.sin(spiral_angle)
            
        # 2. Orbital movement for mid-ground particles
        elif particle['depth'] > 0.3:
            orbit_radius = particle['formation_radius'] + 30 * math.sin(time_factor * 3 * math.pi)
            orbit_angle = particle['formation_angle'] + particle['orbit_speed'] * frame_index
            target_x = center_x + orbit_radius * math.cos(orbit_angle)
            target_y = center_y + orbit_radius * math.sin(orbit_angle)
            
        # 3. Wave formation for background particles
        else:
            wave_amplitude = 80
            wave_frequency = 0.02
            wave_offset = time_factor * 2 * math.pi
            target_x = particle['original_x'] + wave_amplitude * math.sin(particle['original_y'] * wave_frequency + wave_offset)
            target_y = particle['original_y'] + wave_amplitude * math.cos(particle['original_x'] * wave_frequency + wave_offset)
        
        return target_x, target_y
    
    def update_particles(self, frame_index, total_frames):
        """Update all particles with sophisticated movement phases"""
        time_factor = frame_index / total_frames
        
        # Define animation phases
        expansion_phase = 0.25   # First 25% - particles expand out
        organized_phase = 0.60   # Next 60% - organized movement
        return_phase = 0.15      # Last 15% - return to original positions
        
        for particle in self.particles:
            if time_factor < expansion_phase:
                # EXPANSION PHASE - particles explode out of the painting
                self.update_expansion_phase(particle, time_factor / expansion_phase)
                
            elif time_factor < expansion_phase + organized_phase:
                # ORGANIZED MOVEMENT PHASE - beautiful formations
                org_time = (time_factor - expansion_phase) / organized_phase
                self.update_organized_phase(particle, org_time, frame_index, total_frames)
                
            else:
                # RETURN PHASE - particles return to original positions
                return_time = (time_factor - expansion_phase - organized_phase) / return_phase
                self.update_return_phase(particle, return_time)
    
    def update_expansion_phase(self, particle, phase_progress):
        """Particles explode out of the painting with vibrant colors"""
        # Calculate direction from center
        center_x, center_y = self.width // 2, self.height // 2
        dx = particle['original_x'] - center_x
        dy = particle['original_y'] - center_y
        
        # Normalize direction
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Explosion strength based on depth (foreground explodes more)
        explosion_strength = 200 + particle['depth'] * 300
        
        # Curved explosion path
        curve_factor = math.sin(phase_progress * math.pi)
        explosion_distance = explosion_strength * curve_factor
        
        # Add some randomness for organic movement
        random_offset_x = 30 * math.sin(phase_progress * 4 * math.pi + particle['id'] * 0.1)
        random_offset_y = 30 * math.cos(phase_progress * 4 * math.pi + particle['id'] * 0.1)
        
        # Calculate new position
        particle['x'] = particle['original_x'] + dx * explosion_distance + random_offset_x
        particle['y'] = particle['original_y'] + dy * explosion_distance + random_offset_y
        
        # Add slight rotation around original position
        rotation_angle = phase_progress * math.pi * 0.5
        cos_rot = math.cos(rotation_angle)
        sin_rot = math.sin(rotation_angle)
        
        relative_x = particle['x'] - particle['original_x']
        relative_y = particle['y'] - particle['original_y']
        
        particle['x'] = particle['original_x'] + relative_x * cos_rot - relative_y * sin_rot
        particle['y'] = particle['original_y'] + relative_x * sin_rot + relative_y * cos_rot
        
        # Keep particles vibrant during explosion
        base_size = 3.0 + particle['depth'] * 2.0  # Larger for explosion
        particle['size'] = base_size + 1.0 * math.sin(phase_progress * 6 * math.pi + particle['id'] * 0.1)
        
        # Maintain full opacity - particles stay bright!
        particle['opacity'] = 255
        
        particle['phase'] = 'expanding'
    
    def update_organized_phase(self, particle, phase_progress, frame_index, total_frames):
        """Particles perform organized movements while staying vibrant"""
        target_x, target_y = self.get_organized_movement(particle, frame_index, total_frames)
        
        # Smooth movement towards target
        movement_speed = 0.1
        particle['x'] += (target_x - particle['x']) * movement_speed
        particle['y'] += (target_y - particle['y']) * movement_speed
        
        # Add some Z-axis movement for 3D effect
        particle['z'] = 30 * math.sin(phase_progress * 2 * math.pi + particle['id'] * 0.01)
        
        # Size pulsing effect - keep particles visible
        base_size = 2.5 + particle['depth'] * 2.5  # Slightly larger for better visibility
        pulse = 0.8 * math.sin(phase_progress * 4 * math.pi + particle['id'] * 0.05)  # More dramatic pulse
        particle['size'] = base_size + pulse
        
        # Maintain full opacity - particles stay bright!
        particle['opacity'] = 255
        
        particle['phase'] = 'organized'
    
    def update_return_phase(self, particle, phase_progress):
        """Particles return to their original positions but stay as vibrant particles"""
        # Smooth return to original position
        return_curve = 1 - (1 - phase_progress) * (1 - phase_progress)  # Ease-in curve
        
        particle['x'] = particle['x'] + (particle['original_x'] - particle['x']) * return_curve * 0.2
        particle['y'] = particle['y'] + (particle['original_y'] - particle['y']) * return_curve * 0.2
        particle['z'] = particle['z'] * (1 - return_curve)
        
        # Keep particles vibrant and visible - no size reduction
        base_size = 2.0 + particle['depth'] * 2.0
        particle['size'] = base_size + 0.5 * math.sin(phase_progress * 4 * math.pi + particle['id'] * 0.05)
        
        # Maintain full opacity - particles stay bright!
        particle['opacity'] = 255
        
        particle['phase'] = 'returning'
    
    def render_particles(self, frame_index, total_frames):
        """Render all particles to create the frame"""
        # Create expanded canvas to show particles outside original bounds
        expanded_width = self.width * 2
        expanded_height = self.height * 2
        
        # Create the image with expanded bounds
        img_array = np.zeros((expanded_height, expanded_width, 3), dtype=np.uint8)
        
        # Calculate offset to center original image area
        offset_x = self.width // 2
        offset_y = self.height // 2
        
        # Sort particles by z-distance (back to front)
        sorted_particles = sorted(self.particles, key=lambda p: p.get('z', 0))
        
        for particle in sorted_particles:
            # Calculate screen position with offset
            screen_x = int(particle['x'] + offset_x)
            screen_y = int(particle['y'] + offset_y)
            
            # Check if particle is in expanded bounds
            if (0 <= screen_x < expanded_width and 0 <= screen_y < expanded_height):
                # Calculate size with 3D perspective
                z_factor = 1.0 + particle.get('z', 0) / 100.0
                size = max(1, int(particle['size'] * z_factor))
                
                # Get color
                r, g, b = particle['color']
                
                # Apply depth-based color enhancement - make colors more vibrant!
                depth_boost = 1.2 + particle['depth'] * 0.5  # Increased color boost
                r = min(255, int(r * depth_boost))
                g = min(255, int(g * depth_boost))
                b = min(255, int(b * depth_boost))
                
                # Add extra vibrancy based on particle phase
                phase_boost = 1.0
                if particle['phase'] == 'expanding':
                    phase_boost = 1.3  # Extra bright during explosion
                elif particle['phase'] == 'organized':
                    phase_boost = 1.2  # Bright during organized movement
                else:  # returning
                    phase_boost = 1.1  # Still bright when returning
                
                r = min(255, int(r * phase_boost))
                g = min(255, int(g * phase_boost))
                b = min(255, int(b * phase_boost))
                
                # Draw particle (simple circle for now, can be enhanced)
                for dy in range(-size, size + 1):
                    for dx in range(-size, size + 1):
                        if dx*dx + dy*dy <= size*size:
                            px = screen_x + dx
                            py = screen_y + dy
                            if 0 <= px < expanded_width and 0 <= py < expanded_height:
                                # Blend with existing pixels
                                img_array[py, px] = [r, g, b]
        
        # Crop back to original size, centered
        final_img = img_array[offset_y:offset_y+self.height, offset_x:offset_x+self.width]
        
        return final_img

class ArtisticStyleProcessor:
    def __init__(self, width=1024, height=1024):
        self.width = width
        self.height = height
        self.particle_system = None
    
    def particle_powder_style(self, image, depth_map, frame_index, total_frames):
        """Revolutionary particle system where entire painting becomes organized particles"""
        # Initialize particle system on first frame
        if self.particle_system is None:
            img_array = np.array(image)
            self.particle_system = AdvancedParticleSystem(self.width, self.height, img_array, depth_map)
        
        # Update particles
        self.particle_system.update_particles(frame_index, total_frames)
        
        # Render particles
        particle_frame = self.particle_system.render_particles(frame_index, total_frames)
        
        return particle_frame
    
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
    """Create artistic overlay elements with phase-specific enhancements"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    time_factor = frame_index / total_frames
    
    # Define phase boundaries
    expansion_phase = 0.25
    organized_phase = 0.60
    return_phase = 0.15
    
    # Determine current phase
    if time_factor < expansion_phase:
        current_phase = "expansion"
        phase_progress = time_factor / expansion_phase
    elif time_factor < expansion_phase + organized_phase:
        current_phase = "organized"
        phase_progress = (time_factor - expansion_phase) / organized_phase
    else:
        current_phase = "return"
        phase_progress = (time_factor - expansion_phase - organized_phase) / return_phase
    
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
        # Phase-specific overlay enhancements
        
        if current_phase == "expansion":
            # Explosion burst effects
            alpha = int(120 + 80 * np.sin(phase_progress * 2 * np.pi))
            center_x, center_y = width // 2, height // 2
            
            # Radial burst lines
            for i in range(16):
                angle = i * (2 * math.pi / 16)
                burst_length = int(200 * phase_progress)
                start_x = center_x + int(20 * math.cos(angle))
                start_y = center_y + int(20 * math.sin(angle))
                end_x = center_x + int(burst_length * math.cos(angle))
                end_y = center_y + int(burst_length * math.sin(angle))
                
                draw.line([start_x, start_y, end_x, end_y], 
                         fill=(255, 255, 255, alpha), width=3)
            
            # Explosion sparkles
            for _ in range(30):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(2, 8)
                sparkle_alpha = int(alpha * random.uniform(0.5, 1.0))
                draw.ellipse([x-size, y-size, x+size, y+size], 
                           fill=(255, 255, 255, sparkle_alpha))
        
        elif current_phase == "organized":
            # Organized movement trails and formations
            alpha = int(80 + 60 * np.sin(phase_progress * 3 * np.pi))
            center_x, center_y = width // 2, height // 2
            
            # Spiral formation guides
            for spiral in range(3):
                spiral_points = []
                for i in range(20):
                    angle = i * 0.3 + phase_progress * 4 * math.pi + spiral * 2
                    radius = 50 + i * 8
                    x = center_x + int(radius * math.cos(angle))
                    y = center_y + int(radius * math.sin(angle))
                    spiral_points.append((x, y))
                
                # Draw spiral trail
                for i in range(len(spiral_points) - 1):
                    draw.line([spiral_points[i], spiral_points[i+1]], 
                             fill=(255, 255, 255, alpha), width=2)
            
            # Orbital rings
            for ring in range(3):
                radius = 80 + ring * 40
                ring_alpha = int(alpha * (1 - ring * 0.2))
                draw.ellipse([
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius
                ], outline=(255, 255, 255, ring_alpha), width=2)
            
            # Formation sparkles
            for _ in range(40):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(1, 6)
                sparkle_alpha = int(alpha * random.uniform(0.3, 0.8))
                
                # Colored sparkles for organized phase
                colors = [(255, 255, 255), (255, 200, 200), (200, 255, 200), (200, 200, 255)]
                color = random.choice(colors)
                draw.ellipse([x-size, y-size, x+size, y+size], 
                           fill=(*color, sparkle_alpha))
        
        else:  # return phase
            # Return journey effects
            alpha = int(100 + 50 * np.sin(phase_progress * 2 * np.pi))
            
            # Converging lines pointing toward original positions
            for _ in range(12):
                start_x = random.randint(0, width)
                start_y = random.randint(0, height)
                
                # Lines converge toward center (representing return)
                center_x, center_y = width // 2, height // 2
                direction_x = (center_x - start_x) * 0.3
                direction_y = (center_y - start_y) * 0.3
                
                end_x = int(start_x + direction_x)
                end_y = int(start_y + direction_y)
                
                draw.line([start_x, start_y, end_x, end_y], 
                         fill=(255, 255, 255, alpha), width=2)
            
            # Gentle glow effect for return
            center_x, center_y = width // 2, height // 2
            glow_radius = int(100 + 50 * np.sin(phase_progress * 3 * np.pi))
            glow_alpha = int(alpha * 0.4)
            
            for i in range(5):
                radius = glow_radius + i * 15
                current_alpha = max(10, glow_alpha - i * 8)
                draw.ellipse([
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius
                ], outline=(255, 255, 255, current_alpha), width=1)
            
            # Return sparkles - fewer and more gentle
            for _ in range(20):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(1, 4)
                sparkle_alpha = int(alpha * random.uniform(0.3, 0.7))
                draw.ellipse([x-size, y-size, x+size, y+size], 
                           fill=(255, 255, 255, sparkle_alpha))
    
    return overlay

def main():
    # Configuration - can be overridden by environment variables
    IMAGE_PATH = os.environ.get('PAINTING_INPUT_PATH', "IMG_7616.png")
    OUTPUT_VIDEO = os.environ.get('PAINTING_OUTPUT_PATH', "painting_3d_effect_premium.mp4")
    
    # Animation settings from web interface
    ANIMATION_DURATION = int(os.environ.get('ANIMATION_DURATION', 10))  # seconds
    ANIMATION_QUALITY = os.environ.get('ANIMATION_QUALITY', 'ultra')   # standard, high, ultra
    ARTISTIC_STYLE = os.environ.get('ANIMATION_STYLE', 'particle_powder')  # style selection
    
    print(f"🎨 Creating revolutionary particle animation")
    print(f"📸 Loading image: {IMAGE_PATH}")
    print(f"⏱️ Duration: {ANIMATION_DURATION} seconds")
    print(f"🎯 Quality: {ANIMATION_QUALITY}")
    print(f"🎭 Style: {ARTISTIC_STYLE}")
    
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
        
        # Optimize size based on quality setting
        if ANIMATION_QUALITY == 'standard':
            max_size = 800
        elif ANIMATION_QUALITY == 'high':
            max_size = 1000
        else:  # ultra
            max_size = 1200
            
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            print(f"📐 Resized to max {max_size}px for {ANIMATION_QUALITY} quality")
        
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
        
        # Calculate frames based on duration
        fps = 30
        num_frames = ANIMATION_DURATION * fps
        
        print(f"🎬 Generating {ARTISTIC_STYLE} animation...")
        print(f"📋 Animation settings:")
        print(f"   ⏱️ Duration: {ANIMATION_DURATION} seconds ({num_frames} frames)")
        print(f"   🎯 Quality: {ANIMATION_QUALITY}")
        print(f"   📐 Resolution: {w}x{h}")
        print("📋 Animation phases:")
        print("   🚀 Phase 1 (0-25%): Explosive expansion - particles break free from canvas")
        print("   🌀 Phase 2 (25-85%): Organized movement - spirals, orbits, and wave formations")
        print("   🏠 Phase 3 (85-100%): Return journey - particles return to original positions")
        print("   ✨ VIBRANT COLORS: Particles maintain bright colors throughout entire animation!")
        print()
        
        frames = []
        
        # Define phase boundaries
        expansion_end = int(num_frames * 0.25)
        organized_end = int(num_frames * 0.85)
        
        for i in range(num_frames):
            # Determine current phase
            if i < expansion_end:
                phase = "🚀 EXPANSION"
                phase_progress = (i / expansion_end) * 100
            elif i < organized_end:
                phase = "🌀 ORGANIZED"
                phase_progress = ((i - expansion_end) / (organized_end - expansion_end)) * 100
            else:
                phase = "🏠 RETURNING"
                phase_progress = ((i - organized_end) / (num_frames - organized_end)) * 100
            
            # Update progress less frequently for longer animations
            progress_interval = max(10, num_frames // 30)  # Show ~30 updates max
            if i % progress_interval == 0:
                print(f"✨ Frame {i+1:3d}/{num_frames} | {phase} | Progress: {phase_progress:5.1f}%")
            
            # Apply artistic style
            if hasattr(processor, ARTISTIC_STYLE):
                if ARTISTIC_STYLE == 'particle_powder':
                    artistic_frame = processor.particle_powder_style(img, depth_norm, i, num_frames)
                else:
                    artistic_frame = getattr(processor, ARTISTIC_STYLE)(img, depth_norm, i, num_frames)
            else:
                # Fallback to particle_powder if style not found
                artistic_frame = processor.particle_powder_style(img, depth_norm, i, num_frames)
            
            frame_img = Image.fromarray(artistic_frame)
            
            # Add artistic enhancement
            time_factor = i / num_frames
            
            # Dynamic saturation - boost colors during organized phase
            if expansion_end <= i < organized_end:
                saturation = 1.0 + 0.4 * np.sin(time_factor * 2 * np.pi)
            else:
                saturation = 1.0 + 0.2 * np.sin(time_factor * 2 * np.pi)
            
            enhancer = ImageEnhance.Color(frame_img)
            frame_img = enhancer.enhance(saturation)
            
            # Dynamic contrast - increase drama during expansion
            if i < expansion_end:
                contrast = 1.0 + 0.6 * np.sin(time_factor * 3 * np.pi)
            else:
                contrast = 1.0 + 0.3 * np.cos(time_factor * 1.5 * np.pi)
            
            enhancer = ImageEnhance.Contrast(frame_img)
            frame_img = enhancer.enhance(contrast)
            
            # Add overlay elements
            overlay = create_artistic_overlay(w, h, i, num_frames, ARTISTIC_STYLE)
            frame_img = Image.alpha_composite(frame_img.convert('RGBA'), overlay)
            frame_img = frame_img.convert('RGB')
            
            frames.append(frame_img)
        
        print("✓ All frames generated successfully!")
        print(f"🎞️ Total particles created: {len(processor.particle_system.particles) if processor.particle_system else 'N/A'}")
        
        # Export with quality-based settings
        print(f"🎞️ Exporting {ANIMATION_QUALITY} quality video...")
        
        # Quality settings
        if ANIMATION_QUALITY == 'standard':
            bitrate = "8000k"
            crf = "18"
        elif ANIMATION_QUALITY == 'high':
            bitrate = "15000k"
            crf = "14"
        else:  # ultra
            bitrate = "25000k"
            crf = "10"
        
        clip = ImageSequenceClip([np.array(f) for f in frames], fps=fps)
        
        clip.write_videofile(
            OUTPUT_VIDEO,
            codec="libx264",
            audio=False,
            bitrate=bitrate,
            ffmpeg_params=["-crf", crf, "-preset", "slow"]
        )
        
        print(f"🌟 REVOLUTIONARY particle animation created: {OUTPUT_VIDEO}")
        print(f"🎯 Settings: {ANIMATION_DURATION}s | {ANIMATION_QUALITY} quality | {ARTISTIC_STYLE} style")
        print(f"✨ VIBRANT PARTICLE TRANSFORMATION:")
        print(f"   🎨 Entire painting converted to bright, colorful particles")
        print(f"   🚀 Particles explode beyond canvas boundaries")
        print(f"   🌀 Organized formations: spirals, orbits, waves")
        print(f"   🏠 Perfect return to original positions AS PARTICLES")
        print(f"   💫 Three-phase animation with vibrant colors throughout!")
        print(f"   🌈 Colors never fade - particles stay bright and beautiful!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 