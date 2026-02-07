from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager
from django.utils.crypto import get_random_string
from PIL import Image  
import os

from decimal import Decimal


class CustomUser(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100,  blank=True)
    email = models.EmailField(unique=True)
    # profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, default='profile_pics/default.jpg')
    date_joined = models.DateTimeField(auto_now_add=True)
    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    referrer = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name="referred_users")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)  # Add this field
    

    USERNAME_FIELD = "email"

    objects = CustomUserManager()
    
    def __str__(self) -> str:
        return self.email

    class Meta:
        ordering = ('-date_joined',)


    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = get_random_string(length=10)
        super().save(*args, **kwargs)
        
        # Automatically create a ReferralBonus record for the referrer if applicable
        from client.models import ReferralBonus
        if self.referrer:
            ReferralBonus.objects.get_or_create(
                referrer=self.referrer,
                referred=self,
                defaults={'amount': Decimal('0.00'), 'deposit': None}  # Initialize with 0 bonus
            )
    
        
    
        
        


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, default='profile_pics/default.jpg')
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=100,  blank=True)
    address = models.CharField(max_length=150, blank=True)
    state = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=150, blank=True)
    zip_code = models.CharField(max_length=100,  blank=True)
   
    
    

    def __str__(self) -> str:
        return f"full name: {self.user.full_name} >>>>> Email: {self.user.email} "

    
    
    def resize_image(self):
        img_path = self.profile_picture.path
        img = Image.open(img_path)

        # Define max size (e.g., 300x300 pixels)
        max_size = (300, 300)
        img.thumbnail(max_size, Image.ANTIALIAS)

        # Overwrite the image with the resized version
        img.save(img_path, optimize=True, quality=85)

