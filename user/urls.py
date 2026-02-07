from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('register/', views.register, name='register'),
    path('referral_signup/<str:referral_code>/', views.referral_signup, name='referral_signup'),
    path('emailVerification/<uidb64>/<token>', views.activate, name='activate'),
    path('login/', views.login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('change_password/<uidb64>/<token>', views.password_change, name='password_change'),
    path('password_reset_confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    # path('registration_success/', views.register_success, name='register_success'),
   
]


# if settings.DEBUG:

#     urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)