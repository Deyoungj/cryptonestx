# from django.core.management.base import BaseCommand
# from django.utils.timezone import now
# from client.models import Investment, Account

# class Command(BaseCommand):
#     help = "Add daily returns to users' balances."

#     def handle(self, *args, **kwargs):
#         today = now().date()
#         active_investments = Investment.objects.filter(is_matured=False)

#         for investment in active_investments:
#             # Check if today's return hasn't been added
#             if investment.last_return_date != today:
#                 daily_return = investment.calculate_daily_return()

#                 # Update user's account balance
#                 account, created = Account.objects.get_or_create(user=investment.user)
#                 account.account_balance += daily_return
#                 account.save()

#                 # Update investment's last return date and cumulative returns
#                 investment.returns += daily_return
#                 investment.last_return_date = today
#                 investment.save()

#                 self.stdout.write(f"Added ${daily_return} to {investment.user.email}'s balance.")

#         self.stdout.write("Daily returns processed successfully.")



from django.core.management.base import BaseCommand
from django.utils.timezone import now
from client.models import Investment, Account
from decimal import Decimal



class Command(BaseCommand):
    help = "Add 10% daily returns to all active investments."

    def handle(self, *args, **kwargs):
        today = now().date()
        active_investments = Investment.objects.filter(is_matured=False)

        for investment in active_investments:
            if investment.last_return_date == today:
                continue


            get_percent = str(investment.plan.percent/100)

            daily_return = investment.amount * Decimal(get_percent)  # 10% daily

            # Update user account
            account, _ = Account.objects.get_or_create(user=investment.user)
            account.account_balance += daily_return
            account.total_profit += daily_return  # <-- ADD THIS
            account.save()

            # Update investment tracking
            investment.returns += daily_return
            investment.last_return_date = today
            investment.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Added ${daily_return} to {investment.user.email}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Daily returns processed successfully."))

