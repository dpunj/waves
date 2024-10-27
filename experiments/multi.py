import numpy as np
from PIL import Image
import cmath
from scipy.signal import convolve2d
import os
from datetime import datetime

class CoastalVariationGenerator:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.max_iter = 100
        
        # Different interesting regions of the Mandelbrot set
        self.regions = [
            # Region 1: Classic coastline
            {
                'x_range': (-0.7485, -0.7445),
                'y_range': (0.1000, 0.1040),
                'bio_intensity': 1.0,
                'wave_intensity': 1.0,
                'name': 'classic_coast'
            },
            # Region 2: Rocky coastline
            {
                'x_range': (-0.7443, -0.7423),
                'y_range': (0.1315, 0.1335),
                'bio_intensity': 0.7,
                'wave_intensity': 1.3,
                'name': 'rocky_coast'
            },
            # Region 3: Gentle slopes
            {
                'x_range': (-0.7424, -0.7404),
                'y_range': (0.1366, 0.1386),
                'bio_intensity': 1.4,
                'wave_intensity': 0.8,
                'name': 'gentle_slopes'
            },
            # Region 4: Complex patterns
            {
                'x_range': (-0.7418, -0.7398),
                'y_range': (0.1888, 0.1908),
                'bio_intensity': 1.2,
                'wave_intensity': 1.1,
                'name': 'complex_patterns'
            },
            # Region 5: Deep bays
            {
                'x_range': (-0.7452, -0.7432),
                'y_range': (0.1102, 0.1122),
                'bio_intensity': 0.9,
                'wave_intensity': 1.5,
                'name': 'deep_bays'
            }
        ]
        
    def get_mandelbrot_value(self, c, max_iter):
        z = 0
        for n in range(max_iter):
            if abs(z) > 2:
                smooth_val = n + 1 - np.log(np.log2(abs(z)))
                return smooth_val / max_iter
            z = z * z + c
        return 1.0

    def predict_wave_patterns(self, coastline_points, wave_intensity):
        gradient = np.gradient(coastline_points)
        curvature = np.gradient(gradient)
        wave_map = np.zeros((self.height, self.width))
        
        for x in range(self.width):
            coast_y = int(coastline_points[x])
            wave_strength = abs(curvature[x]) * 2 * wave_intensity
            
            for y in range(coast_y, min(coast_y + 150, self.height)):
                distance = y - coast_y
                wave_probability = wave_strength * np.exp(-distance / (50 * wave_intensity))
                wave_probability *= (1 + 0.5 * np.sin(distance * 0.1 + x * 0.05))
                wave_map[y, x] = wave_probability
        
        return wave_map

    def predict_biosphere(self, coastline_points, bio_intensity):
        bio_map = np.zeros((self.height, self.width))
        
        for x in range(self.width):
            coast_y = int(coastline_points[x])
            
            # Shallow water zone
            for y in range(coast_y, min(coast_y + int(50 * bio_intensity), self.height)):
                distance = y - coast_y
                bio_probability = np.exp(-distance / (30 * bio_intensity))
                bio_map[y, x] = bio_probability
            
            # Beach ecosystem
            for y in range(max(0, coast_y - int(20 * bio_intensity)), coast_y):
                distance = coast_y - y
                bio_probability = 0.5 * np.exp(-distance / (10 * bio_intensity))
                bio_map[y, x] = bio_probability
        
        kernel = np.ones((5, 5)) / 25
        bio_map = convolve2d(bio_map, kernel, mode='same')
        return bio_map

    def generate_variation(self, region):
        x_min, x_max = region['x_range']
        y_min, y_max = region['y_range']
        
        # Generate coastline
        coastline_points = []
        for x in range(self.width):
            real = x_min + (x / self.width) * (x_max - x_min)
            best_y = None
            best_val = float('inf')
            
            for y_pixel in range(self.height):
                y = y_min + (y_pixel / self.height) * (y_max - y_min)
                c = complex(real, y)
                val = self.get_mandelbrot_value(c, self.max_iter)
                if abs(val - 0.5) < best_val:
                    best_val = abs(val - 0.5)
                    best_y = y_pixel
            
            coastline_points.append(best_y)
        
        # Smooth coastline
        coastline_points = np.array(coastline_points)
        window_size = 15
        kernel = np.ones(window_size) / window_size
        coastline_points = np.convolve(coastline_points, kernel, mode='same')
        
        # Scale coastline
        coastline_points = coastline_points - np.min(coastline_points)
        coastline_points = (coastline_points / np.max(coastline_points)) * (self.height * 0.6)
        coastline_points += self.height * 0.2
        
        # Generate prediction maps
        wave_map = self.predict_wave_patterns(coastline_points, region['wave_intensity'])
        bio_map = self.predict_biosphere(coastline_points, region['bio_intensity'])
        
        # Create image
        image_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        for y in range(self.height):
            for x in range(self.width):
                coast_y = int(coastline_points[x])
                
                if y < coast_y:  # Land
                    base_color = [230, 220, 180]
                    bio_intensity = bio_map[y, x] * 100 * region['bio_intensity']
                    image_array[y, x] = [
                        max(0, min(255, base_color[0] - bio_intensity)),
                        max(0, min(255, base_color[1] + bio_intensity)),
                        max(0, min(255, base_color[2] - bio_intensity))
                    ]
                else:  # Water
                    depth_factor = (y - coast_y) / (self.height - coast_y)
                    base_blue = 255 - depth_factor * 100
                    base_green = 200 - depth_factor * 100
                    
                    wave_intensity = wave_map[y, x] * 100 * region['wave_intensity']
                    bio_intensity = bio_map[y, x] * 100 * region['bio_intensity']
                    
                    image_array[y, x] = [
                        0,
                        max(0, min(255, base_green + bio_intensity - wave_intensity * 0.5)),
                        max(0, min(255, base_blue - wave_intensity + bio_intensity * 0.3))
                    ]
        
        return Image.fromarray(image_array)

def generate_multiple_variations(output_dir='coastal_variations', width=800, height=600):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Initialize generator
    generator = CoastalVariationGenerator(width, height)
    
    # Generate and save each variation
    variations = []
    for region in generator.regions:
        image = generator.generate_variation(region)
        filename = f"{region['name']}_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        image.save(filepath)
        variations.append({
            'name': region['name'],
            'path': filepath,
            'image': image
        })
        
    return variations

if __name__ == "__main__":
    # Generate high-resolution variations
    variations = generate_multiple_variations(
        width=1920,
        height=1080,
        output_dir='coastal_variations'
    )
    
    print("Generated variations:")
    for var in variations:
        print(f"- {var['name']}: {var['path']}")