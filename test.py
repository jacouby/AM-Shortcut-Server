from PIL import Image
import imagehash

def compare_images_phash(image1_path, image2_path):
    # Open the images
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)
    
    # Compute the perceptual hash for both images
    hash1 = imagehash.phash(img1)
    hash2 = imagehash.phash(img2)
    
    # Compare the hashes
    return hash1 - hash2

# Example usage
image1_path = 'image1.jpeg'
image2_path = 'image2.jpeg'
 
hash_difference = compare_images_phash(image1_path, image2_path)
print(f"Perceptual hash difference: {hash_difference}")
if hash_difference == 0:
    print("The images are the same.")
else:
    print("The images are different.")
