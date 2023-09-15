from django.shortcuts import render

# Create your views here.

def Index(request):
    return render(request, 'app/index.html')

def Login(request):
    return render(request, 'app/account/login.html')

def Register(request):
    return render(request, 'app/account/register.html')

def Profile(request):
    return render(request, 'app/account/profile.html')

def Logout(request):
    return render(request, 'app/account/logout.html')

def Deposit(request):
    return render(request, 'app/transaction/deposit.html')

def Withdraw(request):
    return render(request, 'app/transaction/withdraw.html')

def Deposits(request):
    return render(request, 'app/history/deposits.html')

def Withdrawals(request):
    return render(request, 'app/history/withdraws.html')

def Contact(request):
    return render(request, 'app/contact.html')

def About(request):
    return render(request, 'app/about.html')

def Notification(request):
    return render(request, 'app/alert/notification.html')