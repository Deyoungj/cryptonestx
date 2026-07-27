from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user.models import CustomUser, Profile
from .models import (Transaction, Withdrawal,
                     Deposit, Account, ReferralBonus,
                     Investment, Paymentgateway, clientPaymentgateway, Plan, PromotionalCreditClaim
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
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from decimal import Decimal, InvalidOperation

# from decimal import Decimal, InvalidOperation

# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.db.models import Sum
# from django.shortcuts import render

# from .models import Account, Investment, Withdrawal, clientPaymentgateway





# Minimum deposit required for Level 2 eligibility
LEVEL_2_DEPOSIT_REQUIREMENT = Decimal("500.00")


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



        # try:
        #     message = render_to_string('client/dashboard/mail_temp/contact.html',{
        #     'fullname':fullname,
        #     'email': email,
        #     'message': message,
            
           
        #     }
        #     )

        #     email_msg = EmailMessage(subject, message, to=[settings.ADMIN_EMAIL_CUSTOM])
        #     email_msg.content_subtype = 'html'

        #     email_msg.send()
        # except Exception as e:
        #     print('ERROR', e)

        

    
    
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

    promotional_balance = account.promotional_balance
    account_level = account.level
    withdrawal_enabled = account.withdrawal_enabled
    is_verified = account.is_verified
    
    protocall = 'https' if request.is_secure() else 'http'
    domain = str(get_current_site(request).domain)
    referral_code = request.user.referral_code
    referrals = ReferralBonus.objects.filter(referrer=request.user)
    # referred = 
    
    # total_investmented_amount = Investment.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_investmented_amount = account.total_invested
    total_investments = Investment.objects.filter(user=request.user).count()
    
    total_deposit_amount = Deposit.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    total_withdraw_amount = Withdrawal.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_referral_bonus_amount = ReferralBonus.objects.filter(referrer=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    # total_investments_amount = Investment.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_investments_amount = account.total_invested
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
        'promotional_balance': round(account.promotional_balance,2),

        'account_level': account.level,
        'withdrawal_enabled': account.withdrawal_enabled,
        'is_verified': account.is_verified,

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
        'account_balance': round(account.account_balance,2),
        "plans":Plan.objects.all(),
        "investments":investments,
        'locked_investments': locked_investments,


        
        
    }



    return render(request, 'client/dashboard/invest.html', context)


# @login_required(login_url="login")
# def upgrade_level_2(request):
#     account = Account.objects.get(user=request.user)

#     # User is already Level 2 or higher
#     if account.level >= 2:
#         return render(
#             request,
#             "client/dashboard/upgrade_level_2.html",
#             {
#                 "account": account,
#                 "already_upgraded": True,
#                 "projected_balance": account.account_balance,
#             },
#         )

#     # Get or create the promotion claim record
#     claim, created = PromotionalCreditClaim.objects.get_or_create(
#         user=request.user,
#         defaults={
#             "promotional_amount": account.promotional_balance,
#         },
#     )

#     if request.method == "POST":

#         with transaction.atomic():

#             # Lock account to prevent duplicate claims
#             account = Account.objects.select_for_update().get(
#                 user=request.user
#             )

#             claim = PromotionalCreditClaim.objects.select_for_update().get(
#                 user=request.user
#             )

#             # Already upgraded
#             if account.level >= 2:
#                 messages.info(
#                     request,
#                     "Your account is already upgraded to Level 2.",
#                 )
#                 return redirect("upgrade_level_2")

#             # Already claimed
#             if claim.status == "claimed":
#                 messages.info(
#                     request,
#                     "Your promotional credit has already been released.",
#                 )
#                 return redirect("upgrade_level_2")

#             # Level 2 eligibility
#             if not account.is_verified:
#                 messages.error(
#                     request,
#                     "Your account must be verified before you can upgrade to Level 2.",
#                 )
#                 return redirect("upgrade_level_2")

#             # Promotional balance must exist
#             if account.promotional_balance <= Decimal("0.00"):
#                 messages.error(
#                     request,
#                     "There is no promotional credit available to release.",
#                 )
#                 return redirect("upgrade_level_2")

#             # ==========================================
#             # RELEASE PROMOTIONAL CREDIT
#             # ==========================================

#             promotional_amount = account.promotional_balance

#             account.account_balance += promotional_amount
#             account.promotional_balance = Decimal("0.00")

#             # Upgrade account
#             account.level = 2

#             # Enable normal withdrawal eligibility
#             account.withdrawal_enabled = True

#             account.save(
#                 update_fields=[
#                     "account_balance",
#                     "promotional_balance",
#                     "level",
#                     "withdrawal_enabled",
#                 ]
#             )

#             # ==========================================
#             # RECORD PROMOTIONAL CLAIM
#             # ==========================================

#             claim.promotional_amount = promotional_amount
#             claim.claimed_amount = promotional_amount
#             claim.status = "claimed"
#             claim.claimed_at = timezone.now()

#             claim.save(
#                 update_fields=[
#                     "promotional_amount",
#                     "claimed_amount",
#                     "status",
#                     "claimed_at",
#                 ]
#             )

#         messages.success(
#             request,
#             f"Congratulations! Your account is now Level 2 and "
#             f"${promotional_amount:,.2f} has been released to your main balance.",
#         )

#         return redirect("upgrade_level_2")

#     # Calculate projected balance for display
#     projected_balance = (
#         account.account_balance + account.promotional_balance
#     )

#     return render(
#         request,
#         "client/dashboard/upgrade_level_2.html",
#         {
#             "account": account,
#             "claim": claim,
#             "already_upgraded": False,
#             "projected_balance": projected_balance,
#         },
#     )


@login_required(login_url="login")
def upgrade_level_2(request):

    level_2_deposit_requirement = LEVEL_2_DEPOSIT_REQUIREMENT

    # ---------------------------------------------------------
    # GET CURRENT ACCOUNT
    # ---------------------------------------------------------
    account = Account.objects.get(user=request.user)

    # ---------------------------------------------------------
    # CHECK QUALIFYING DEPOSIT
    # ---------------------------------------------------------
    qualifying_deposit_completed = Transaction.objects.filter(
        user=request.user,
        transaction_type="deposit",
        status="successful",
        amount__gte=level_2_deposit_requirement,
    ).exists()

    # ---------------------------------------------------------
    # GET OR CREATE PROMOTIONAL CLAIM
    # ---------------------------------------------------------
    claim, created = PromotionalCreditClaim.objects.get_or_create(
        user=request.user,
        defaults={
            "promotional_amount": account.promotional_balance,
        },
    )

    # ---------------------------------------------------------
    # IF ACCOUNT IS ALREADY LEVEL 2
    # ---------------------------------------------------------
    if account.level >= 2:

        return render(
            request,
            "client/dashboard/upgrade_level_2.html",
            {
                "account": account,
                "claim": claim,
                "already_upgraded": True,
                "projected_balance": account.account_balance,
                "qualifying_deposit_completed": True,
                "level_2_deposit_requirement": level_2_deposit_requirement,
            },
        )

    # =========================================================
    # POST — ACTIVATE LEVEL 2
    # =========================================================
    if request.method == "POST":

        with transaction.atomic():

            # -------------------------------------------------
            # LOCK ACCOUNT
            # -------------------------------------------------
            account = (
                Account.objects
                .select_for_update()
                .get(user=request.user)
            )

            # -------------------------------------------------
            # LOCK CLAIM
            # -------------------------------------------------
            claim = (
                PromotionalCreditClaim.objects
                .select_for_update()
                .get(user=request.user)
            )

            # -------------------------------------------------
            # 1. CHECK ACCOUNT LEVEL
            # -------------------------------------------------
            if account.level >= 2:

                messages.info(
                    request,
                    "Your account is already upgraded to Level 2."
                )

                return redirect("upgrade_level_2")

            # -------------------------------------------------
            # 2. CHECK VERIFICATION
            # -------------------------------------------------
            if not account.is_verified:

                messages.error(
                    request,
                    "Your account must be verified before activating Level 2."
                )

                return redirect("upgrade_level_2")

            # -------------------------------------------------
            # 3. CHECK QUALIFYING DEPOSIT
            # -------------------------------------------------
            qualifying_deposit_completed = Transaction.objects.filter(
                user=request.user,
                transaction_type="deposit",
                status="successful",
                amount__gte=level_2_deposit_requirement,
            ).exists()

            if not qualifying_deposit_completed:

                messages.error(
                    request,
                    (
                        f"You need a successful deposit of at least "
                        f"${level_2_deposit_requirement:,.2f} "
                        f"before activating Level 2."
                    )
                )

                return redirect("upgrade_level_2")

            # -------------------------------------------------
            # 4. CHECK PROMOTIONAL BALANCE
            # -------------------------------------------------
            if account.promotional_balance <= Decimal("0.00"):

                messages.error(
                    request,
                    "There is no promotional balance available to release."
                )

                return redirect("upgrade_level_2")

            # -------------------------------------------------
            # 5. HANDLE CLAIM STATUS
            # -------------------------------------------------
            #
            # Normally a "claimed" status means the promotion
            # has already been transferred.
            #
            # However, we also protect against an inconsistent
            # database state such as:
            #
            # claim.status = "claimed"
            # account.level = 1
            # account.promotional_balance = 12000
            #
            # In that situation, the Account state is treated
            # as authoritative because the promotional balance
            # is still present.
            #
            if claim.status == "claimed":

                if (
                    account.level >= 2
                    and account.promotional_balance <= Decimal("0.00")
                ):
                    messages.info(
                        request,
                        "Your promotional credit has already been released."
                    )

                    return redirect("upgrade_level_2")

                # -------------------------------------------------
                # REPAIR INCONSISTENT CLAIM STATE
                # -------------------------------------------------
                #
                # The claim says "claimed", but the account is still
                # Level 1 and still has promotional funds.
                #
                # Reset the claim state so the legitimate release
                # can proceed.
                #
                claim.status = "pending"
                claim.claimed_amount = Decimal("0.00")
                claim.claimed_at = None

            # -------------------------------------------------
            # 6. CAPTURE PROMOTIONAL AMOUNT
            # -------------------------------------------------
            promotional_amount = account.promotional_balance

            old_balance = account.account_balance

            new_balance = old_balance + promotional_amount

            # -------------------------------------------------
            # 7. MOVE PROMOTIONAL BALANCE INTO MAIN BALANCE
            # -------------------------------------------------
            account.account_balance = new_balance
            account.promotional_balance = Decimal("0.00")

            # -------------------------------------------------
            # 8. UPGRADE ACCOUNT
            # -------------------------------------------------
            account.level = 2
            account.withdrawal_enabled = True

            account.save(
                update_fields=[
                    "account_balance",
                    "promotional_balance",
                    "level",
                    "withdrawal_enabled",
                ]
            )

            # -------------------------------------------------
            # 9. UPDATE PROMOTIONAL CLAIM
            # -------------------------------------------------
            claim.promotional_amount = promotional_amount
            claim.claimed_amount = promotional_amount
            claim.status = "claimed"
            claim.claimed_at = timezone.now()

            claim.save(
                update_fields=[
                    "promotional_amount",
                    "claimed_amount",
                    "status",
                    "claimed_at",
                ]
            )

            # -------------------------------------------------
            # 10. RECORD PROMOTIONAL TRANSACTION
            # -------------------------------------------------
            Transaction.objects.create(
                user=request.user,
                transaction_type="promotion",
                discription="Promotional Credit Released - Level 2 Upgrade",
                amount=promotional_amount,
                status="successful",
                method="Promotional Credit",
            )

        # =====================================================
        # SUCCESS
        # =====================================================

        messages.success(
            request,
            (
                f"Level 2 activated successfully. "
                f"${promotional_amount:,.2f} has been added "
                f"to your account balance."
            )
        )

        return redirect("upgrade_level_2")

    # =========================================================
    # GET PAGE
    # =========================================================

    projected_balance = (
        account.account_balance +
        account.promotional_balance
    )

    return render(
        request,
        "client/dashboard/upgrade_level_2.html",
        {
            "account": account,
            "claim": claim,
            "already_upgraded": False,
            "projected_balance": projected_balance,
            "qualifying_deposit_completed": qualifying_deposit_completed,
            "level_2_deposit_requirement": level_2_deposit_requirement,
        },
    )

# @login_required(login_url="login")
# def upgrade_level_2(request):

#     account = Account.objects.get(user=request.user)

#     level_2_deposit_requirement = LEVEL_2_DEPOSIT_REQUIREMENT

#     qualifying_deposit_completed = Transaction.objects.filter(
#         user=request.user,
#         transaction_type="deposit",
#         status="successful",
#         amount__gte=level_2_deposit_requirement,
#     ).exists()

#     claim, created = PromotionalCreditClaim.objects.get_or_create(
#         user=request.user,
#         defaults={
#             "promotional_amount": account.promotional_balance,
#         },
#     )

#     if account.level >= 2:

#         return render(
#             request,
#             "client/dashboard/upgrade_level_2.html",
#             {
#                 "account": account,
#                 "claim": claim,
#                 "already_upgraded": True,
#                 "projected_balance": account.account_balance,
#                 "qualifying_deposit_completed": True,
#                 "level_2_deposit_requirement": level_2_deposit_requirement,
#             },
#         )

#     if request.method == "POST":

#         with transaction.atomic():

#             account = (
#                 Account.objects
#                 .select_for_update()
#                 .get(user=request.user)
#             )

#             claim = (
#                 PromotionalCreditClaim.objects
#                 .select_for_update()
#                 .get(user=request.user)
#             )

#             # -----------------------------
#             # VERIFICATION
#             # -----------------------------

#             if not account.is_verified:

#                 messages.error(
#                     request,
#                     "Your account must be verified before activating Level 2."
#                 )

#                 return redirect("upgrade_level_2")

#             # -----------------------------
#             # QUALIFYING DEPOSIT
#             # -----------------------------

#             qualifying_deposit_completed = Transaction.objects.filter(
#                 user=request.user,
#                 transaction_type="deposit",
#                 status="successful",
#                 amount__gte=level_2_deposit_requirement,
#             ).exists()

#             if not qualifying_deposit_completed:

#                 messages.error(
#                     request,
#                     f"You need a successful deposit of at least "
#                     f"${level_2_deposit_requirement:,.2f} before activating Level 2."
#                 )

#                 return redirect("upgrade_level_2")

#             # -----------------------------
#             # CLAIM CHECK
#             # -----------------------------

#             if claim.status == "claimed":

#                 messages.info(
#                     request,
#                     "Your promotional credit has already been released."
#                 )

#                 return redirect("upgrade_level_2")

#             # -----------------------------
#             # PROMOTIONAL BALANCE CHECK
#             # -----------------------------

#             promotional_amount = account.promotional_balance

#             if promotional_amount <= Decimal("0.00"):

#                 messages.error(
#                     request,
#                     "There is no promotional balance available to release."
#                 )

#                 return redirect("upgrade_level_2")

#             # -----------------------------
#             # RELEASE PROMOTIONAL CREDIT
#             # -----------------------------

#             account.account_balance = (
#                 account.account_balance + promotional_amount
#             )

#             account.promotional_balance = Decimal("0.00")
#             account.level = 2
#             account.withdrawal_enabled = True

#             account.save(
#                 update_fields=[
#                     "account_balance",
#                     "promotional_balance",
#                     "level",
#                     "withdrawal_enabled",
#                 ]
#             )

#             # -----------------------------
#             # UPDATE CLAIM
#             # -----------------------------

#             claim.promotional_amount = promotional_amount
#             claim.claimed_amount = promotional_amount
#             claim.status = "claimed"
#             claim.claimed_at = timezone.now()

#             claim.save(
#                 update_fields=[
#                     "promotional_amount",
#                     "claimed_amount",
#                     "status",
#                     "claimed_at",
#                 ]
#             )

#             # -----------------------------
#             # RECORD PROMOTIONAL TRANSACTION
#             # -----------------------------

#             Transaction.objects.create(
#                 user=request.user,
#                 transaction_type="promotion",
#                 discription="Promotional Credit Released - Level 2 Upgrade",
#                 amount=promotional_amount,
#                 status="successful",
#                 method="Promotional Credit",
#             )

#         messages.success(
#             request,
#             f"Level 2 activated successfully. "
#             f"${promotional_amount:,.2f} has been added to your account balance."
#         )

#         return redirect("upgrade_level_2")

#     projected_balance = (
#         account.account_balance +
#         account.promotional_balance
#     )

#     return render(
#         request,
#         "client/dashboard/upgrade_level_2.html",
#         {
#             "account": account,
#             "claim": claim,
#             "already_upgraded": False,
#             "projected_balance": projected_balance,
#             "qualifying_deposit_completed": qualifying_deposit_completed,
#             "level_2_deposit_requirement": level_2_deposit_requirement,
#         },
#     )



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
        account.total_invested += int(amount)
        account.save()
        

        Investment.objects.create(user=request.user, plan=plan, amount=amount,returns=expected_returns, due_date=due_date)
        
        
        
        
        # Withdrawal.objects.create(user=request.user, amount=amount, Withdrawal_method=Withdrawal_method, address=address)
        
        message_s = "investment Successful"
        
        
        
        

    


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
        # amount = request.POST.get('amount', None)
        raw_amount = request.POST.get("amount", "").replace(",", "").strip()
        amount = Decimal(raw_amount)
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
        
        
        
    
    context = {
        'account_balance': round(account.account_balance,2),
        # "plan":Plan.objects.filter(plan_name=plan).first(),
        'locked_investments': locked_investments,
        "payment_gates": Paymentgateway.objects.all(),
        "message":message_s,
        "deposits":deposits_list
    }
        
        
   
    
    return render(request, 'client/dashboard/deposit.html', context)







# @login_required(redirect_field_name='withdraw', login_url='login')
# def withdraw(request):
    
#     account = Account.objects.filter(user=request.user).first()
#     # locked = Investment.objects.filter(user=request.user, invest_status='active').aggregate(Sum('amount'))["amount__sum"]
#     locked_investments = Investment.objects.filter(user=request.user, is_matured=False).aggregate(Sum('amount'))['amount__sum'] or 0.00
#     withdrawals =  Withdrawal.objects.filter(user=request.user)
#     message_s = ""
    
#     if request.method == "POST":
#         amount = float(request.POST.get('amount', None))
#         Withdrawal_method = request.POST.get('payment_method', None)
#         address = request.POST.get('address', None)
        
        
#         # print(amount > account.account_balance)
        
#         # if amount > account.account_balance:
#         #     message_s = "Insufficient funds."
            
        
#         # elif amount < 10:
            
#         #     message_s = "minmum amount for withdrawal 10 ."

#         if not account.withdrawal_enabled:
#             message_s = "Withdrawal is currently unavailable for your account."
#         elif amount > account.account_balance:
#             message_s = "Insufficient funds."
#         elif amount < 10:
#             message_s = "Minimum withdrawal amount is $10."

#         else:
            
#             Withdrawal.objects.create(user=request.user, amount=amount, Withdrawal_method=Withdrawal_method, address=address)
            
#             message_s = "Your withdrawal is in progress"
        





        


    
#     context = {
#         'account_balance': round(account.account_balance,2),
#         # "plans":Plan.objects.all(),
#         "c_paymentgates": clientPaymentgateway.objects.all(),
#         'locked_investments': locked_investments,
#         "message":message_s,
#         "withdrawals":withdrawals
        
        
#     }
    
    
#     return render(request, 'client/dashboard/withdraw.html', context)



# @login_required(redirect_field_name='withdraw', login_url='login')
# def withdraw(request):

#     account = Account.objects.filter(user=request.user).first()

#     locked_investments = (
#         Investment.objects
#         .filter(user=request.user, is_matured=False)
#         .aggregate(Sum('amount'))['amount__sum']
#         or Decimal("0.00")
#     )

#     message_s = ""

#     if request.method == "POST":

#         # Get form values
#         raw_amount = request.POST.get('amount', '').replace(',', '').strip()
#         withdrawal_method = request.POST.get('payment_method', '').strip()
#         address = request.POST.get('address', '').strip()

#         # Validate amount
#         try:
#             amount = Decimal(raw_amount)
#         except (InvalidOperation, TypeError):
#             amount = Decimal("0.00")
#             message_s = "Please enter a valid withdrawal amount."

#         if not message_s:

#             with transaction.atomic():

#                 # Lock the account during the withdrawal check
#                 account = Account.objects.select_for_update().get(
#                     user=request.user
#                 )

#                 # ==========================================
#                 # WITHDRAWAL ELIGIBILITY
#                 # ==========================================

#                 if not account.withdrawal_enabled:

#                     message_s = (
#                         "Withdrawal is currently unavailable for your account. "
#                         "Please complete the required account eligibility steps."
#                     )

#                 elif amount < Decimal("10.00"):

#                     message_s = "Minimum withdrawal amount is $10."

#                 elif amount > account.account_balance:

#                     message_s = "Insufficient funds."

#                 elif not withdrawal_method:

#                     message_s = "Please select a withdrawal method."

#                 elif not address:

#                     message_s = "Please enter your payment address."

#                 else:

#                     # ==========================================
#                     # CREATE WITHDRAWAL
#                     # ==========================================

#                     Withdrawal.objects.create(
#                         user=request.user,
#                         amount=amount,
#                         Withdrawal_method=withdrawal_method,
#                         address=address,
#                     )

#                     message_s = "Your withdrawal request is in progress."

#     withdrawals = Withdrawal.objects.filter(
#         user=request.user
#     ).order_by('-timestamp')

#     # context = {
#     #     'account_balance': account.account_balance.quantize(
#     #         Decimal("0.01")
#     #     ),
#     #     'c_paymentgates': clientPaymentgateway.objects.all(),
#     #     'locked_investments': locked_investments,
#     #     'message': message_s,
#     #     'withdrawals': withdrawals,
#     # }

#     context = {
#     'account_balance': account.account_balance.quantize(
#         Decimal("0.01")
#     ),
#     'account_level': account.level,
#     'withdrawal_enabled': account.withdrawal_enabled,
#     'is_verified': account.is_verified,
#     'promotional_balance': account.promotional_balance,
#     'c_paymentgates': clientPaymentgateway.objects.all(),
#     'locked_investments': locked_investments,
#     'message': message_s,
#     'withdrawals': withdrawals,
#     }

#     return render(
#         request,
#         'client/dashboard/withdraw.html',
#         context
#     )


@login_required(redirect_field_name='withdraw', login_url='login')
def withdraw(request):

    account = Account.objects.filter(user=request.user).first()

    locked_investments = (
        Investment.objects
        .filter(
            user=request.user,
            is_matured=False
        )
        .aggregate(Sum('amount'))['amount__sum']
        or Decimal("0.00")
    )

    message_s = ""

    if request.method == "POST":

        # ==========================================
        # GET FORM VALUES
        # ==========================================

        raw_amount = (
            request.POST.get('amount', '')
            .replace(',', '')
            .strip()
        )

        withdrawal_method = (
            request.POST.get('payment_method', '')
            .strip()
        )

        address = (
            request.POST.get('address', '')
            .strip()
        )

        # ==========================================
        # VALIDATE AMOUNT
        # ==========================================

        try:
            amount = Decimal(raw_amount)

        except (InvalidOperation, TypeError):
            amount = Decimal("0.00")
            message_s = "Please enter a valid withdrawal amount."

        # Prevent negative values and malformed decimals
        if not message_s and amount <= Decimal("0.00"):
            message_s = "Please enter a valid withdrawal amount."

        # ==========================================
        # PROCESS WITHDRAWAL
        # ==========================================

        if not message_s:

            with transaction.atomic():

                # Lock the account so two withdrawal
                # requests cannot race against the same balance.
                account = (
                    Account.objects
                    .select_for_update()
                    .get(user=request.user)
                )

                # ==========================================
                # WITHDRAWAL ELIGIBILITY
                # ==========================================

                if not account.withdrawal_enabled:

                    message_s = (
                        "Withdrawal is currently unavailable "
                        "for your account. Please complete the "
                        "required account eligibility steps."
                    )

                elif amount < Decimal("10.00"):

                    message_s = (
                        "Minimum withdrawal amount is $10."
                    )

                elif amount > account.account_balance:

                    message_s = "Insufficient funds."

                elif not withdrawal_method:

                    message_s = (
                        "Please select a withdrawal method."
                    )

                elif not address:

                    message_s = (
                        "Please enter your payment address."
                    )

                else:

                    # ==========================================
                    # CREATE WITHDRAWAL REQUEST
                    # ==========================================

                    Withdrawal.objects.create(
                        user=request.user,
                        amount=amount,
                        Withdrawal_method=withdrawal_method,
                        address=address,
                    )

                    message_s = (
                        "Your withdrawal request is in progress."
                    )

    # ==========================================
    # WITHDRAWAL HISTORY
    # ==========================================

    withdrawals = (
        Withdrawal.objects
        .filter(user=request.user)
        .order_by('-timestamp')
    )

    # ==========================================
    # PAGE CONTEXT
    # ==========================================

    context = {
        'account_balance': account.account_balance.quantize(
            Decimal("0.01")
        ),
        'account_level': account.level,
        'withdrawal_enabled': account.withdrawal_enabled,
        'is_verified': account.is_verified,
        'promotional_balance': account.promotional_balance,
        'c_paymentgates': clientPaymentgateway.objects.all(),
        'locked_investments': locked_investments,
        'message': message_s,
        'withdrawals': withdrawals,
    }

    return render(
        request,
        'client/dashboard/withdraw.html',
        context
    )






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