from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user.models import CustomUser, Profile
from .models import (Transaction, Withdrawal,
                     Deposit, Account, ReferralBonus,
                     Investment, Paymentgateway, clientPaymentgateway, Plan
                     ) 
from django.conf import settings
from django.core.mail import  EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Sum
import string
import random
import base64
import time
from io import BytesIO
from PIL import Image
from django.utils.crypto import get_random_string
from datetime import timedelta
from .utils import get_monthly_referral_profit
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site

from decimal import Decimal





def home(request):

    context = {
        "plans":Plan.objects.all(),

    }
    
    
    return render(request, 'client/home/index.html', context=context)



def about(request):
    
    
    return render(request, 'client/home/about-us.html')



def contact(request):
    
    if request.method == "POST":
        fullname = request.POST.get('fullname', None)
        email = request.POST.get('email', None)
        message = request.POST.get('message', None)

        subject = request.POST.get('subject', None)



        try:
            message = render_to_string('client/dashboard/mail_temp/contact.html',{
            'fullname':fullname,
            'email': email,
            'message': message,
            
           
            }
            )

            email_msg = EmailMessage(subject, message, to=[settings.ADMIN_EMAIL_CUSTOM])
            email_msg.content_subtype = 'html'

            email_msg.send()
        except Exception as e:
            print('ERROR', e)

        

    
    
    return render(request, 'client/home/contact.html')



def affliate(request):
    
    
    return render(request, 'client/home/affliate.html')



def faq(request):
    
    
    return render(request, 'client/home/faq.html')










@login_required(redirect_field_name='overview', login_url='login')
def overview(request):
    
    account = Account.objects.filter(user=request.user).first()
    # locked = Investment.objects.filter(user=request.user, invest_status='active').aggregate(Sum('amount'))["amount__sum"] or 0.00
    # locked_total = Investment.objects.filter(user=request.user, invest_status='active').count()
    
    protocall = 'https' if request.is_secure() else 'http'
    domain = str(get_current_site(request).domain)
    referral_code = request.user.referral_code
    referrals = ReferralBonus.objects.filter(referrer=request.user)
    # referred = 
    
    total_investmented_amount = Investment.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_investments = Investment.objects.filter(user=request.user).count()
    
    total_deposit_amount = Deposit.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    total_withdraw_amount = Withdrawal.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_referral_bonus_amount = ReferralBonus.objects.filter(referrer=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    total_investments_amount = Investment.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_investments_profits_amount = Investment.objects.filter(user=request.user, is_matured=True).aggregate(Sum('returns'))['returns__sum'] or 0.00
    
    # Locked investment balance
    locked_investments = Investment.objects.filter(user=request.user, is_matured=False).aggregate(Sum('amount'))['amount__sum'] or 0.00
    locked_investments_total = Investment.objects.filter(user=request.user, is_matured=False).count()
    investments_list = Investment.objects.filter(user=request.user).order_by('-start_date')
    
    total_referral_balance = ReferralBonus.objects.filter(referrer=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    
    # Monthly referral profit
    monthly_referral_profit = get_monthly_referral_profit(request.user)
    
    
    context = {
        'account_balance': round(account.account_balance,2),
        'account_total_profit': round(account.total_profit,2),
        'referral_balance': round(account.referral_bonus,2),
        "referral_link": f'{protocall}://{domain}/account/referral_signup/{referral_code}',
        'total_balance_amount': round(account.account_balance + Decimal(total_investments_amount),2) or 0.00,
        # 'locked_total': locked_total,
        'referral_count': referrals.count(),
        'total_referral_balance': total_referral_balance,
        'monthly_referral_profit': round(monthly_referral_profit,2),
        'total_investmented_amount': total_investmented_amount,
        'total_investments': total_investments,
        'locked_investments': locked_investments,
        'locked_investments_total': locked_investments_total,
        'investments_list': investments_list,
        'total_deposit_amount': round(total_deposit_amount,2),
        'total_withdraw_amount': round(total_withdraw_amount,2),
        'total_investments_amount': round(total_investments_amount,2),
        'total_investments_profits_amount': round(total_investments_profits_amount,2),
        'total_referral_bonus_amount': round(total_referral_bonus_amount,2),
        'referrals': referrals,
    }
    
    return render(request, 'client/dashboard/index.html', context)



@login_required(redirect_field_name='invest', login_url='login')
def invest(request):

    account = Account.objects.filter(user=request.user).first()
    locked_investments = Investment.objects.filter(user=request.user, is_matured=False).aggregate(Sum('amount'))['amount__sum'] or 0.00
    investments = Investment.objects.filter(user=request.user)

    
    context = {
        'account': account,
        "plans":Plan.objects.all(),
        "investments":investments,
        'locked_investments': locked_investments,


        
        
    }



    return render(request, 'client/dashboard/invest.html', context)





@login_required(redirect_field_name='invest_form', login_url='login')
def invest_form(request, plan):

    account = Account.objects.filter(user=request.user).first()
    # locked = Investment.objects.filter(user=request.user, invest_status='active').aggregate(Sum('amount'))["amount__sum"]
    locked_investments = Investment.objects.filter(user=request.user, is_matured=False).aggregate(Sum('amount'))['amount__sum'] or 0.00
    investments = Investment.objects.filter(user=request.user)
    message_s = ""
    
    
    if request.method == 'POST':
        amount = float(request.POST.get('amount', None))
        # plan_s = request.POST.get('plan', None).split("|")[0]
        
        plan=Plan.objects.filter(plan_name=plan).first()
        print(amount)
        print(plan)
        
 
        expected_returns = amount * (float(plan.percent) / 100)
        lock_period = timedelta(days=plan.period_length)
        due_date = timezone.now().date() + lock_period

        if amount > account.account_balance:
            return render(request, 'client/dashboard/invest-form.html', {"message":"insufficient balance "})

        account.account_balance -= int(amount)
        account.save()
        
        Investment.objects.create(user=request.user, plan=plan, amount=amount,returns=expected_returns, due_date=due_date)
        
        
        
        
        # Withdrawal.objects.create(user=request.user, amount=amount, Withdrawal_method=Withdrawal_method, address=address)
        
        message_s = "investment Successful"
        
        
        # c_subject = "Investment"

        # message = render_to_string('client/dashboard/mail_temp/invest.html',{
        #     'user':request.user.full_name,
        #     'amount': amount,
        #     "plan": request.POST.get('plan', None).split("|")[1],
            
           
        # }
        # )



        # email_msg = EmailMessage(c_subject, message, to=[request.user.email])
        # email_msg.content_subtype = 'html'


    
        # # # # for admin

        try:
            # a_subject = "Withdrawal Request from a user"

            a_message = render_to_string('client/dashboard/mail_temp/invest_admin.html',{
                'user':request.user.full_name,
                'email':request.user.email,
                'amount': amount,
                "plan": request.POST.get('plan', None).split("|")[1],
                
               
               
            }
            )


            # c_subject = "Investment"

            message = render_to_string('client/dashboard/mail_temp/invest.html',{
                'user':request.user.full_name,
                'amount': amount,
                "plan": request.POST.get('plan', None).split("|")[1],
                
               
            }
            )

            # a_email_msg = EmailMessage(a_subject, a_message, to=[settings.ADMIN_EMAIL_CUSTOM])
            # a_email_msg.content_subtype = 'html'


            # email_msg = EmailMessage(c_subject, message, to=[request.user.email])
            # email_msg.content_subtype = 'html'
            
            # # email_msg = send_mail(subject, 'message', to=[email])

            # email_msg.send()
            # a_email_msg.send()



            a_email_msg = EmailMultiAlternatives(
                    subject="Investment from a user",
                    body="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.ADMIN_EMAIL_CUSTOM],
                    )  
            

            a_email_msg.attach_alternative(a_message, "text/html")


            email_msg = EmailMultiAlternatives(
                    subject="Investment Successful",
                    body="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[request.user.email],
                    )  
            
            email_msg.attach_alternative(message, "text/html")

        

            a_email_msg.send()
            email_msg.send()

            return redirect('overview')


        except Exception as e:
            print(e)

        

    


    account = Account.objects.filter(user=request.user).first()
    # plan_m=Plan.objects.filter(plan_name=plan).first()

    context = {
        'account': account,
        "plan":Plan.objects.filter(plan_name=plan).first(),
        "payment_gates": Paymentgateway.objects.all(),
        "message":message_s,
        "investments":investments,
        'locked_investments': locked_investments,
        'account_balance': round(account.account_balance,2),

        
    }

    

    

    return render(request, 'client/dashboard/invest-form.html', context)







@login_required(redirect_field_name='deposit', login_url='login')
def deposit(request):
    
    account = Account.objects.filter(user=request.user).first()
    # locked = Investment.objects.filter(user=request.user, invest_status='active').aggregate(Sum('amount'))["amount__sum"]
    locked_investments = Investment.objects.filter(user=request.user, is_matured=False).aggregate(Sum('amount'))['amount__sum'] or 0.00
    deposits_list = Deposit.objects.filter(user=request.user)
    
    message_s = ""
    
     # For GET requests, display deposits and account balance
    # deposits = Deposit.objects.filter(user=request.user).order_by('-timestamp')
    account = get_object_or_404(Account, user=request.user)
    
    
    
    
    if request.method == 'POST':
        amount = request.POST.get('amount', None)
        payment_method = request.POST.get('payment_method', None).split("|")[0]
        payment_img = request.FILES.get("paymentp", None).read()
        image = Image.open(BytesIO(payment_img))
        image = image.convert('RGB')

        max_width = 800 
        width_percent = (max_width / float(image.size[0]))
        new_height = int((float(image.size[1]) * float(width_percent)))
        resized_image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

        output_buffer = BytesIO()
        
        resized_image.save(output_buffer, format='JPEG', quality=85)

        # 1. Get the bytes from the buffer
        image_bytes = output_buffer.getvalue()
        output_buffer.close()


        # 2. Encode to Base64 string
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # print(amount)
        # print(payment_method)
        # print(resized_image)
        
        
        Deposit.objects.create(user=request.user, amount=amount, payment_method=payment_method)
        
        # return redirect("deposit" )
        message_s = "Deposit is been processed"
        
        
        # c_subject = "Deposit"

        # message = render_to_string('client/dashboard/mail_temp/deposit.html',{
        #     'user':request.user.full_name,
        #     'amount': amount,
        #     "payment_method": payment_method,
           
        # }
        # )



        # email_msg = EmailMessage(c_subject, message,to=[request.user.email])
        # email_msg.content_subtype = 'html'
        
  



        # # # for admin

        try:
            # a_subject = "Deposit Request from a user"
            # c_subject = "Deposit"


            a_message = render_to_string('client/dashboard/mail_temp/admin_deposit.html',{
                'user':request.user.full_name,
                'email':request.user.email,
                'amount': amount,
                "payment_method": payment_method,
                "payment_image": image_base64                                                                                        
               
               
            }
            )


            message = render_to_string('client/dashboard/mail_temp/deposit.html',{
            'user':request.user.full_name,
            'amount': amount,
            "payment_method": payment_method,
           
        }
        )

            # a_email_msg = EmailMessage(a_subject, a_message, to=[settings.ADMIN_EMAIL_CUSTOM])
            # a_email_msg.content_subtype = 'html'

            # a_email_msg.attach()


            a_email_msg = EmailMultiAlternatives(
                    subject="Deposit Request from a user",
                    body="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.ADMIN_EMAIL_CUSTOM],
                    )  
            

            a_email_msg.attach_alternative(a_message, "text/html")

            a_email_msg.attach(f' {request.user.full_name}_deposit.jpg', image_bytes, "image/jpeg")


            email_msg = EmailMultiAlternatives(
                    subject="Deposit Request",
                    body="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[request.user.email],
                    )  
            
            email_msg.attach_alternative(message, "text/html")
    
            

            a_email_msg.send()
            email_msg .send()
        except Exception as e:
            print(e)
        
    
    
    context = {
        'account_balance': round(account.account_balance,2),
        # "plan":Plan.objects.filter(plan_name=plan).first(),
        'locked_investments': locked_investments,
        "payment_gates": Paymentgateway.objects.all(),
        "message":message_s,
        "deposits":deposits_list
    }
        
        
   
    
    return render(request, 'client/dashboard/deposit.html', context)







@login_required(redirect_field_name='withdraw', login_url='login')
def withdraw(request):
    
    account = Account.objects.filter(user=request.user).first()
    # locked = Investment.objects.filter(user=request.user, invest_status='active').aggregate(Sum('amount'))["amount__sum"]
    locked_investments = Investment.objects.filter(user=request.user, is_matured=False).aggregate(Sum('amount'))['amount__sum'] or 0.00
    withdrawals =  Withdrawal.objects.filter(user=request.user)
    message_s = ""
    
    if request.method == "POST":
        amount = float(request.POST.get('amount', None))
        Withdrawal_method = request.POST.get('payment_method', None)
        address = request.POST.get('address', None)
        
        
        # print(amount > account.account_balance)
        
        if amount > account.account_balance:
            message_s = "Insufficient funds."
            
        
        elif amount < 10:
            
            message_s = "minmum amount for withdrawal 10 ."

        else:
            
        
            
        
            Withdrawal.objects.create(user=request.user, amount=amount, Withdrawal_method=Withdrawal_method, address=address)
            
            message_s = "Your withdrawal is in progress"
        





            try:
                # a_subject = ""




                a_message = render_to_string('client/dashboard/mail_temp/withdraw_admin.html',{
                    'user':request.user.full_name,
                    'amount': amount,
                    "Withdrawal_method": Withdrawal_method,
                    "address": address
                
                
                }
                )

                message = render_to_string('client/dashboard/mail_temp/withdraw.html',{
                'user':request.user.full_name,
                'amount': amount,
                "Withdrawal_method": Withdrawal_method,
                "address": address
            
                }
                )

                # print(request.user.email)

                a_email_msg = EmailMultiAlternatives(
                        subject="Withdrawal Request from a user",
                        body="",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[settings.ADMIN_EMAIL_CUSTOM],
                        )  
                

                a_email_msg.attach_alternative(a_message, "text/html")


                email_msg = EmailMultiAlternatives(
                        subject="Withdrawal",
                        body="",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[request.user.email],
                        )  
                
                email_msg.attach_alternative(message, "text/html")

            
                
                a_email_msg.send()
                
                email_msg.send()
                
            except Exception as e:
                print(e)
        


    
    context = {
        'account_balance': round(account.account_balance,2),
        # "plans":Plan.objects.all(),
        "c_paymentgates": clientPaymentgateway.objects.all(),
        'locked_investments': locked_investments,
        "message":message_s,
        "withdrawals":withdrawals
        
        
    }
    
    
    return render(request, 'client/dashboard/withdraw.html', context)







# @login_required(redirect_field_name='invest', login_url='login')
# def invest(request):
    
#     account = Account.objects.filter(user=request.user).first()
#     # locked = Investment.objects.filter(user=request.user, invest_status='active').aggregate(Sum('amount'))["amount__sum"]
#     locked_investments = Investment.objects.filter(user=request.user, is_matured=False).aggregate(Sum('amount'))['amount__sum'] or 0.00
#     investments = Investment.objects.filter(user=request.user)
#     message_s = ""
    
    
#     if request.method == 'POST':
#         amount = float(request.POST.get('amount', None))
#         plan_s = request.POST.get('plan', None).split("|")[0]
        
#         plan = Plan.objects.get(id=plan_s)
        
#         print(request.POST.get('plan', None).split("|")[1])
#         expected_returns = amount * (float(plan.percent) / 100)
#         lock_period = timedelta(days=plan.period_length)
#         due_date = timezone.now().date() + lock_period
        
#         Investment.objects.create(user=request.user, plan=plan, amount=amount,returns=expected_returns, due_date=due_date)
        
        
        
        
#         # Withdrawal.objects.create(user=request.user, amount=amount, Withdrawal_method=Withdrawal_method, address=address)
        
#         message_s = "investment Successful"
        
        
#         # c_subject = "Investment"

#         # message = render_to_string('client/dashboard/mail_temp/invest.html',{
#         #     'user':request.user.full_name,
#         #     'amount': amount,
#         #     "plan": request.POST.get('plan', None).split("|")[1],
            
           
#         # }
#         # )



#         # email_msg = EmailMessage(c_subject, message, to=[request.user.email])
#         # email_msg.content_subtype = 'html'


    
#         # # # # for admin

#         # a_subject = "Withdrawal Request from a user"

#         # a_message = render_to_string('client/dashboard/mail_temp/invest_admin.html',{
#         #     'user':request.user.full_name,
#         #     'email':request.user.email,
#         #     'amount': amount,
#         #     "plan": request.POST.get('plan', None).split("|")[1],
            
           
           
#         # }
#         # )

#         # a_email_msg = EmailMessage(a_subject, a_message, to=[settings.ADMIN_EMAIL_CUSTOM])
#         # a_email_msg.content_subtype = 'html'
        
#         # # # email_msg = send_mail(subject, 'message', to=[email])

#         # email_msg.send()
#         # a_email_msg.send()

    
#     context = {
#         'account_balance': round(account.account_balance,2),
#         "plans":Plan.objects.all(),
#         'locked_investments': locked_investments,
#         "message":message_s,
#         "investments":investments,
        
        
        
        
#     }
    
#     return render(request, 'client/dashboard/invest.html', context)







def referral(request):
    
    account = Account.objects.filter(user=request.user).first()
    # locked = Investment.objects.filter(user=request.user, invest_status='active').aggregate(Sum('amount'))["amount__sum"]
    locked_investments = Investment.objects.filter(user=request.user, is_matured=False).aggregate(Sum('amount'))['amount__sum'] or 0.00
    referrals = ReferralBonus.objects.filter(referrer=request.user)
    
    
    message_s = ""
    
    # if request.method == "POST":
    #     amount = float(request.POST.get('amount', None))
    #     Withdrawal_method = request.POST.get('payment_method', None).split("|")[0]
    #     address = request.POST.get('address', None)
        
        
    #     print(Withdrawal_method)
        
    #     if amount > account.referral_bonus:
    #         message_s = "Insufficient funds."
            
        
    #     if amount < 1:
            
    #         message_s = "Insufficient funds."
            
        
    #     Withdrawal.objects.create(user=request.user, amount=amount, Withdrawal_method=Withdrawal_method, address=address, withdrawal_type='referral_bonus')
    #     # ReferralBonusWithdrawal.objects.create(user=request.user, amount=amount)
        
    #     message_s = "withdrawal in progress"
        
        
    #     c_subject = "Referra lWithdrawal"

    #     message = render_to_string('client/dashboard/mail_temp/withdraw.html',{
    #         'user':request.user.full_name,
    #         'amount': amount,
    #         "Withdrawal_method": Withdrawal_method,
    #         "address": address
           
    #     }
    #     )



    #     email_msg = EmailMessage(c_subject, message, to=[request.user.email])
    #     email_msg.content_subtype = 'html'



    #     # # for admin

    #     a_subject = " Referral Withdrawal Request from a user"

    #     a_message = render_to_string('client/dashboard/mail_temp/withdraw_admin.html',{
    #         'user':request.user.full_name,
    #         'email':request.user.email,
    #         'amount': amount,
    #         "Withdrawal_method": Withdrawal_method,
    #         "address": address
           
           
    #     }
    #     )

    #     a_email_msg = EmailMessage(a_subject, a_message, to=[settings.ADMIN_EMAIL_CUSTOM])
    #     a_email_msg.content_subtype = 'html'
        
    #     # email_msg = send_mail(subject, 'message', to=[email])

    #     email_msg.send()
    #     a_email_msg.send()

    
    context = {
        'account_balance': round(account.account_balance,2),
        'referral_balance': round(account.referral_bonus,2),
        "c_paymentgates": clientPaymentgateway.objects.all(),
        'locked_investments': locked_investments,
        'referrals': referrals,
        "message":message_s,
 
        
        
    }
    
    
    return render(request, 'client/dashboard/referral.html', context)





# def referral_bonus_withdraw(request):
#     if request.method == "POST":
#         amount = request.POST.get("amount")
        
#         try:
#             amount = Decimal(amount)
#         except (ValueError, TypeError):
#             messages.error(request, "Invalid amount.")
#             return redirect("referral_page")  # Redirect to referral page
        
#         account = Account.objects.filter(user=request.user).first()
#         if not account:
#             messages.error(request, "Account not found.")
#             return redirect("referral_page")

#         # Ensure the user has enough referral bonus balance
#         if amount <= 0 or amount > account.referral_bonus:
#             messages.error(request, "Insufficient referral bonus balance.")
#             return redirect("referral_page")

#         # Find available referral bonuses and mark them as withdrawn
#         referral_bonuses = ReferralBonus.objects.filter(referrer=request.user, is_withdrawn=False)
#         remaining_amount = amount

#         for bonus in referral_bonuses:
#             if remaining_amount <= 0:
#                 break
#             if bonus.amount <= remaining_amount:
#                 remaining_amount -= bonus.amount
#                 bonus.is_withdrawn = True  # Mark as withdrawn
#             else:
#                 bonus.amount -= remaining_amount
#                 remaining_amount = 0
#             bonus.save()

#         # Deduct from referral bonus balance
#         account.referral_bonus -= amount
#         account.save()

#         # Create a withdrawal request
#         withdrawal_request = ReferralBonusWithdrawal.objects.create(
#             user=request.user,
#             amount=amount,
#             status="pending",
#             requested_at=now(),
#         )

#         messages.success(request, "Referral bonus withdrawal request submitted.")
#         return redirect("referral_page")

#     return redirect("referral_page")  # If not a POST request







def profile(request):
    
    account = Account.objects.filter(user=request.user).first()
    # locked = Investment.objects.filter(user=request.user, invest_status='active').aggregate(Sum('amount'))["amount__sum"]
    locked_investments = Investment.objects.filter(user=request.user, is_matured=False).aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    
    message_s=""
    
    
    if request.method == "POST":

        full_name = request.POST.get('full_name', None)
        gender = request.POST.get('gender', None)
        phone = request.POST.get('phone', None)
        address = request.POST.get('address', None)
        zipcode = request.POST.get('zipcode', None)
        state = request.POST.get('state', None)
        country = request.POST.get('country', None)
        profile_picture = request.FILES.get("profile_picture")

        profile = Profile.objects.get(user=request.user)

        profile.address = address
        profile.zip_code = zipcode
        profile.state =state
        profile.country =country

        profile.phone = phone
        profile.gender = gender
        profile.user.full_name =full_name
        
        if profile_picture:
            profile.profile_picture = profile_picture

        

        profile.save()
        
        message_s=" profile updated successfully"
    
    
    context = {
        'account_balance': round(account.account_balance,2),
        'locked_investments': locked_investments,
        "message":message_s
        
        
    }
    
    return render(request, 'client/dashboard/profile.html', context)