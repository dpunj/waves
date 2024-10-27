import numpy as np
from PIL import Image
import cmath
from scipy.signal import convolve2d

class CoastalEcosystemPredictor:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.max_iter = 100
        # Focus on an interesting part of the Mandelbrot set boundary
        self.x_min, self.x_max = -0.7485, -0.7445
        self.y_min, self.y_max = 0.1000, 0.1040
        
    def get_mandelbrot_value(self, c, max_iter):
        z = 0
        for n in range(max_iter):
            if abs(z) > 2:
                # Smooth coloring formula
                smooth_val = n + 1 - np.log(np.log2(abs(z)))
                return smooth_val / max_iter
            z = z * z + c
        return 1.0

    def predict_wave_patterns(self, coastline_points):
        """Predict wave patterns based on coastline geometry"""
        # Calculate coastline gradient
        gradient = np.gradient(coastline_points)
        # Calculate curvature
        curvature = np.gradient(gradient)
        
        # Initialize wave probability map
        wave_map = np.zeros((self.height, self.width))
        
        for x in range(self.width):
            coast_y = int(coastline_points[x])
            
            # Wave formation is more likely in areas of high curvature
            wave_intensity = abs(curvature[x]) * 2
            
            # Create wave probability distribution
            for y in range(coast_y, min(coast_y + 150, self.height)):
                distance = y - coast_y
                # Wave probability decreases with distance from shore
                wave_probability = wave_intensity * np.exp(-distance / 50)
                # Add some periodic variation
                wave_probability *= (1 + 0.5 * np.sin(distance * 0.1 + x * 0.05))
                wave_map[y, x] = wave_probability
        
        return wave_map

    def predict_biosphere(self, coastline_points):
        """Predict biological activity zones"""
        bio_map = np.zeros((self.height, self.width))
        
        for x in range(self.width):
            coast_y = int(coastline_points[x])
            
            # Shallow water zone (highest biological activity)
            for y in range(coast_y, min(coast_y + 50, self.height)):
                distance = y - coast_y
                # Biological activity peaks in shallow waters
                bio_probability = np.exp(-distance / 30)
                bio_map[y, x] = bio_probability
            
            # Beach ecosystem
            for y in range(max(0, coast_y - 20), coast_y):
                distance = coast_y - y
                # Beach biological activity
                bio_probability = 0.5 * np.exp(-distance / 10)
                bio_map[y, x] = bio_probability
        
        # Smooth the biological activity map
        kernel = np.ones((5, 5)) / 25
        bio_map = convolve2d(bio_map, kernel, mode='same')
        
        return bio_map

    def generate_prediction_map(self):
        # Generate base coastline
        coastline_points = []
        for x in range(self.width):
            real = self.x_min + (x / self.width) * (self.x_max - self.x_min)
            best_y = None
            best_val = float('inf')
            
            for y_pixel in range(self.height):
                y = self.y_min + (y_pixel / self.height) * (self.y_max - self.y_min)
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
        wave_map = self.predict_wave_patterns(coastline_points)
        bio_map = self.predict_biosphere(coastline_points)
        
        # Create final image
        image_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        for y in range(self.height):
            for x in range(self.width):
                coast_y = int(coastline_points[x])
                
                if y < coast_y:  # Land
                    base_color = [230, 220, 180]  # Sandy beach
                    # Add green tint for biological activity
                    bio_intensity = bio_map[y, x] * 100
                    image_array[y, x] = [
                        max(0, min(255, base_color[0] - bio_intensity)),
                        max(0, min(255, base_color[1] + bio_intensity)),
                        max(0, min(255, base_color[2] - bio_intensity))
                    ]
                else:  # Water
                    # Base ocean color
                    depth_factor = (y - coast_y) / (self.height - coast_y)
                    base_blue = 255 - depth_factor * 100
                    base_green = 200 - depth_factor * 100
                    
                    # Add wave patterns (dark blue)
                    wave_intensity = wave_map[y, x] * 100
                    
                    # Add biological activity (green tint)
                    bio_intensity = bio_map[y, x] * 100
                    
                    image_array[y, x] = [
                        0,
                        max(0, min(255, base_green + bio_intensity - wave_intensity * 0.5)),
                        max(0, min(255, base_blue - wave_intensity + bio_intensity * 0.3))
                    ]
        
        return Image.fromarray(image_array)

def create_ecosystem_prediction(width=800, height=600, output_file='coastal_ecosystem.png'):
    predictor = CoastalEcosystemPredictor(width, height)
    image = predictor.generate_prediction_map()
    image.save(output_file)
    return image

if __name__ == "__main__":
    image = create_ecosystem_prediction(
        width=1920,
        height=1080,
        output_file='coastal_ecosystem.png'
    )