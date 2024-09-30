# members/process_mri.py
import os
import nibabel as nib
import numpy as np
import torch
import torch.nn.functional as F
import torch.nn as nn
import matplotlib.pyplot as plt
from monai.networks.nets import UNet
from monai.losses import DiceLoss

def load_and_transpose_nifti_image(file_path):
    nifti_image = nib.load(file_path)
    image_data = nifti_image.get_fdata()
    transposed_image_data = np.transpose(image_data, (3, 0, 1, 2))
    transposed_shape = transposed_image_data.shape
    return transposed_image_data, transposed_shape

def resize_image_batch(image_data, target_shape=(1, 4, 256, 256, 256)):
    image_tensor = torch.tensor(image_data, dtype=torch.float32).unsqueeze(0)
    resized_image_batch = F.interpolate(
        image_tensor, 
        size=target_shape[2:], 
        mode='trilinear', 
        align_corners=False
    )
    return resized_image_batch

def initialize_model():
    """
    Initialize the UNet model and load the pre-trained weights.

    Returns:
    - model (torch.nn.Module): The initialized model.
    - device (torch.device): The device to run the model on.
    """
    model = UNet(
        spatial_dims=3,
        in_channels=4,
        out_channels=5,
        channels=(16, 32, 64, 128, 256),
        strides=(2, 2, 2, 2)
    )
    device = torch.device("cpu")  # Change to "cuda" if you have a GPU
    model.to(device)
    
    # Construct the absolute path to the 'sc.pth' file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    weights_path = os.path.join(current_dir, 'sc.pth')
    
    model.load_state_dict(torch.load(weights_path))
    model.eval()
    return model, device

def infer(model, input_tensor, device):
    """
    Perform inference on the input tensor using the trained model.

    Parameters:
    - model (torch.nn.Module): The trained model.
    - input_tensor (torch.Tensor): The input tensor of shape [1, 4, 256, 256, 256].
    - device (torch.device): The device to run the inference on.

    Returns:
    - output_tensor (torch.Tensor): The model's output tensor containing the predicted segmentation.
    """
    input_tensor = input_tensor.to(device)
    with torch.no_grad():
        output_tensor = model(input_tensor)
    return output_tensor


def save_predicted_segmentation(predicted_output,output_path):

    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    predicted_labels = torch.argmax(predicted_output, dim=1, keepdim=True)
    predicted_labels_np = predicted_labels.cpu().numpy()
    predicted_labels_3d = predicted_labels_np[0, 0].astype(np.uint8)
    nifti_img = nib.Nifti1Image(predicted_labels_3d, affine=np.eye(4))
    nib.save(nifti_img, output_path)
    print(f"Predicted segmentations saved as '{output_path}'")

    # slice_index_axial=50, 
    # slice_index_sagittal=75,
    # slice_index_coronal=60
    # display_flair_groundtruth_predicted(output_path, slice_index_axial, slice_index_sagittal, slice_index_coronal)



# Example usage
# if __name__ == "__main__":
#     uploaded_file_path = 'path/to/your/nifti/file.nii.gz'  # Replace with your actual file path
#     transposed_image_data, transposed_shape = load_and_transpose_nifti_image(uploaded_file_path)
#     resized_image_batch = resize_image_batch(transposed_image_data)
#     model, device = initialize_model()
#     predicted_output = infer(model, resized_image_batch, device)
#     print("Predicted Output Shape:", predicted_output.shape)
#     save_predicted_segmentation(predicted_output)