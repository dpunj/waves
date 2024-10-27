import numpy as np
from PIL import Image
import random

class PerlinNoiseGenerator:
    def __init__(self):
        # Generate permutation array
        self.p = list(range(256))
        random.shuffle(self.p)
        self.p += self.p

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, t, a, b):
        return a + t * (b - a)

    def grad(self, hash, x):
        h = hash & 15
        grad = 1 + (h & 7)  # Gradient value between 1 and 8
        if h & 8:
            grad = -grad  # Random sign
        return grad * x  # Compute the dot product

    def noise(self, x):
        # Integer part of x
        X = int(x) & 255
        # Fractional part of x
        x -= int(x)
        # Fade curve
        u = self.fade(x)
        # Hash coordinates of the point
        A = self.p[X]
        B = self.p[X + 1]
        # And add blended results
        return self.lerp(u, self.grad(A, x), self.grad(B, x - 1))

class SurfCoastGenerator:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.perlin = PerlinNoiseGenerator()
        
    def generate_coastline(self):
        # Create image array
        image_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Generate the main coastline curve using Perlin noise
        coastline_points = []
        scale = 0.02  # Adjust this to change the frequency of the curves
        amplitude = self.height * 0.15  # Adjust this to change the height of the curves
        base_height = self.height * 0.5  # Middle of the image
        
        for x in range(self.width):
            # Generate smoother coastline using multiple octaves of Perlin noise
            noise_val = 0
            for octave in range(4):
                noise_val += (1 / (2 ** octave)) * self.perlin.noise(x * scale * (2 ** octave))
            y = int(base_height + amplitude * noise_val)
            coastline_points.append(y)
        
        # Draw the image
        for y in range(self.height):
            for x in range(self.width):
                coast_y = coastline_points[x]
                
                if y < coast_y - 2:  # Land (top)
                    # Sandy beach color
                    sand_gradient = 1 - (coast_y - y) / (self.height * 0.5)
                    sand_color = [
                        min(255, int(220 + sand_gradient * 35)),  # R
                        min(255, int(210 + sand_gradient * 30)),  # G
                        min(255, int(170 + sand_gradient * 30))   # B
                    ]
                    image_array[y, x] = sand_color
                    
                elif y < coast_y + 2:  # Surf line
                    # White foam
                    foam_intensity = random.randint(200, 255)
                    image_array[y, x] = [foam_intensity] * 3
                    
                else:  # Ocean (bottom)
                    # Ocean depth gradient
                    depth_factor = (y - coast_y) / (self.height - coast_y)
                    blue = int(255 - depth_factor * 100)  # Darker blue as it gets deeper
                    green = int(200 - depth_factor * 100)
                    image_array[y, x] = [0, green, blue]

        # Add wave details
        self._add_wave_details(image_array, coastline_points)
        
        return Image.fromarray(image_array)
    
    def _add_wave_details(self, image_array, coastline_points):
        # Add wave patterns in the water
        for x in range(self.width):
            coast_y = coastline_points[x]
            wave_range = 100  # How far from the coast to draw waves
            
            for offset in range(10, wave_range, 20):  # Multiple wave lines
                wave_y = coast_y + offset
                if wave_y >= self.height:
                    continue
                    
                # Create wave pattern using Perlin noise
                wave_noise = self.perlin.noise(x * 0.05 + offset * 0.1) * 5
                wave_y = int(wave_y + wave_noise)
                
                if 0 <= wave_y < self.height:
                    # Draw subtle wave lines
                    for dy in range(-1, 2):
                        y = wave_y + dy
                        if 0 <= y < self.height:
                            current_color = image_array[y, x]
                            # Add a slightly lighter blue color for the wave
                            wave_color = [
                                current_color[0],
                                min(255, current_color[1] + 20),
                                min(255, current_color[2] + 30)
                            ]
                            image_array[y, x] = wave_color

def create_surf_coast(width=800, height=600, output_file='surf_coast.png'):
    # Create and generate the coastline
    generator = SurfCoastGenerator(width, height)
    image = generator.generate_coastline()
    
    # Save the image
    image.save(output_file)
    return image

if __name__ == "__main__":
    # Generate a surf coast image
    image = create_surf_coast(
        width=1920,
        height=1080,
        output_file='surf_coast.png'
    )