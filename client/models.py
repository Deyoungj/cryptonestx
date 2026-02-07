from django.db import models
from user.models import CustomUser
# from custom_admin.models import Plan
from datetime import datetime
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal 
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Custom User Model
User = settings.AUTH_USER_MODEL

status = [
    ("Pending", "Pending"),
    ("Approved", "Approved"),
]


invest_status = [
    ("active", "active"),
    ("Completed", "Completed"),
]



class Plan(models.Model):
   plan_name  = models.CharField( max_length=200)
   percent = models.IntegerField()
   period = models.CharField(max_length=150)
   period_length =  models.IntegerField(default=0)
   minimum_amount = models.CharField(max_length=50)
   maximum_amount = models.CharField(max_length=50)
#    total_return = models.IntegerField()
   # plan_image = models.CharField(max_length=900, default="")
   plan_image = models.ImageField(upload_to='plan_images/', null=True, blank=True, default='plan_images/default.jpg')

   def __str__(self):
       return f'{self.plan_name}' 





class Paymentgateway(models.Model):
    name = models.CharField(max_length=30,unique=True)
    address = models.CharField(max_length=100)



    def __str__(self) -> str:
        return f'payment name: {self.name}' 



class clientPaymentgateway(models.Model):
    name = models.CharField(max_length=30,unique=True)
    


    def __str__(self) -> str:
        return f'client payment name: {self.name}' 
    
    

class Account(models.Model):
   user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
   account_balance = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
   total_profit = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
   total_invested = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
   referral_bonus = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)

   def __str__(self):
      return f'user: {self.user.full_name} | Amount: ${self.account_balance}'





class Deposit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ], default='pending')
    
    
    def __str__(self):
        return f'user: {self.user.full_name} | Amount: ${self.amount}'
    
    
    def save(self, *args, **kwargs):
        
        # Check if the deposit status has changed
        if self.pk:  # Check if this is an existing deposit
            original = Deposit.objects.get(pk=self.pk)
            if original.status != self.status and self.status == 'successful':
                self.handle_successful_deposit()
                self.send_success_email()  # ✅ email sent ONCE
        
        
        if not self.reference:
            self.reference = self.generate_unique_reference()
        
        
        # Handle referral bonus if the deposit is successful
        if self.status == 'successful':
            self.apply_referral_bonus()
            
        super().save(*args, **kwargs)
        
        


    def send_success_email(self):
        subject = "Deposit Successful"

        # HTML email template (recommended)
        try:

            html_content = render_to_string("client/dashboard/mail_temp/deposit_success.html", {
                "user": self.user,
                "amount": self.amount,
                "payment_method": self.payment_method,
                "reference": self.reference,
                "date": self.timestamp,
            })

            # Plain text fallback
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.user.email],
            )

            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)  

        except Exception as e:
            print(f"Error sending deposit success email: {e}")
        
        
            
    def generate_unique_reference(self):
        while True:
            reference = get_random_string(length=10)  # Adjust the length as needed
            if not Transaction.objects.filter(transction_id=reference).exists():
                return reference
            
            

    def apply_referral_bonus(self):
        """Grant referral bonus if applicable."""
        referrer = self.user.referrer
        if referrer:
            # Calculate 10% referral bonus
            bonus_percentage = Decimal('0.10')
            bonus_amount = self.amount * bonus_percentage
            
            # Update the ReferralBonus record or create a new one
            referral_bonus, created = ReferralBonus.objects.get_or_create(
                referrer=referrer,
                referred=self.user,
                defaults={'amount': Decimal('0.00'), 'deposit': None}
            )

            referral_bonus.amount += bonus_amount
            referral_bonus.deposit = self
            referral_bonus.save()
            
            # Update referrer's total referral bonus balance in Account
            referrer_account, _ = Account.objects.get_or_create(user=referrer)
            referrer_account.referral_bonus += bonus_amount
            referrer_account.save()





            subject = "Referral Bonus Earned"

            # HTML email template (recommended)
            try:

                html_content = render_to_string("client/dashboard/mail_temp/Referral.html", {
                    "user": self.user,
                    "referrer": referrer.full_name,
                    "bonus_amount": bonus_amount,


                })

                # Plain text fallback
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[self.referrer.email],
                )

                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)  

            except Exception as e:
                print(f"Error sending deposit success email: {e}")









            
    
    def handle_successful_deposit(self):
        # Update the account balance
        try:
            account = Account.objects.get(user=self.user)
            account.account_balance += self.amount
            account.save()
        except Account.DoesNotExist:
            raise ValueError(f"Account for user {self.user.email} does not exist.")

        # Update or create a transaction entry
        Transaction.objects.update_or_create(
            transction_id=self.reference,
            defaults={
                'user': self.user,
                'transaction_type': 'deposit',
                'discription': f"Deposit of ${self.amount} via {self.payment_method}",
                'amount': self.amount,
                'status': 'successful',
                'method': self.payment_method,
                'timestamp': self.timestamp,
            }
        )
            
    




class Withdrawal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    Withdrawal_method = models.CharField(max_length=100, default="btc")
    address = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ], default='pending')
    
    withdrawal_type = models.CharField(max_length=100, choices=[
        ('referral_bonus', 'referral_bonus'),
        ('account_balance', 'account_balance')], default='account_balance')
    
    
    
    def __str__(self):
        return f'user: {self.user.full_name} | Amount: ${self.amount}'
    

    
    def save(self, *args, **kwargs):
        
        # Check if the deposit status has changed
        if self.pk:  # Check if this is an existing deposit
            original = Withdrawal.objects.get(pk=self.pk)
            if original.status != self.status and self.status == 'successful':
                self.handle_successful_withdrawal()
                self.send_success_email()  # ✅ email sent ONCE
        
        
        if not self.reference:
            self.reference = self.generate_unique_reference()
        
        
        
            
        super().save(*args, **kwargs)
    
    
    
    
    def generate_unique_reference(self):
        while True:
            reference = get_random_string(length=10)  # Adjust the length as needed
            if not Transaction.objects.filter(transction_id=reference).exists():
                return reference
    



    def send_success_email(self):
        subject = "Withdrawal Successful"

        # HTML email template (recommended)
        try:

            html_content = render_to_string("client/dashboard/mail_temp/withdraw_success.html", {
                "user": self.user,
                "amount": self.amount,
                "method": self.Withdrawal_method,
                "address": self.address,
                "reference": self.reference,
                "date": self.timestamp,
            })

            # Plain text fallback
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.user.email],
            )

            email.attach_alternative(html_content, "text/html")
            email.send()  

        except Exception as e:
            print(f"Error sending withdrawal success email: {e}")




    def handle_successful_withdrawal(self):
        # Update the account balance
        try:
            account = Account.objects.get(user=self.user)
            
            if self.withdrawal_type == "account_balance":
                account.account_balance -= self.amount
                
            if self.withdrawal_type == "referral_bonus":
                account.referral_bonus -= self.amount

            

                
                
            account.save()
            
            
        except Account.DoesNotExist:
            raise ValueError(f"Account for user {self.user.email} does not exist.")

        # Update or create a transaction entry
        Transaction.objects.update_or_create(
            transction_id=self.reference,
            defaults={
                'user': self.user,
                'transaction_type': 'withdrawal',
                'discription': f"withdrawal of ${self.amount} via {self.Withdrawal_method}",
                'amount': self.amount,
                'status': 'successful',
                'method': self.Withdrawal_method,
                'timestamp': self.timestamp,
            }
        )
    










class Transaction(models.Model):
    
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('investment', 'Investment'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    discription = models.CharField(max_length=200)
    transction_id = models.CharField(max_length=200)
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ], default='pending')
    
    method = models.CharField(max_length=100)
    timestamp = models.DateTimeField( default=now)

    def save(self, *args, **kwargs):
            if not self.transction_id:
                self.transction_id = self.generate_unique_transaction_id()
            super().save(*args, **kwargs)

    def generate_unique_transaction_id(self):
        while True:
            transction_id = get_random_string(length=10)  # Adjust the length as needed
            if not Transaction.objects.filter(transction_id=transction_id).exists():
                return transction_id


    def __str__(self):
        return f'Discription: {self.discription}   | User: {self.user.email}'






class Investment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="investments")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    investment_id = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    returns = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    # payment_gateway = models.CharField(max_length=100)
    lock_period = models.DurationField(blank=True, null=True)  # Lock duration (e.g., 14 days, 1 month)
    is_matured = models.BooleanField(default=False)  # True when the lock period ends

    start_date = models.DateField(default=now)
    due_date = models.DateField()
    last_return_date = models.DateField(null=True, blank=True)  # New field to track last return date


    def save(self, *args, **kwargs):
        
        if not self.investment_id:
            self.investment_id = self.generate_unique_transaction_id()
            
        # Set the lock period based on the selected plan
        # if not self.lock_period:
        #     if self.plan == '14_days':
        #         self.lock_period = timedelta(days=14)
        #     elif self.plan == '1_month':
        #         self.lock_period = timedelta(days=30)
        
        if not self.lock_period and not self.due_date:
            # Use `Plan` to set the lock period and calculate due date
            self.lock_period = timedelta(days=self.plan.period_length)
            self.due_date = self.start_date + self.lock_period
                    
        super().save(*args, **kwargs)
        
        
        
    def has_matured(self):
        """Check if the investment has matured based on current time."""
        return now().date() >= self.due_date
    
    
    def calculate_total_return(self):
        """Calculate the total return with 10% daily increase."""
        days_invested = (now().date() - self.start_date).days
        daily_rate = Decimal('0.10')  # Use Decimal for precise arithmetic
        base = Decimal('1') + daily_rate  # Convert 1 to Decimal
        if days_invested > 0:
            total_return = self.amount * (base ** Decimal(days_invested))
        else:
            total_return = self.amount
        return round(total_return, 2)
    
    
    def calculate_daily_return(self):
        daily_rate = Decimal('0.02')  # 7% daily return
        return round(self.amount * daily_rate, 2)


    def generate_unique_transaction_id(self):
        while True:
            investment_id = get_random_string(length=10)  # Adjust the length as needed
            if not Investment.objects.filter(investment_id=investment_id).exists():
                return investment_id
            
            
    def handle_successful_investment(self):
        # Update the account balance
        try:
            account = Account.objects.get(user=self.user)
            account.account_balance -= self.amount
            account.save()
        except Account.DoesNotExist:
            raise ValueError(f"Account for user {self.user.email} does not exist.")

        # Update or create a transaction entry
        Transaction.objects.update_or_create(
            transction_id=self.investment_id,
            defaults={
                'user': self.user,
                'transaction_type': 'Investment',
                'discription': f"investment of ${self.amount} via account balance",
                'amount': self.amount,
                'status': 'successful',
                'method': "account balance",
                'timestamp': self.start_date,
            }
        )
    


    def __str__(self):
        return f'Plan: {self.plan}  | User: {self.user.email}'




class ReferralBonus(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referral_bonuses")
    referred = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referred_bonuses")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    deposit = models.OneToOneField(Deposit, on_delete=models.CASCADE, related_name="referral_bonus", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Referral Bonus: {self.referrer.email} -> {self.referred.email} (${self.amount})"
    
    
    
    