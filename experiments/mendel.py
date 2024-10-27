import numpy as np
from PIL import Image
import colorsys

def mandelbrot(h, w, max_iter):
    # Create a complex plane
    y, x = np.ogrid[-1.4:1.4:h*1j, -2:0.8:w*1j]
    c = x + y*1j
    z = c
    divtime = max_iter + np.zeros(z.shape, dtype=int)

    # Calculate the Mandelbrot set
    for i in range(max_iter):
        z = z**2 + c
        diverge = z*np.conj(z) > 2**2  # radius = 2
        div_now = diverge & (divtime == max_iter)
        divtime[div_now] = i
        z[diverge] = 2  # avoid diverging too much

    return divtime

def create_mandelbrot_image(width=800, height=600, max_iter=100, output_file='mandelbrot.png'):
    # Generate the Mandelbrot set
    mandel = mandelbrot(height, width, max_iter)
    
    # Create an RGB image
    image = Image.new('RGB', (width, height))
    pixels = image.load()
    
    # Color mapping function
    def color_map(i, max_iter):
        if i == max_iter:
            return (0, 0, 0)  # Black for points in the set
        else:
            # Convert iterations to a color using HSV color space
            hue = i / max_iter
            saturation = 1.0
            value = 1.0 if i < max_iter else 0.0
            # Convert HSV to RGB
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            return tuple(int(255 * x) for x in rgb)
    
    # Fill the image with colors
    for x in range(width):
        for y in range(height):
            pixels[x, y] = color_map(mandel[y, x], max_iter)
    
    # Save the image
    image.save(output_file)
    return image

if __name__ == "__main__":
    # Create a high-resolution Mandelbrot set image
    image = create_mandelbrot_image(
        width=1920,
        height=1080,
        max_iter=150,
        output_file='mandelbrot_hd.png'
    )