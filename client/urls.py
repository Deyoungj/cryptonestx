from django.urls import path

from . import views





urlpatterns = [
    path('', views.home, name='home' ),
    path('about/', views.about, name='about'),
    path('affiliate/', views.affliate, name='affiliate'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('referral/', views.referral, name='referral'),
    path('deposit/', views.deposit, name='deposit'),
    path('overview/', views.overview, name='overview'),
    path('invest/', views.invest, name='invest'),
    path('invest_form/<str:plan>/', views.invest_form, name='invest_form'),
    path('profile/', views.profile, name='profile'),

    path('withdraw/', views.withdraw, name='withdraw'),
    # path('mailer/', views.mailer, name='mailer'),

    # path('blog/', views.blog, name='blog'),
    # path('blog_details/', views.blog_details, name='blog_details'),
]
