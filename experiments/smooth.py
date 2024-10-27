import numpy as np
from PIL import Image
import cmath

class MandelbrotCoastGenerator:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.max_iter = 100
        # Focus on an interesting part of the Mandelbrot set boundary
        self.x_min, self.x_max = -0.7485, -0.7445
        self.y_min, self.y_max = 0.1000, 0.1040
        
    def get_smooth_value(self, c, max_iter):
        z = 0
        for n in range(max_iter):
            if abs(z) > 2:
                # Smooth coloring formula
                smooth_val = n + 1 - np.log(np.log2(abs(z)))
                return smooth_val / max_iter
            z = z * z + c
        return 1.0

    def generate_boundary_points(self):
        """Generate points along the Mandelbrot set boundary"""
        points = []
        
        for x in range(self.width):
            # Map x coordinate to Mandelbrot set coordinate
            real = self.x_min + (x / self.width) * (self.x_max - self.x_min)
            
            # Find the boundary point for this x coordinate
            best_y = None
            best_val = float('inf')
            
            # Search for boundary point
            for y_pixel in range(self.height):
                y = self.y_min + (y_pixel / self.height) * (self.y_max - self.y_min)
                c = complex(real, y)
                val = self.get_smooth_value(c, self.max_iter)
                
                # Looking for values close to 0.5 which typically represents the boundary
                if abs(val - 0.5) < best_val:
                    best_val = abs(val - 0.5)
                    best_y = y_pixel
            
            points.append(best_y)
            
        # Smooth the points using a moving average
        smoothed_points = np.array(points)
        window_size = 15
        kernel = np.ones(window_size) / window_size
        smoothed_points = np.convolve(smoothed_points, kernel, mode='same')
        
        return smoothed_points

    def generate_coastline(self):
        # Create image array
        image_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Generate the coastline points
        coastline_points = self.generate_boundary_points()
        
        # Scale the coastline to use more of the image height
        coastline_points = coastline_points - np.min(coastline_points)
        coastline_points = (coastline_points / np.max(coastline_points)) * (self.height * 0.6)
        coastline_points += self.height * 0.2  # Center vertically
        
        # Draw the image
        for y in range(self.height):
            for x in range(self.width):
                coast_y = int(coastline_points[x])
                
                if y < coast_y - 2:  # Land (top)
                    # Sandy beach gradient
                    sand_gradient = 1 - (coast_y - y) / (self.height * 0.5)
                    sand_color = [
                        min(255, int(230 + sand_gradient * 25)),  # R
                        min(255, int(220 + sand_gradient * 20)),  # G
                        min(255, int(180 + sand_gradient * 20))   # B
                    ]
                    image_array[y, x] = sand_color
                    
                elif y < coast_y + 4:  # Surf line
                    # Create a gradient for the foam
                    foam_dist = abs(y - coast_y)
                    foam_intensity = int(255 * (1 - foam_dist / 4))
                    image_array[y, x] = [foam_intensity] * 3
                    
                else:  # Ocean (bottom)
                    # Ocean depth gradient
                    depth_factor = (y - coast_y) / (self.height - coast_y)
                    depth_factor = min(1.0, depth_factor * 1.5)  # Intensify the gradient
                    
                    # Create wave patterns based on distance from shore
                    wave_factor = np.sin(y * 0.1 + x * 0.05) * 0.1
                    wave_factor *= max(0, 1 - (y - coast_y) / 100)  # Fade waves with depth
                    
                    blue = int(255 - depth_factor * 100 + wave_factor * 50)
                    green = int(200 - depth_factor * 100 + wave_factor * 30)
                    
                    image_array[y, x] = [0, 
                                       max(0, min(255, green)),
                                       max(0, min(255, blue))]

        return Image.fromarray(image_array)

def create_mandelbrot_coast(width=800, height=600, output_file='mandelbrot_coast.png'):
    # Create and generate the coastline
    generator = MandelbrotCoastGenerator(width, height)
    image = generator.generate_coastline()
    
    # Save the image
    image.save(output_file)
    return image

if __name__ == "__main__":
    # Generate a high-resolution coastline
    image = create_mandelbrot_coast(
        width=1920,
        height=1080,
        output_file='mandelbrot_coast.png'
    )