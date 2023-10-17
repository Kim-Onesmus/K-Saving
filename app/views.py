from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User, auth
from requests.auth import HTTPBasicAuth
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
import json
import requests
from . models import Client, ContactUs, MpesaPayment, My_Plan, Pay
from . forms import ClientForm, My_PlanForm


def Index(request):
    return render(request, 'app/index.html')


def MyPlan(request):
    user = request.user
    client = user.client
    existing_plan = My_Plan.objects.filter(client=client).first()
    form = My_PlanForm(instance=existing_plan)
    
    if request.method == 'POST':
        plan = request.POST['plan']
        amount = request.POST['amount']
        target = request.POST['target']
        
        form = My_PlanForm(request.POST, request.FILES, instance=existing_plan)
        if plan and amount and target:
            if existing_plan:
                messages.error(request, 'You already have an active plan.')
                return redirect('my_plan')
            
            else:
                new_plan = My_Plan(client=client, plan=plan, amount=amount, target=target)
                new_plan.save()

                messages.success(request, 'Plan saved successfully.')
                return redirect('my_plan')
            
        if form.is_valid():
            form.save()
            messages.info(request, 'Plan edited successfully')
            return redirect('my_plan')   
    else:
        return render(request, 'app/plan.html') 
    
    plan = My_Plan.objects.get(client=client)
    context = {'form':form, 'existing_pan':existing_plan, 'plan':plan}
    return render(request, 'app/plan.html', context)

def Register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password1 = request.POST['password1']
        
        if password == password1:
            if len(username) == 12 and username.startswith('2547'):
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
                messages.error(request, 'Enter a valid number')
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
    client = user.client
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
        messages.info(request, 'Logged Out')
        return redirect('login')
    return render(request, 'app/account/logout.html')


def getAccessToken(request):
    consumer_key = 'gvmRX9peDcWeYTRRHBrOZh42jITwtl4N'
    consumer_secret = 'Vsmx9HaLqGPdAhPQ'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    r = request.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_toke = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_toke['access_token']
    return HttpResponse(validated_mpesa_access_token)

def Deposit(request):
    if request.method == 'POST':
        number = request.POST['number']
        amount = request.POST['amount']
        user = request.user
        if len(number) == 12 and number.startswith('254') or number.startswith('2547'):
            access_token = MpesaAccessToken.validated_mpesa_access_token
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            headers = {"Authorization": "Bearer %s" % access_token}
            payload = {
                "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
                "Password": LipanaMpesaPpassword.decode_password,
                "Timestamp": LipanaMpesaPpassword.lipa_time,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": number,
                "PartyB": LipanaMpesaPpassword.Business_short_code,
                "PhoneNumber": number,
                "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
                "AccountReference": "KimTech",
                "TransactionDesc": "Savings"
            }
            deposit = Pay.objects.create(
                client=user.client,
                amount=amount,
                number=number,
            )
            deposit.save()
            response = requests.post(api_url, json=payload, headers=headers)
            messages.success(request, 'Submitted successfully')
            return redirect('deposit')
        else:
            messages.error(request, f"Phone number '{number}' is not valid or wron format")
            return redirect('deposit')
    else:
        return render(request, 'app/transaction/deposit.html')
    return render(request, 'app/transaction/deposit.html')

@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://mydomain.com/confirmation",
               "ValidationURL": "https://mydomain.com/validation"}
    response = requests.post(api_url, json=options, headers=headers)

    return HttpResponse(response.text)


@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))



@csrf_exempt
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)

    payment = MpesaPayment(
        first_name=mpesa_payment['FirstName'],
        last_name=mpesa_payment['LastName'],
        middle_name=mpesa_payment['MiddleName'],
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
        reference=mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type=mpesa_payment['TransactionType'],

    )
    payment.save()

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }

    return JsonResponse(dict(context))

def Withdraw(request):
    return render(request, 'app/transaction/withdraw.html')

def Deposits(request):
    user = request.user
    client = Client.objects.get(user=user)
    deposits = MpesaPayment.objects.filter(phone_number=client.username)
    
    context = {'deposits':deposits}
    return render(request, 'app/history/deposits.html', context)

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