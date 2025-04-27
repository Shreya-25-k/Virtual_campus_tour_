import cv2
import os
import logging
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_images(input_folder):
    """Load images from the specified folder."""
    image_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]
    image_files.sort()

    images = [cv2.imread(image) for image in image_files]
    if len(images) < 2:
        logging.error(f"Not enough images in {input_folder}. Need at least 2.")
        return None
    return images

def resize_images(images):
    """Resize images to the largest dimensions among them, padding to maintain aspect ratio."""
    max_height = max(image.shape[0] for image in images)
    max_width = max(image.shape[1] for image in images)

    resized_images = []
    for img in images:
        aspect_ratio = img.shape[1] / img.shape[0]
        if aspect_ratio > 1:  # Landscape
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:  # Portrait or square
            new_height = max_height
            new_width = int(max_height * aspect_ratio)

        resized_img = cv2.resize(img, (new_width, new_height))
        delta_w = max_width - new_width
        delta_h = max_height - new_height
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)

        # Pad image with black borders
        padded_img = cv2.copyMakeBorder(resized_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        resized_images.append(padded_img)

    return resized_images

def detect_keypoints_and_descriptors(images):
    """Detect keypoints and descriptors for a list of images."""
    detector = cv2.SIFT_create()
    keypoints_descriptors = [detector.detectAndCompute(img, None) for img in images]
    return keypoints_descriptors

def match_keypoints(descriptors):
    """Match keypoints between all sets of descriptors using FLANN."""
    index_params = dict(algorithm=1, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    good_matches = []
    for i in range(len(descriptors) - 1):
        matches = flann.knnMatch(descriptors[i][1], descriptors[i + 1][1], k=2)
        good = [m for m, n in matches if m.distance < 0.7 * n.distance]
        good_matches.append(good)
        logging.info(f"Number of good matches between image {i + 1} and image {i + 2}: {len(good)}")

    return good_matches

def stitch_images(images):
    """Stitch images together and return the result."""
    stitcher = cv2.Stitcher_create()
    stitcher.setPanoConfidenceThresh(0.7)
    status, panorama = stitcher.stitch(images)

    if status == cv2.Stitcher_OK:
        return panorama
    else:
        logging.error(f"Stitching failed with status code {status}")
        return None

def crop_panorama(panorama):
    """Crop black borders from the panorama more aggressively."""
    # Convert image to grayscale
    gray = cv2.cvtColor(panorama, cv2.COLOR_BGR2GRAY)
    
    # Find non-zero rows and columns
    rows = np.any(gray > 0, axis=1)
    cols = np.any(gray > 0, axis=0)
    
    # Get the bounding box of non-zero regions
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    # Crop the image
    cropped = panorama[rmin:rmax+1, cmin:cmax+1]
    
    return cropped

def process_folder(folder, output_file):
    """Process a folder of images to create a panorama."""
    logging.info(f"Processing {folder}...")
    images = load_images(folder)
    if images is None:
        return False

    resized_images = resize_images(images)
    keypoints_descriptors = detect_keypoints_and_descriptors(resized_images)

    # Match keypoints for all pairs of images
    good_matches = match_keypoints(keypoints_descriptors)

    # Check if there are enough good matches
    if any(len(matches) < 10 for matches in good_matches):
        logging.error("Not enough good matches to perform stitching.")
        return False

    # Stitch images
    panorama = stitch_images(resized_images)
    if panorama is not None:
        # Crop the panorama to remove black borders
        panorama_cropped = crop_panorama(panorama)

        cv2.imwrite(output_file, panorama_cropped)
        logging.info(f"Panorama saved to {output_file}")
        return True
    return False

if __name__ == "__main__":
    # Ensure the output directory exists
    os.makedirs("images/panoramas", exist_ok=True)

    folders = {
        "images/room1": "images/panoramas/mainentrance.jpg",
        "images/room2": "images/panoramas/Mainblock.jpg",
        "images/room3": "images/panoramas/panorama3.jpg",
        "images/room4": "images/panoramas/panorama4.jpg",
        "images/room5": "images/panoramas/panorama5.jpg",
        "images/room6": "images/panoramas/panorama6.jpg",
        "images/room6_1": "images/panoramas/panorama6_1.jpg",
        "images/room7": "images/panoramas/panorama7.jpg",
    }

    for folder, output in folders.items():
        if not process_folder(folder, output):
            logging.error(f"Failed to create panorama for {folder}")