# members/utils.py
import torch
import nibabel as nib
import numpy as np
from .nn_model import YourModel  # Import your model architecture

def load_model():
    model = YourModel()  # Initialize the model
    model_path = 'model/model.pth'
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()  # Set the model to evaluation mode
    return model

def predict_nifti(nifti_file_path):
    model = load_model()
    # Load and preprocess your NIfTI file
    nifti_data = nib.load(nifti_file_path).get_fdata()
    # Ensure your data is in the correct format, e.g., torch tensor
    input_data = torch.tensor(nifti_data).unsqueeze(0).unsqueeze(0).float()
    with torch.no_grad():
        prediction = model(input_data)
    # Post-process the prediction as needed
    # Convert prediction to NIfTI image if required
    result_img = nib.Nifti1Image(prediction.numpy(), affine=np.eye(4))
    return result_img
