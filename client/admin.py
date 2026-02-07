from django.contrib import admin
from .models import Account, Deposit, Plan, Paymentgateway, clientPaymentgateway,Withdrawal, Investment, Transaction, ReferralBonus





@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'payment_method', 'status', 'timestamp', 'reference']
    search_fields = ['user__email', 'reference']
    list_filter = ['status', 'payment_method']

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'Withdrawal_method', 'status', 'timestamp']
    search_fields = ['user__email', 'reference']
    list_filter = ['status', 'Withdrawal_method']

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'plan', 'amount', 'returns', 'investment_id', 'start_date', 'due_date', 'lock_period', 'is_matured']
    search_fields = ['user__email', 'investment_id']
    list_filter = [ 'plan', 'is_matured']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'transaction_type', 'amount', 'transction_id', 'method', 'status', 'timestamp']
    search_fields = ['user__email', 'transction_id']
    list_filter = ['transaction_type', 'status']
    
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'account_balance', 'total_profit', 'total_invested', 'referral_bonus']
    search_fields = ['user__email']
    list_filter = ['user__email']
    
    
@admin.register(ReferralBonus)
class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ['id', 'referrer', 'referred', 'amount', 'deposit', 'created_at']
    search_fields = ['referrer__email', 'referred__email']
    list_filter = ['referred__email']
    

# class DepositAdmin(admin.ModelAdmin):
#     search_fields = ['user__email']
    
    
# class AccountAdmin(admin.ModelAdmin):
#     search_fields = ['user__email']
    

# admin.site.register(Deposit, DepositAdmin)
# admin.site.register(Account, AccountAdmin)
admin.site.register(Plan)
admin.site.register(Paymentgateway)
admin.site.register(clientPaymentgateway)