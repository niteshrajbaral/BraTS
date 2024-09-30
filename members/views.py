# members/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import MRIUploadForm

from .Display_output import display_flair_groundtruth_predicted
# from .utils import predict_nifti, display_flair_groundtruth_predicted

# for signup, login, and logout
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .process_mri import (
    load_and_transpose_nifti_image,
    resize_image_batch,
    initialize_model,
    infer,
    save_predicted_segmentation
)
from .Display_output import display_flair_groundtruth_predicted
# for saving the result image
import os
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np


# @login_required(login_url='/login/')
def home(request):
    if request.method == 'POST':
        form = MRIUploadForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            nifti_file = form.cleaned_data['nifti_file']  # Ensure this matches the form field name

            try:
                # Ensure the uploads directory exists
                uploads_dir = './media/nifti_files'
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)

                # Save the uploaded file
                file_path = os.path.join(uploads_dir, nifti_file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in nifti_file.chunks():
                        destination.write(chunk)

                # Debugging statement to check the saved file path
                print(f"File saved to: {file_path}")

                # Perform inference on the uploaded file
                transposed_image_data, transposed_shape = load_and_transpose_nifti_image(file_path)
                resized_image_batch = resize_image_batch(transposed_image_data)
                model, device = initialize_model()
                predicted_output = infer(model, resized_image_batch, device)
                print("Predicted Output Shape:", predicted_output.shape)

                             
                # Save the predicted segmentation
                username = request.user.username  # Get the username from the request object
                predicted_segmentation_path = f'./media/inference/{username}/{name}_predicted_segmentations.nii.gz'
                save_predicted_segmentation(predicted_output, predicted_segmentation_path)

                path_array = [file_path, predicted_segmentation_path]
                display_flair_groundtruth_predicted(path_array, 50, 75, 60,username,name)

                # Provide the path to the result image for display
                result_img_path = f'./media/inference/{username}/{name}_inference.gif'
                return render(request, 'result.html', {'result_img_path': result_img_path, 'name':name})
            except Exception as e:
                # Handle exceptions and provide feedback
                form.add_error(None, f"An error occurred: {e}")
    else:
        form = MRIUploadForm()
    return render(request, 'home.html', {'form': form})
def result(request):
    return HttpResponse("This is the result page")

# for signup, login, and logout
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You are successfully signed up!')
            return redirect('success_page')
    else:
        form = CustomUserCreationForm()
    login_form = AuthenticationForm()
    return render(request, 'signup.html', {'signup_form': form, 'login_form': login_form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('success_page')
    else:
        form = AuthenticationForm()
    signup_form = CustomUserCreationForm()
    return render(request, 'signup.html', {'signup_form': signup_form, 'login_form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def success_view(request):
    return render(request, 'success.html')

def success_page(request):
    return render(request, 'success_page.html')


def my_results_view(request):
    username = request.user.username
    user_folder = f'./media/inference/{username}/'
    images = []

    if os.path.exists(user_folder):
        for file_name in os.listdir(user_folder):
            # Find gif files and exclude 'inference_image.gif'
            if file_name.endswith('.gif') and file_name != 'inference.gif':
                # Create the image URL
                image_url = f'/media/inference/{username}/{file_name}'
                
                # Extract the image name (without the extension)
                image_name = os.path.splitext(file_name)[0]  # Get the file name without extension
                
                # Trim the image name by splitting it and taking the first word
                trimmed_name = image_name.split('_')[0]  # Split by underscore and take the first part
                
                # Append the image details to the list
                images.append({'url': image_url, 'name': trimmed_name})

    # Render the template with the list of images
    return render(request, 'myResults.html', {'images': images})