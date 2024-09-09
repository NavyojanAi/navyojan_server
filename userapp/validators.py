from django.core.exceptions import ValidationError
from userapp.app_constants import max_pdf_size



def validate_pdf(file):
    if not file.name.endswith('.pdf'):
        raise ValidationError("Only PDF files are allowed.")
    
    if file.size > max_pdf_size:
        raise ValidationError(f"PDF file size should not exceed 5MB.")