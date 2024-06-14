from firebase_admin import auth , credentials
import cv2
from matplotlib import pyplot as plt
import numpy as np
import imutils
import easyocr
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .forms import Upload
from myapp.models import Driver_info 
from .models import Images
from .models import UploadedImage
#from .models import UploadedImage
import pyrebase
import smtplib
from email.mime.text import MIMEText
import firebase_admin
from django.core import serializers
import json
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login


# Create your views here.
def index(request):
    user_count = User.objects.all().count()
    violation_count = Images.objects.all().count()
    
    context = {
        "user_count" : user_count,
        "violation_count" : violation_count
    }
    return render(request, 'myapp/index.html', context)

def upload_image1(request):
    if request.method == 'POST' and request.POST.get('image_url'):
        image_url = request.POST.get('image_url')
        response = requests.get(image_url)
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch image from URL'}, status=400)

        img = Image.open(BytesIO(response.content))
        
        # Process the image using EasyOCR
        reader = easyocr.Reader(['en'])
        result = reader.readtext(img)

        # Example of extracting text from the OCR result
        text = ' '.join([res[1] for res in result])

        # Query the driver based on the extracted text (e.g., license plate number)
        driver = Driver_info.objects.filter(plate=text).first()

        # Construct the URL for the result page with query parameters
        result_url = reverse('result1') + f"?image_url={image_url}&text={text}&driver_id={driver.id if driver else ''}"

        return JsonResponse({'redirect_url': result_url})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

def result1(request):
    # Retrieve data from the GET parameters
    image_url = request.GET.get('image_url')
    text = request.GET.get('text')
    driver_id = request.GET.get('driver_id')
    driver = get_object_or_404(Driver_info, id=driver_id) if driver_id else None
    
    # Render the 'result1.html' template with the necessary data
    return render(request, 'myapp/result1.html', {'image_url': image_url, 'text': text, 'driver': driver})


def vehicles(request):
    products = Images.objects.all()
    return render(request, 'myapp/violations.html', {'products': products})



########################################################################################
# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

def extract_text(request):
    if request.method == 'POST':
        image_url = request.POST.get('image_url')
        image_id = request.POST.get('image_id')

        # Ensure image_url is valid
        if not image_url or not image_id:
            return JsonResponse({'error': 'Invalid image URL or image ID'}, status=400)
        
        # Fetch the image from the provided URL
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        
        # Process the image using EasyOCR
        reader = easyocr.Reader(['en'])
        result = reader.readtext(img)
        if result:
            # Extract all text detected by EasyOCR
            extracted_text = str(' '.join([res[-2] for res in result]))
        else:
            extracted_text = "No text found"

        # Query the DriverInfo model with the extracted text
        driver = Driver_info.objects.filter(plate__iexact=extracted_text).first()

       # Construct the URL for the result page with query parameters
        result_url = reverse('images') + f"?image_url={image_url}&extracted_text={extracted_text}&driver_id={driver.id if driver else ''}"

        return JsonResponse({'redirect_url': result_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def image_list(request):
    extracted_text = request.GET.get('extracted_text', 'No text extracted')
    images = Images.objects.select_related('driver').all()
    return render(request, 'myapp/last_result.html', {'images': images,'extracted_text': extracted_text })

def result2(request):
    extracted_text = request.GET.get('extracted_text', 'No text extracted')
    try:
        driver = Driver_info.objects.get(plate__iexact=extracted_text)
        driver_data = {
            'name': driver.name,
            'address': driver.address,
            'model': driver.model,
            
        }
    except Driver_info.DoesNotExist:
        driver_data = None

    return render(request, 'myapp/result2.html', {'extracted_text': extracted_text, 'driver_data': driver_data})
##################
# auth_app/views.py
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import OTP
import random

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user):
    otp = generate_otp()
    OTP.objects.update_or_create(user=user, defaults={'otp': otp, 'expires_at': datetime.now() + timedelta(minutes=2)})
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp}',
        'chihambakwekudakwashe3@gmail.com',
        [user.email],
        fail_silently=False,
    )

def login(request):
    if request.method == 'POST':
        # Perform initial authentication
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            send_otp_email(user)
            request.session['pre_otp_user_id'] = user.id
            return redirect('verify_otp')
    return render(request, 'myapp/login.html')

def verify_otp_view(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        user_id = request.session.get('pre_otp_user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            otp_record = OTP.objects.get(user=user)
            
            # Ensure otp_record.expires_at is timezone-aware
            if timezone.is_naive(otp_record.expires_at):
                otp_record.expires_at = timezone.make_aware(otp_record.expires_at, timezone.get_default_timezone())

            # Using timezone-aware current time
            current_time = timezone.now()

            if otp_record.otp == otp and otp_record.expires_at > current_time:
                auth_login(request, user)
                return redirect('index')
            else:
                return render(request, 'myapp/verify_otp.html', {'error': 'Invalid or expired OTP'})
    return render(request, 'myapp/verify_otp.html')

from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template

def pdf(request, pk):
    # Assuming you are fetching the first driver for demonstration purposes
    # Adjust the logic as per your requirement
    driver = Driver_info.objects.get(id=pk)
    
    if not driver:
        return HttpResponse("Driver not found", status=404)
    
    template_path = 'myapp/pdf.html'
    context = {
        'driver': driver,
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # Render the HTML template with context data
    template = get_template(template_path)
    html = template.render(context)

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response

def violation_info(request):
    
    violation_info = Images.objects.all()
    
    context = {
        'data': violation_info,
    }
    return render(request, 'myapp/datatable.html', context)
#############################################################################

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = Images(image=request.FILES['image'])
        uploaded_image.save()
        return JsonResponse({'status': 'success', 'message': 'Image uploaded successfully'})
    else:
        return JsonResponse({'status': 'failed', 'message': 'Invalid request method or missing image'})