# from django.core.management.base import BaseCommand
# from django.utils.timezone import now
# from client.models import Investment, Account


# class Command(BaseCommand):
#     help = "Transfer matured investments to users' main balance."

#     def handle(self, *args, **kwargs):
#         # Fetch only active investments that are not yet matured
#         matured_investments = Investment.objects.filter(is_matured=False)

#         for investment in matured_investments:
#             if investment.has_matured():
#                 try:
#                     # Calculate total return including 7% daily
#                     total_return = investment.calculate_total_return()

#                     # Transfer funds to user's account balance
#                     account = Account.objects.get(user=investment.user)
#                     account.account_balance += total_return
#                     account.save()

#                     # Mark investment as matured
#                     investment.is_matured = True
#                     investment.save()

#                     self.stdout.write(
#                         self.style.SUCCESS(
#                             f"Transferred ${total_return} for user {investment.user.email}"
#                         )
#                     )
#                 except Account.DoesNotExist:
#                     self.stderr.write(
#                         self.style.ERROR(
#                             f"Account for user {investment.user.email} does not exist."
#                         )
#                     )

#         self.stdout.write(self.style.SUCCESS("Matured investments processed successfully."))



from django.core.management.base import BaseCommand
from django.utils.timezone import now
from client.models import Investment, Account


class Command(BaseCommand):
    help = "Move matured investment total returns to user balance."

    def handle(self, *args, **kwargs):
        investments = Investment.objects.filter(is_matured=False)

        for investment in investments:
            if investment.has_matured():

                total_return = investment.calculate_total_return()

                # Profit = returns minus the original invested amount
                profit_only = total_return - investment.amount

                account = Account.objects.get(user=investment.user)
                account.account_balance += total_return
                account.total_profit += profit_only  # <-- ADD THIS
                account.save()

                investment.is_matured = True
                investment.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Transferred ${total_return} to {investment.user.email}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Matured investments processed successfully."))
