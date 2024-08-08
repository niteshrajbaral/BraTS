# from django.db import models

# class MRIUpload(models.Model):
#     name = models.CharField(max_length=255)
#     nifti_file = models.FileField(upload_to='nifti_files/',default='')

#     def __str__(self):
#         return self.name

from django.db import models
from .validators import validate_nifti_file

class MRIUpload(models.Model):
    name = models.CharField(max_length=255) 
    nifti_file = models.FileField(upload_to='nifti_files/', validators=[validate_nifti_file])

    def __str__(self):
        return self.name
