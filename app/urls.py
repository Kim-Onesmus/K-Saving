from django.urls import path
from . import views

urlpatterns = [
    path('index', views.Index, name='index'),
    path('login', views.Login, name='login'),
    path('register', views.Register, name='register'),
    path('profile', views.Profile, name='profile'),
    path('logout', views.Logout, name='logout'),
    
    path('deposit', views.Deposit, name='deposit'),
    path('withdraw', views.Withdraw, name='withdraw'),
    
    path('deposits', views.Deposits, name='deposits'),
    path('withdraws', views.Withdrawals, name='withdraws'),
    
    path('contact', views.Contact, name='contact'),
    path('about', views.About, name='about'),
    
    path('', views.Notification, name='notification'),
]