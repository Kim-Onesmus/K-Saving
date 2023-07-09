from django.urls import path
from . import views

urlpatterns = [
    path('index', views.Index, name='index'),
    path('', views.Login, name='login'),
    path('register', views.Register, name='register'),
    path('verification', views.Verification, name='verification'),
    path('setpassword', views.setPassword, name='setPassword'),
    path('profile', views.Profile, name='profile'),
    path('logout', views.Logout, name='logout'),
    
    path('deposit', views.Deposit, name='deposit'),
    path('withdraw', views.Withdraw, name='withdraw'),
    
    path('deposits', views.Deposits, name='deposits'),
    path('withdraws', views.Withdrawals, name='withdraws'),
    
    path('contact', views.Contact, name='contact'),
    path('about', views.About, name='about'),
    
    path('notification', views.Notification, name='notification'),
]