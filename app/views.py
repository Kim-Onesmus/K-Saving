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
from . models import Client, ContactUs, MpesaPayment, My_Plan, Pay, Withdraw, Notification, MpesaCallBacks
from . forms import ClientForm, My_PlanForm
from django.urls import reverse
from django.forms.models import model_to_dict
from rest_framework import views, response, status
from .serializers import MpesaResponseBodySerializer, TransactionSerializer
from .models import MpesaResponseBody, Transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
load_dotenv()
import os

@login_required(login_url='login')
def Index(request):
    client = request.user.client
    existing_plan = My_Plan.objects.filter(client=client).first()
    if existing_plan:
        pays = Pay.objects.filter(client=client)
        total_amount = pays.aggregate(Sum('amount'))['amount__sum'] or 0  # Sum of all pay amounts
        approved_withdrawals = Withdraw.objects.filter(client=client, status='approved')
        total_amount -= approved_withdrawals.aggregate(Sum('amount'))['amount__sum'] or 0
        remaining = existing_plan.target - total_amount
        remaining_days = remaining / existing_plan.amount

    else:
        messages.info(request, 'Make a plan to continue')
        return redirect('my_plan')
    context = {'existings_plan': existing_plan, 'total_amount': total_amount, 'remaining': remaining, 'remaining_days': remaining_days}
    return render(request, 'app/index.html', context)


@login_required(login_url='login')
def MyPlan(request):
    user = request.user
    client = user.client
    existing_plan = My_Plan.objects.filter(client=client).first()
    form = My_PlanForm(instance=existing_plan)
    
    if request.method == 'POST':
        plan = request.POST['plan']
        amount = request.POST['amount']
        target = request.POST['target']
        
        if existing_plan:
            messages.info(request, 'You have an existing plan')
            return redirect('my_plan')

        else:
            form = My_PlanForm(request.POST, request.FILES, instance=existing_plan)
            if form.is_valid():
                form.save()
                messages.info(request, 'Plan edited successfully')
                return redirect('my_plan')

            new_plan = My_Plan(client=client, plan=plan, amount=amount, target=target)
            new_plan.save()

            messages.success(request, 'Plan saved successfully.')
            return redirect('my_plan')

    else:
        planings = My_Plan.objects.filter(client=client)
        context = {'form': form, 'existing_plan': existing_plan, 'planings': planings}
        return render(request, 'app/plan.html', context)
    planings = My_Plan.objects.filter(client=client)
    context = {'form': form, 'existing_plan': existing_plan, 'planings': planings}
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def Logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.info(request, 'Logged Out')
        return redirect('login')
    return render(request, 'app/account/logout.html')

def getAccessToken(request):
    consumer_key = os.getenv('CONSUMER_KEY')
    consumer_secret = os.getenv('CONSUMER_SECRETE')
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_toke = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_toke['access_token']
    return validated_mpesa_access_token

@login_required(login_url='login')
def Deposit(request):
    client = request.user.client
    plan_existing = My_Plan.objects.filter(client=client).first()

    if not plan_existing:
        messages.error(request, 'Create a plan to Deposit')
        return redirect('my_plan')

    if request.method == 'POST':
        number = request.POST['number']
        amount = request.POST['amount']
        user = request.user

        if len(number) == 12 and (number.startswith('254') or number.startswith('2547')):
            access_token = getAccessToken(request)
            print('Access token', str(access_token))
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            headers = {"Authorization": f"Bearer {access_token}"}

            payload = {
                "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
                "Password": LipanaMpesaPpassword.decode_password,
                "Timestamp": LipanaMpesaPpassword.lipa_time,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": number,
                "PartyB": LipanaMpesaPpassword.Business_short_code,
                "PhoneNumber": number,
                "CallBackURL": 'https://216e-154-159-238-195.ngrok-free.app/c2b/callback',
                "AccountReference": "KimTech",
                "TransactionDesc": "Savings"
            }
            # print('Payload', payload)
            response = requests.post(api_url, json=payload, headers=headers)
            print('Status code', response.status_code)
            if response.status_code == 200:
                mpesa_response = response.json()
                if 'ResponseCode' in mpesa_response and mpesa_response['ResponseCode'] == '0':
                    messages.success(request, 'Deposit initiated, please complete it on your M-Pesa app.')
                else:
                    messages.error(request, 'Deposit failed: ResponseCode is not 0')
            else:
                messages.error(request, 'M-Pesa API call failed')
        else:
            messages.error(request, f"Phone number '{number}' is not valid or in the wrong format")
        
        return redirect('deposit')
    else:
        return render(request, 'app/transaction/deposit.html')


@csrf_exempt
def call_back(request):
    if request.method == 'POST':
        print('M-Pesa callback received and being processed.......')
        mpesa_body = request.body.decode('utf-8')
        # print('Raw M-Pesa Body:', mpesa_body)
        
        try:
            # Parse JSON response
            mpesa_payment = json.loads(mpesa_body)
            # print("Parsed M-Pesa Payment Data:", mpesa_payment)
            
            # Determine the status based on ResultCode
            result_code = mpesa_payment['Body']['stkCallback']['ResultCode']
            status = "Success" if result_code == 0 else "Failed"
            print('Result Code', result_code)

            # Save callback data, including all details and status
            callback_entry = MpesaCallBacks(
                ip_address=request.META.get('REMOTE_ADDR'),
                caller=mpesa_payment['Body']['stkCallback']['MerchantRequestID'],
                conversation_id=mpesa_payment['Body']['stkCallback']['CheckoutRequestID'],
                content=mpesa_payment,  # Save the entire JSON content
                status=status,
            )
            callback_entry.save()
            
            # Return the entire JSON response from M-Pesa
            return JsonResponse(mpesa_payment, status=200, safe=False)

        except json.JSONDecodeError:
            print("Invalid JSON format in M-Pesa response.")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid JSON"}, status=400)
    
    elif request.method == 'GET':
        # Handle GET request to display all callback records
        callbacks = MpesaCallBacks.objects.all().values('ip_address', 'caller', 'conversation_id', 'content', 'status')
        return JsonResponse(list(callbacks), safe=False)  # Convert QuerySet to list for JSON response
    
    # Invalid request method
    return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid Request"}, status=400)

@csrf_exempt
def validation(request):
    print('Validating...............')
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    print('Confirming................')
    mpesa_body = request.body.decode('utf-8')
    if not mpesa_body:
        print("Empty request body received.")
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Empty request body"}, status=400)
    
    try:
        mpesa_payment = json.loads(mpesa_body)
        print("Received M-Pesa Payment Data:", mpesa_payment)
        # Here you can save the confirmed payment details to your database if needed.
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted", "body": mpesa_payment}, status=200)
    
    except json.JSONDecodeError:
        print("JSON decoding error: Invalid JSON format in request body.")
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid JSON format"}, status=400)


@csrf_exempt
def register_urls(request):
    access_token = getAccessToken(request)  # Fetch the access token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    
    # Use your public URLs for confirmation and validation
    options = {
        "ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
        "ResponseType": "Completed",
        "ConfirmationURL": "https://216e-154-159-238-195.ngrok-free.app/c2b/confirmation",  # Use your ngrok URL
        "ValidationURL": "https://216e-154-159-238-195.ngrok-free.app/c2b/validation"  # Use your ngrok URL
    }
    
    response = requests.post(api_url, json=options, headers=headers)

    return HttpResponse(response.text)


@login_required(login_url='login')
def WithdrawFunc(request):
    client = request.user.client
    existings_plan = My_Plan.objects.filter(client=client).first()
    if not existings_plan:
        messages.error(request, 'Create a plan to Deposit')
        return redirect('my_plan')

    pays = Pay.objects.filter(client=client)
    total_amount = pays.aggregate(Sum('amount'))['amount__sum'] or 0
    approved_withdrawals = Withdraw.objects.filter(client=client, status='approved')
    total_amount -= approved_withdrawals.aggregate(Sum('amount'))['amount__sum'] or 0
    remaining = existings_plan.target - total_amount
    remaining_days = remaining / existings_plan.amount

    if request.method == 'POST':
        client = request.user.client
        number = request.POST['number']
        amount = request.POST['amount']

        if len(number) == 12 and (number.startswith('254') or number.startswith('2547')):
            if total_amount >= existings_plan.target:
                withdraw_details = Withdraw.objects.create(client=client, number=number, amount=amount)
                withdraw_details.save()

                subject = 'Smart Saver withdrawal request'
                message = f'A withdrwal request of KSH.{amount} has been made for account {client}.\nIf you did not make any request contact us to cancell the request. \nThank you. \nRegards \nSmart Saver'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [request.user.email, ]
                send_mail( subject, message, email_from, recipient_list )

                notification_data = Notification.objects.create(client=client, message=message)
                notification_data.save()
                
                messages.info(request, 'Withdraw request submitted, you will receive a notification once the payment is made.')
                return redirect('withdraw')

            else:
                messages.error(request, 'You have not reached your target')
                return redirect('withdraw')
        else:
            messages.error(request, f"Phone number '{number}' is not valid or in the wrong format")
            return redirect('withdraw')
    else:
        return render(request, 'app/transaction/withdraw.html')
    return render(request, 'app/transaction/withdraw.html')


@login_required(login_url='login')
def Deposits(request):
    client = request.user.client
    deposits = Pay.objects.filter(client=client)
    
    context = {'deposits':deposits}
    return render(request, 'app/history/deposits.html', context)


@login_required(login_url='login')
def Withdrawals(request):
    client = request.user.client
    deposits = Withdraw.objects.filter(client=client)

    context = {'deposits':deposits}
    return render(request, 'app/history/withdraws.html', context)



@login_required(login_url='login')
def Contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        messange = request.POST['messange']
        
        contact_details = ContactUs.objects.create(name=name, email=email, subject=subject, messange=messange)
        contact_details.save()


        subject = contact_details.subject
        message = f'Email from: {email} \n {contact_details.messange}'
        email_from = request.user.email
        recipient_list = [settings.EMAIL_HOST_USER, ]
        send_mail( subject, message, email_from, recipient_list )

        messages.info(request, 'Messange sent')
        return redirect('contact')
    return render(request, 'app/contact.html')

@login_required(login_url='login')
def About(request):
    return render(request, 'app/about.html')

@login_required(login_url='login')
def Notifications(request):
    client = request.user.client
    user_notification = Notification.objects.filter(client=client)

    context = {'user_notification':user_notification}
    return render(request, 'app/alert/notification.html', context)

