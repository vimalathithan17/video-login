from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
# Create your views here.
# views.py or any other module
from django_otp.decorators import otp_required
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
import base64
import cv2
from pyzbar import pyzbar
import numpy as np
def send_test_email():
    subject = 'Test Email'
    message = 'This is a test email sent from Django.'
    email_from = settings.DEFAULT_FROM_EMAIL  # Or you can specify a custom email address here
    recipient_list = ['22i272@psgtech.ac.in']  # Replace with the actual recipient's email

    send_mail(subject, message, email_from, recipient_list)

# Call this function from a view or any part of your code to send the email

def homepage(request):
    # send_test_email()
    print(request.user,request.user.is_anonymous,request.user.is_verified)
    return render(request,'home/home.html')

@ensure_csrf_cookie
def capture(request):
    return render(request,'home/image.html')

def decode_barcode(frame):
    # Find and decode barcodes
    barcodes = pyzbar.decode(frame)

    # Process each barcode found
    for barcode in barcodes:
        # Extract the bounding box location of the barcode
        (x, y, w, h) = barcode.rect

        # Draw a rectangle around the barcode
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Convert barcode data to string format
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type

        # Print barcode information
        print(barcode_data)
        #print("Barcode Type:", barcode_type)
        return barcode_data  # Set flag to True if a barcode is detected

    return False  # Set flag to False if no barcode is detected


def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'

def verify(request):
    user=authenticate(request,username='22i272',password='22i272')
    print(user)
    login(request,user) 
    return redirect('homepage')
    if is_ajax(request):
        photo = request.POST.get('photo')
        _, str_img = photo.split(';base64')

        # print(photo)
        decoded_file = base64.b64decode(str_img)
        np_img = np.frombuffer(decoded_file, dtype=np.uint8)

        # Decode the image using OpenCV
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        frame = cv2.resize(img, None, fx=0.6, fy=0.6)

        # Convert the frame to grayscale for barcode detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Call the barcode decoding function
        barcode_detected = decode_barcode(gray)
        print(barcode_detected)
        if barcode_detected:
            print('shit')
            user=authenticate(request,username=barcode_detected.lower(),password=barcode_detected.lower())
            print(user)
            login(request,user)
            return redirect('homepage')
        return render(request,'home/image.html')
    return HttpResponse('fuck you')


@otp_required
def vote(request):
    return HttpResponse('sucess')  

def logout2(request):
    logout(request)
    return HttpResponse('lo')

from functools import partial

from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth import views as auth_views
from django.utils.functional import cached_property

from django_otp.forms import OTPAuthenticationForm, OTPTokenForm


class LoginView(auth_views.LoginView):
    """
    This is a replacement for :class:`django.contrib.auth.views.LoginView` that
    requires two-factor authentication. It's slightly clever: if the user is
    already authenticated but not verified, it will only ask the user for their
    OTP token. If the user is anonymous or is already verified by an OTP
    device, it will use the full username/password/token form. In order to use
    this, you must supply a template that is compatible with both
    :class:`~django_otp.forms.OTPAuthenticationForm` and
    :class:`~django_otp.forms.OTPTokenForm`. This is a good view for
    :setting:`OTP_LOGIN_URL`.

    """

    # otp_authentication_form = OTPAuthenticationForm
    otp_token_form = OTPTokenForm

    @cached_property
    def authentication_form(self):
        user = self.request.user
        form =  partial(self.otp_token_form,user)
        return form

    def form_valid(self, form):
        # OTPTokenForm does not call authenticate(), so we may need to populate
        # user.backend ourselves to keep login() happy.

        return super().form_valid(form)


