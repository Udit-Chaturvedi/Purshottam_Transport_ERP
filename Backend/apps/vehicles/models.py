from django.db import models
from django.core.exceptions import ValidationError
import os
from datetime import date

def document_upload_path(instance, filename):
    return f"documents/{instance.registration_number}/{filename}"

ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf']

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError('Only .jpg, .jpeg, .png, or .pdf files are allowed.')
    
    MAX_FILE_SIZE = 5 * 1024 * 1024
    if value.size > MAX_FILE_SIZE:
        raise ValidationError('File size should not exceed 5MB.')
    
# Custom validation to ensure the date is not in the past
def validate_not_past_date(value):
    if value < date.today():
        raise ValidationError(f"The date {value} is in the past, please provide a valid future date.")

class Vehicle(models.Model):
    registration_number = models.CharField(max_length=20, unique=True)
    engine_number = models.CharField(max_length=50, unique=True)
    chassis_number = models.CharField(max_length=50, unique=True)

    # RC Document
    rc_document_number = models.CharField(max_length=100)
    rc_file = models.FileField(upload_to=document_upload_path, validators=[validate_file_extension])

    # Insurance Document
    insurance_document_number = models.CharField(max_length=100)
    insurance_expiry_date = models.DateField(validators=[validate_not_past_date])
    insurance_file = models.FileField(upload_to=document_upload_path, validators=[validate_file_extension])

    # Tax Document
    tax_document_number = models.CharField(max_length=100)
    tax_expiry_date = models.DateField(validators=[validate_not_past_date])
    tax_file = models.FileField(upload_to=document_upload_path, validators=[validate_file_extension])

    # T-Permit Document
    permit_document_number = models.CharField(max_length=100)
    permit_expiry_date = models.DateField(validators=[validate_not_past_date])
    permit_file = models.FileField(upload_to=document_upload_path, validators=[validate_file_extension])

    # Fitness Document
    fitness_document_number = models.CharField(max_length=100)
    fitness_expiry_date = models.DateField(validators=[validate_not_past_date])
    fitness_file = models.FileField(upload_to=document_upload_path, validators=[validate_file_extension])

    # PUC Document
    puc_document_number = models.CharField(max_length=100)
    puc_expiry_date = models.DateField(validators=[validate_not_past_date])
    puc_file = models.FileField(upload_to=document_upload_path, validators=[validate_file_extension])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.registration_number
