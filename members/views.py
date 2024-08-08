# members/views.py
from django.shortcuts import render
from django.http import HttpResponse
from .forms import MRIUploadForm
from .models import MRIUpload
from .utils import predict_nifti

# for signup, login, and logout
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm


# for saving the result image
import os
import nibabel as nib

def home(request):
    if request.method == 'POST':
        form = MRIUploadForm(request.POST, request.FILES)
        if form.is_valid():
            mri_upload = form.save()
            nifti_file_path = mri_upload.nifti_file.path
            result_img = predict_nifti(nifti_file_path)

            # Save the result image as a file
            result_img_path = os.path.join('nifti_files', 'result_' + os.path.basename(nifti_file_path))
            nib.save(result_img, result_img_path)

            return render(request, 'result.html', {'result_img_path': result_img_path})
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

