from requests import request
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib import messages
from .models import *

def send_email(recipient_email, detection_results):
    subject = 'Rapport Quotidien des Détections'
    context = {'detection_results': detection_results}  # Pass detection results to the template
    
    # Render HTML content from a template
    html_content = render_to_string('email_template.html', context)
    
    # Create the email
    email = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_content),  # Plain text version of the email
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_email],
    )
    
    # Attach HTML content
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
    except Exception as e:
        messages.error(request, f'Failed to send email: {e}')
