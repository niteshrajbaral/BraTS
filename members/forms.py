
from django import forms
from .models import MRIUpload
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class MRIUploadForm(forms.ModelForm):
    class Meta:
        model = MRIUpload
        fields = ['name','nifti_file']

    def clean_nifti_file(self):
        file = self.cleaned_data.get('nifti_file')
        valid_extensions = ['.nii', '.nii.gz']
        if not any(file.name.endswith(ext) for ext in valid_extensions):
            raise forms.ValidationError('File must be a NIfTI file with .nii or .nii.gz extension')
        return file
    
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

# forms
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        help_text=None,
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text=None,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text=None,
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")