import cv2

def compare_images_orb(image1_path, image2_path):
    # Read the images using OpenCV
    img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)
    
    # Initiate ORB detector
    orb = cv2.ORB_create()
    
    # Find the keypoints and descriptors with ORB
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    
    # Create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    # Match descriptors
    matches = bf.match(des1, des2)
    
    # Sort them in the order of their distance
    matches = sorted(matches, key=lambda x: x.distance)
    
    # Calculate the average distance of matches
    avg_distance = sum(match.distance for match in matches) / len(matches)
    
    return avg_distance

# Example usage
image1_path = './images/2a.jpeg'
image2_path = './images/2s.jpeg'

avg_distance = compare_images_orb(image1_path, image2_path)
print(f"Average ORB keypoint match distance: {avg_distance}")
if avg_distance < 10:  # Threshold depends on the application
    print("The images are very similar.")
else:
    print("The images are different.")
