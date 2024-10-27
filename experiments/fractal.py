import numpy as np
from PIL import Image
import random

class CoastlineGenerator:
    def __init__(self, size=513):
        # Size must be 2^n + 1
        self.size = size
        self.heightmap = np.zeros((size, size))
        self.roughness = 0.6
        self.sea_level = 0.4  # Adjust this to control land/water ratio
    
    def _get_random_offset(self, current_range):
        # Decreasing randomness as we get into finer details
        return (random.random() - 0.5) * current_range * self.roughness
    
    def diamond_square(self):
        # Initialize corners with random values
        self.heightmap[0, 0] = random.random()
        self.heightmap[0, -1] = random.random()
        self.heightmap[-1, 0] = random.random()
        self.heightmap[-1, -1] = random.random()
        
        step_size = self.size - 1
        range_size = 1.0
        
        while step_size > 1:
            half_step = step_size // 2
            
            # Diamond step
            for y in range(0, self.size - 1, step_size):
                for x in range(0, self.size - 1, step_size):
                    # Average of corners
                    avg = (self.heightmap[y, x] +
                          self.heightmap[y + step_size, x] +
                          self.heightmap[y, x + step_size] +
                          self.heightmap[y + step_size, x + step_size]) / 4.0
                    
                    # Set center point
                    self.heightmap[y + half_step, x + half_step] = (
                        avg + self._get_random_offset(range_size)
                    )
            
            # Square step
            for y in range(0, self.size, half_step):
                for x in range((y + half_step) % step_size, self.size, step_size):
                    count = 0
                    avg = 0
                    
                    # Check all four directions
                    if y >= half_step:  # Top
                        avg += self.heightmap[y - half_step, x]
                        count += 1
                    if y + half_step < self.size:  # Bottom
                        avg += self.heightmap[y + half_step, x]
                        count += 1
                    if x >= half_step:  # Left
                        avg += self.heightmap[y, x - half_step]
                        count += 1
                    if x + half_step < self.size:  # Right
                        avg += self.heightmap[y, x + half_step]
                        count += 1
                    
                    avg /= count
                    self.heightmap[y, x] = avg + self._get_random_offset(range_size)
            
            step_size //= 2
            range_size *= 0.5
    
    def generate_coastline(self):
        self.diamond_square()
        
        # Normalize values to 0-1 range
        min_val = np.min(self.heightmap)
        max_val = np.max(self.heightmap)
        self.heightmap = (self.heightmap - min_val) / (max_val - min_val)
        
        # Create RGB image
        image_array = np.zeros((self.size, self.size, 3), dtype=np.uint8)
        
        # Color mapping
        for y in range(self.size):
            for x in range(self.size):
                height = self.heightmap[y, x]
                if height < self.sea_level:
                    # Deep to shallow water gradient
                    depth_factor = height / self.sea_level
                    blue = int(150 + 105 * depth_factor)  # 150-255
                    green = int(150 + 75 * depth_factor)  # 150-225
                    image_array[y, x] = [0, green, blue]
                else:
                    # Land elevation gradient
                    land_factor = (height - self.sea_level) / (1 - self.sea_level)
                    green = int(180 - 60 * land_factor)  # Darker green for higher elevation
                    image_array[y, x] = [100 + int(50 * land_factor), green, 50]
        
        return Image.fromarray(image_array)

def create_coastline_image(size=513, output_file='coastline.png'):
    # Create and generate the coastline
    generator = CoastlineGenerator(size)
    image = generator.generate_coastline()
    
    # Save the image
    image.save(output_file)
    return image

if __name__ == "__main__":
    # Generate a coastline image
    image = create_coastline_image(
        size=513,  # Must be 2^n + 1 (e.g., 129, 257, 513, 1025)
        output_file='coastline.png'
    )