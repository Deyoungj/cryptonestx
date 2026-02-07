from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage, send_mail,EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from .models import CustomUser
from .token import account_activation_token
from django.conf import settings
import os
import re
import requests

url_pattern = re.compile(r'https?://[^\s/$.?#].[^\s]*')



def register(request):
    
    if request.method == "POST":
        # recaptcha_response = request.POST.get('g-recaptcha-response')


        #   # 2. Data to send to Google API
        # data = {
        #     'secret': '6LcfOTMsAAAAAOmuOY5Zl7F4RyXCTf-kw5dwZeVG',
        #     'response': recaptcha_response
        # }

        # # 3. Verify with Google
        # r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        # result = r.json()
        
        # # 2. Check if reCAPTCHA was successful
        # if not result.get('success'):
        #     return render(request, "user/signup.html", {
        #         'message': 'Invalid reCAPTCHA. Please try again.'
        #     })

        # 3. Proceed with existing registration logic
        full_name = request.POST.get('fullname', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password1', '')

        # Input Validation
        if not all([full_name, email, password, password2]):
            return render(request, "user/signup.html", {'message': 'All fields must be filled'})
        
        if CustomUser.objects.filter(email=email).exists():
            return render(request, "user/signup.html", {'message': 'Email already exists'})

        if password != password2:
            return render(request, "user/signup.html", {'message': "Passwords didn't match"})


        try:
            # a_subject = "Welcome"

            html_content = render_to_string('user/email_temp/welcome.html',{
                'user':full_name,
                  
            }
            )


            a_html_content = render_to_string('user/email_temp/welcome_admin.html',{
                'user':full_name,
                'email':email,
                  
            }
            )

            email_msg = EmailMultiAlternatives(
                    subject="Welcome to Cardone Mining Capital",
                    body="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                    )   
            

            a_email_msg = EmailMultiAlternatives(
                    subject="New Account Signup Alert",
                    body="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.ADMIN_EMAIL_CUSTOM],
                    )   



  



            email_msg.attach_alternative(html_content, "text/html")
            a_email_msg.attach_alternative(a_html_content, "text/html")



            # logo_path = os.path.join(
            #     settings.BASE_DIR,
            #     "client/static/client/images/logo1.png"
            # )



            # with open(logo_path, "rb") as f:
            #     logo = MIMEImage(f.read())
            #     logo.add_header("Content-ID", "<logo>")
            #     logo.add_header("Content-Disposition", "inline", filename="logo.png")
            #     email_msg.attach(logo)

            # a_email_msg = EmailMessage(a_subject, a_message, to=[email])
            # a_email_msg.content_subtype = 'html'
            
            # # email_msg = send_mail(subject, 'message', to=[email])

            # email_msg.send()
            email_msg.send()
            a_email_msg.send()


        except Exception as e:
            print(e)


            

        # # Create User
        user = CustomUser.objects.create(full_name=full_name, email=email)
        user.set_password(password)
        user.is_active = True
        user.save()

        # Authenticate and Login
        auth_user = authenticate(request, email=email, password=password)
        if auth_user:
            auth_login(request, auth_user)
            return redirect('overview')


        # try:
        #     pass
        # except Exception as e:
        #     raise e
        # else:
        #     pass



        

        # subject = "Welcome"
        
        # message = render_to_string('user/email_temp/activation.html',{
        #     'user':full_name,
        #     'domain': get_current_site(request).domain,
        #     "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        #     'token': account_activation_token.make_token(user),
        #     'protocol': 'https' if request.is_secure() else 'http'
        # }
        # )

        # email_msg = EmailMessage(subject, message,to=[email])
        
        
        # if email_msg.send():


        #     context={
        #         'full_name' :  full_name,
        #         'email' :   email,
        #     }

        #     return render(request, 'user/confirm_email.html', context)
        
        # else:
        #     return render(request, 'user/signup.html', {'message': "Email can't sent, make sure you typed a valid email"})
    
    
    return render(request, 'user/signup.html', {'message': ""})





def activate(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        return render(request, 'user/activated.html')
    else:
        return render(request, 'user/active_invalid.html')








def login(request):
    if request.method == "POST":
        # # 1. Get reCAPTCHA response from the form
        # recaptcha_response = request.POST.get('g-recaptcha-response')
        
        # # 2. Verify with Google
        # data = {
        #     'secret': '6LcfOTMsAAAAAOmuOY5Zl7F4RyXCTf-kw5dwZeVG',
        #     'response': recaptcha_response
        # }
        # r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        # result = r.json()

        # # 3. Check if reCAPTCHA verification failed
        # if not result.get('success'):
        #     return render(request, 'user/signin.html', {
        #         'message': "Invalid reCAPTCHA. Please try again."
        #     })

        # 4. Proceed with your original authentication logic
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('overview')
        else:
            return render(request, 'user/signin.html', {
                'message': "Incorrect email or password."
            })
    
    return render(request, 'user/signin.html', {'message': ""})




def user_logout(request):
    logout(request)

    return redirect('home')





def password_reset(request):
    
    
    if request.method == "POST":
        
       
        email = request.POST.get('email', None)
        
   
        check_email = CustomUser.objects.filter(email=email).exists()
        user = CustomUser.objects.filter(email=email).first()


        if check_email:

            subject = "Password Reset"

            message = render_to_string('user/email_temp/password_reset.html',{
                'user':user.full_name,
                'domain': get_current_site(request).domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http' 
            }
            )

            email_msg = EmailMessage(subject, message,to=[email])
            # email_msg = send_mail(subject, 'message', to=[email])

            if email_msg.send():


                context={
                    "full_name":user.full_name,
                    'email' :   email,
                }

                return render(request, 'user/password_pass_email.html', context)
            
            else:
                return render(request, 'user/password_reset.html', {'message': "Email can't sent, error with server."})


  
    
    
    return render(request, 'user/reset-password.html', {'message': ""})




def password_change(request, uidb64, token):

    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):

        if request.method == "POST":
        
       
            password = request.POST.get('password', None)
            password2 = request.POST.get('password2', None)


            if password != password:

                return render(request, 'user/new_password.html',{'message': "Passwords did't match"})
            
        
            user.set_password = password
            user.save()

            print(password)
            print(password2)
            
            return render(request, 'user/password_reset_confirm.html')



    return render(request, 'user/new_password.html', {'message': ""})





def password_reset_confirm(request):
    
    
    return render(request, 'user/password_reset_confirm.html')













def referral_signup(request, referral_code):
    # print(referral_code)

    

    if request.method == "POST":

        # recaptcha_response = request.POST.get('g-recaptcha-response')


        #   # 2. Data to send to Google API
        # data = {
        #     'secret': '6LcfOTMsAAAAAOmuOY5Zl7F4RyXCTf-kw5dwZeVG',
        #     'response': recaptcha_response
        # }

        # # 3. Verify with Google
        # r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        # result = r.json()
        
        # # 2. Check if reCAPTCHA was successful
        # if not result.get('success'):
        #     return render(request, "user/signup.html", {
        #         'message': 'Invalid reCAPTCHA. Please try again.'
        #     })
        
        
        
        full_name = request.POST.get('fullname', None)
        # username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        password2 = request.POST.get('password1', None)

        check_email = CustomUser.objects.filter(email=email).exists()

        if check_email:
            return render(request, "user/signup.html", {'message':'email already exists'})


        if password != password2:
            return render(request,"user/signup.html", {'message': "Passwords didn't match "})
        
        ref_user = CustomUser.objects.filter(referral_code=referral_code).first()
        if not ref_user:
            return render(request, "user/signup.html", {'message': "Invalid referral code"})


        
        try:
            # a_subject = "Welcome"

            html_content = render_to_string('user/email_temp/welcome.html',{
                'user':full_name,
                  
            }
            )

            b_html_content = render_to_string('user/email_temp/welcome.html',{
                'user':full_name,
                  
            }
            )


            a_html_content = render_to_string('user/email_temp/welcome_admin.html',{
                'user':full_name,
                'email':email,
                  
            }
            )

            email_msg = EmailMultiAlternatives(
                    subject="Welcome to Cardone Mining Capital",
                    body="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                    )   
            

            a_email_msg = EmailMultiAlternatives(
                    subject="New referal Signup Alert",
                    body="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.ADMIN_EMAIL_CUSTOM],
                    ) 


            b_email_msg = EmailMultiAlternatives(
                    subject="referal Signup Alert",
                    body="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[ref_user.email],
                    )   



  



            email_msg.attach_alternative(html_content, "text/html")
            a_email_msg.attach_alternative(a_html_content, "text/html")
            b_email_msg.attach_alternative(b_html_content, "text/html")



            # logo_path = os.path.join(
            #     settings.BASE_DIR,
            #     "client/static/client/images/logo1.png"
            # )



            # with open(logo_path, "rb") as f:
            #     logo = MIMEImage(f.read())
            #     logo.add_header("Content-ID", "<logo>")
            #     logo.add_header("Content-Disposition", "inline", filename="logo.png")
            #     email_msg.attach(logo)

            # a_email_msg = EmailMessage(a_subject, a_message, to=[email])
            # a_email_msg.content_subtype = 'html'
            
            # # email_msg = send_mail(subject, 'message', to=[email])

            # email_msg.send()
            email_msg.send()
            a_email_msg.send()
            b_email_msg.send()


        except Exception as e:
            print(e)

            

        
        user = CustomUser.objects.create(full_name=full_name, email=email,referrer=ref_user)

        user.set_password(password)
        user.is_active = True
        user.save()
        
        user = authenticate(email=email, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('overview')

        # ref_user = CustomUser.objects.filter(referral_code=referral_code).first()


        



    return render(request, 'user/signup.html', {'message': ""})


