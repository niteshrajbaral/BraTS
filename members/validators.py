# members/validators.py
# validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import MinimumLengthValidator, CommonPasswordValidator

def validate_nifti_file(value):
    valid_extensions = ['.nii', '.nii.gz']
    if not any(value.name.endswith(ext) for ext in valid_extensions):
        raise ValidationError('File must be a NIfTI file with .nii or .nii.gz extension')

# validation
class CustomMinimumLengthValidator(MinimumLengthValidator):
    def get_help_text(self):
        return _("Your password must contain at least %(min_length)d characters.") % {'min_length': self.min_length}

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("This password must contain at least %(min_length)d characters.") % {'min_length': self.min_length},
                code='password_too_short',
            )
class CustomCommonPasswordValidator(CommonPasswordValidator):
    def get_help_text(self):
        return _("Your password can’t be a commonly used password.")

    def validate(self, password, user=None):
        if self._is_common_password(password):
            raise ValidationError(
                _("This password is too common."),
                code='password_too_common',
            )

    def _is_common_password(self, password):
        # Here you can add custom logic to check if the password is common
        # This is just a placeholder for demonstration purposes
        common_passwords = ["password", "12345678", "qwerty"]
        return password in common_passwords