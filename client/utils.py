from datetime import timedelta
from django.db.models import Sum
from django.utils.timezone import now
from .models import ReferralBonus

def get_monthly_referral_profit(user):
    # Get the first and last day of the current month
    start_of_month = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(seconds=1)

    # Filter referral bonuses within the current month
    total_monthly_reward = ReferralBonus.objects.filter(
        referrer=user,
        created_at__gte=start_of_month,
        created_at__lte=end_of_month,
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00

    return total_monthly_reward


