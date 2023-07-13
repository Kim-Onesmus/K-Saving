from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User, auth
from . models import Client, ContactUs
from . forms import ClientForm


def Index(request):
    return render(request, 'app/index.html')

def Register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password1 = request.POST['password1']
        
        if password == password1:
            if Client.objects.filter(username=username).exists():
                messages.info(request, 'Phone number already exists')
                return redirect('/')
            elif Client.objects.filter(email=email).exists():
                messages.info(request, 'Email taken')
                return redirect('/')
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
                user.save()
                
                client_details = Client.objects.create(user=user, first_name=first_name, last_name=last_name, email=email, username=user.username)
                client_details.save()
                
                messages.info(request, 'Account created')
                return redirect('login')
                
        else:
            messages.info(request, 'Passwords dont match')
            return redirect('/')
    else:
        return render(request, 'app/account/register.html')
    return render(request, 'app/account/register.html')

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.info(request, 'Welcome back')
            return redirect('index')
        else:
            messages.error(request, 'Invalid credetials')
            return redirect('login')
        
    else:
        return render(request, 'app/account/login.html')
    return render(request, 'app/account/login.html')

def Verification(request):
    return render(request, 'app/account/code.html')

def Profile(request):
    user = request.user
    client = user
    form = ClientForm(instance=client)
    password_form = PasswordChangeForm(request.user)
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES, instance=client)
        password_form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Profile edited')
            return redirect('profile')

        if password_form.is_valid():
            password_form.save()
            messages.info(request, 'Profile information updated')
            return redirect('login')
    
    context = {'form':form, 'password_form':password_form}
    return render(request, 'app/account/profile.html', context)

def Logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.info(request, 'Logged Out Successfully')
        return redirect('login')
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
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        messange = request.POST['messange']
        
        contact_details = ContactUs.objects.create(name=name, email=email, subject=subject, messange=messange)
        contact_details.save()
        messages.info(request, 'Messange sent')
        return redirect('contact')
    return render(request, 'app/contact.html')

def About(request):
    return render(request, 'app/about.html')

def Notification(request):
    return render(request, 'app/alert/notification.html')