from django.db.models.signals import post_save
from django.core.mail import EmailMessage
from .models import CustomUser, Profile
from client.models import Account
from django.dispatch import receiver
from django.conf import settings


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        account = Account.objects.create(user=instance)
        profile.save()
        account.save()

        


    

# @receiver(post_save, sender=CustomUser)
# def save_profile(sender, instance, **kwargs):
        
#     instance.profile.save()