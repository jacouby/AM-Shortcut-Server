from PIL import Image, ImageChops

def compare_images(image1_path, image2_path):
    # Open the images
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)
    
    # Convert images to grayscale (optional, for more efficient comparison)
    img1 = img1.convert('L')
    img2 = img2.convert('L')
    
    # Check if images have the same size
    if img1.size != img2.size:
        return False
    
    # Get the difference between the two images
    diff = ImageChops.difference(img1, img2)
    
    # Check if there are any non-zero pixels in the difference
    if diff.getbbox():
        return False
    else:
        return True

# Example usage
image1_path = 'image1.jpg'
image2_path = 'image2.jpg'

if compare_images(image1_path, image2_path):
    print("The images are the same.")
else:
    print("The images are different.")
