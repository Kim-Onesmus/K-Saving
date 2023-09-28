from django.urls import path
from . import views

urlpatterns = [
    path('index', views.Index, name='index'),
    path('login', views.Login, name='login'),
    path('', views.Register, name='register'),
    path('verification', views.Verification, name='verification'),
    path('profile', views.Profile, name='profile'),
    path('logout', views.Logout, name='logout'),
    
    path('deposit', views.Deposit, name='deposit'),
    path('access/token', views.getAccessToken, name='get_mpesa_access_token'),
    path('c2b/register', views.register_urls, name="register_mpesa_validation"),
    path('c2b/confirmation', views.confirmation, name="confirmation"),
    path('c2b/validation', views.validation, name="validation"),
    path('c2b/callback', views.call_back, name="call_back"),
    path('withdraw', views.Withdraw, name='withdraw'),
    
    path('deposits/<str:pk>/', views.Deposits, name='deposits'),
    path('withdraws', views.Withdrawals, name='withdraws'),
    
    path('contact', views.Contact, name='contact'),
    path('about', views.About, name='about'),
    
    path('notification', views.Notification, name='notification'),
]