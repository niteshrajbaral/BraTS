#members/Display_output.py

import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
from matplotlib.colors import Normalize
import os
import imageio

def resample_image(image, target_shape):
    """
    Resamples the input image to match the target shape.
    """
    zoom_factors = [t / s for t, s in zip(target_shape, image.shape)]
    return zoom(image, zoom_factors, order=1)  # Using linear interpolation


def apply_color_map(predicted_slice):
    """
    Apply a color map to the predicted slice to make the segmentation colorful.

    Parameters:
    - predicted_slice (numpy.ndarray): The predicted segmentation slice.

    Returns:
    - color_mapped_slice (numpy.ndarray): The color-mapped segmentation slice.
    """
    # Normalize the predicted slice to the range [0, 1]
    norm = Normalize(vmin=predicted_slice.min(), vmax=predicted_slice.max())
    normalized_slice = norm(predicted_slice)

    # Apply a color map (e.g., 'viridis')
    color_mapped_slice = plt.cm.viridis(normalized_slice)

    # Convert to RGB format
    color_mapped_slice = (color_mapped_slice[:, :, :3] * 255).astype(np.uint8)

    return color_mapped_slice

def display_flair_groundtruth_predicted(path_array, slice_index_axial, slice_index_sagittal, slice_index_coronal,user_name,name):
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    views = ["Axial", "Sagittal", "Coronal"]
    modalities = ["(a) FLAIR Image", "(b) Predicted Segmentation"]

    # flair_image = None
    # predicted_segmentation = None

    # Load the images
     # Load the images
    for i, path in enumerate(path_array):
        if not os.path.isfile(path):
            print(f"Error: The path {path} is not a valid file.")
            continue

        try:
            image = nib.load(path).get_fdata()
            print(f"Shape of image at path {path}: {image.shape}")
        except Exception as e:
            print(f"Error loading image at path {path}: {e}")
            continue
        
        if i == 0:  # FLAIR image
            # Resample to (240, 240, 240, 4)
            flair_image = resample_image(image, (240, 240, 240, 4))
        elif i == 1:  # Predicted segmentation
            # Resample to (240, 240, 240)
            predicted_segmentation = resample_image(image, (240, 240, 240))

    if flair_image is None or predicted_segmentation is None:
        print("Error: Could not load FLAIR image or predicted segmentation.")
        return
    # Ensure the output directory exists
    output_dir = f'./media/inference/{user_name}'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Save each slice as an image and collect the file paths
    image_paths = []
    for slice_index in range(predicted_segmentation.shape[2]):
        flair_slice = flair_image[:, :, slice_index]
        predicted_slice = predicted_segmentation[:, :, slice_index]

        fig, axes = plt.subplots(1, 2, figsize=(10, 5))

        axes[0].imshow(flair_slice, cmap='gray')
        axes[0].set_title(f"FLAIR - Slice {slice_index}")
        axes[0].axis('off')

        # Apply color map to the predicted slice
        color_mapped_predicted_slice = apply_color_map(predicted_slice)

        axes[1].imshow(color_mapped_predicted_slice)
        axes[1].set_title(f"Predicted - Slice {slice_index}")
        axes[1].axis('off')

        # Save the figure
        file_name = f'{name}_slice_{slice_index}.png'
        output_path = os.path.join(output_dir, file_name)
        plt.savefig(output_path)
        plt.close()
        image_paths.append(output_path)
        print(f"Slice image saved to: {output_path}")

    # Create a GIF from the saved images
    gif_path = os.path.join(output_dir, f'{name}_inference.gif')
    with imageio.get_writer(gif_path, mode='I', duration=0.1) as writer:
        for image_path in image_paths:
            image = imageio.imread(image_path)
            writer.append_data(image)
    print(f"Inference GIF saved to: {gif_path}")

# Example paths
# path_array = [
#     '../media/inference/train_compact_images/BraTS2021_00110_stacked.nii.gz',  # FLAIR Image
#     '../media/inference/train_compact_labels/BraTS2021_00110.nii.gz',          # Ground Truth
#     '../media/inference/predicted_segmentations.nii.gz'                         # Predicted Segmentation
# ]

