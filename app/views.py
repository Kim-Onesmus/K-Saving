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
from . models import Client, ContactUs, MpesaPayment, My_Plan, Pay, Withdraw, Notification
from . forms import ClientForm, My_PlanForm
from django.urls import reverse
from django.forms.models import model_to_dict
from rest_framework import views, response, status
from .serializers import MpesaResponseBodySerializer, TransactionSerializer
from .models import MpesaResponseBody, Transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings


def Index(request):
    client = request.user.client
    existings_plan = My_Plan.objects.filter(client=client).first()
    pays = Pay.objects.filter(client=client)
    total_amount = sum(pay.amount for pay in pays)
    remaining = existings_plan.target - total_amount
    remaining_days = remaining/existings_plan.amount

    approved_withdrawals = Withdraw.objects.filter(client=client, status='approved')

    # Deduct the withdrawal amounts from the total amount
    for withdrawal in approved_withdrawals:
        total_amount -= withdrawal.amount

    context = {'existings_plan':existings_plan, 'total_amount':total_amount, 'remaining':remaining, 'remaining_days':remaining_days}
    return render(request, 'app/index.html', context)


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
            form = My_PlanForm(request.POST, request.FILES, instance=existing_plan)
            if form.is_valid():
                form.save()
                messages.info(request, 'Plan edited successfully')
                return redirect('my_plan')
        else:
            new_plan = My_Plan(client=client, plan=plan, amount=amount, target=target)
            new_plan.save()

            messages.success(request, 'Plan saved successfully.')
            return redirect('my_plan')

    else:
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


@csrf_exempt
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
    consumer_key = 'AMOetkruFwpNeGQrnfQYMWbq1qyM5Iad'
    consumer_secret = 'vHwWTtUKqYdovT2A'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    r = request.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_toke = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_toke['access_token']
    return HttpResponse(validated_mpesa_access_token)

@csrf_exempt
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
                "CallBackURL": 'https://30de-105-160-60-50.ngrok-free.app/callback/',
                "AccountReference": "KimTech",
                "TransactionDesc": "Savings"
            }
            print('Payload', payload)

            response = requests.post(api_url, json=payload, headers=headers)
            print('response', response)

            if response.status_code == 200:
                mpesa_response = response.json()
                print('Mpesa Response', mpesa_response)
                
                # Check if 'ResponseCode' is in mpesa_response and its value is '0'
                if 'ResponseCode' in mpesa_response and mpesa_response['ResponseCode'] == '0':
                    deposit = Pay.objects.create(
                        client=user.client,
                        amount=amount,
                        number=number,
                    )
                    deposit.save()

                    subject = 'Smart Saver Deposit request'
                    message = f'KSH.{amount} has been deposited in your account {client}.\nCheck your dashboard for verification. \nThank you. \nRegards \nSmart Saver'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [request.user.email, ]
                    send_mail( subject, message, email_from, recipient_list )

                    notification_data = Notification.objects.create(client=client, message=message)
                    notification_data.save()
                    
                    messages.success(request, 'Deposit successful')
                    return redirect('deposit')
                else:
                    # Handle the case where the 'ResponseCode' is not '0'
                    messages.error(request, 'Deposit failed: ResponseCode is not 0')
            else:
                # Handle the case where the API call failed
                messages.error(request, 'M-Pesa API call failed')
        else:
            messages.error(request, f"Phone number '{number}' is not valid or in the wrong format")
        
        return redirect('deposit')
    else:
        return render(request, 'app/transaction/deposit.html')
    return render(request, 'app/transaction/deposit.html')

def WithdrawFunc(request):
    client = request.user.client
    existings_plan = My_Plan.objects.filter(client=client).first()
    pays = Pay.objects.filter(client=client)
    total_amount = sum(pay.amount for pay in pays)
    remaining = existings_plan.target - total_amount
    remaining_days = remaining/existings_plan.amount

    if request.method == 'POST':
        client = request.user.client
        number = request.POST['number']
        amount = request.POST['amount']

        if len(number) == 12 and (number.startswith('254') or number.startswith('2547')):
            if total_amount >= remaining:
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


def Deposits(request):
    client = request.user.client
    deposits = Pay.objects.filter(client=client)
    
    context = {'deposits':deposits}
    return render(request, 'app/history/deposits.html', context)


def Withdrawals(request):
    client = request.user.client
    deposits = Withdraw.objects.filter(client=client)

    context = {'deposits':deposits}
    return render(request, 'app/history/withdraws.html', context)


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
    print(payment)
    payment.save()
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))




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

def About(request):
    return render(request, 'app/about.html')

def Notifications(request):
    client = request.user.client
    user_notification = Notification.objects.filter(client=client)

    context = {'user_notification':user_notification}
    return render(request, 'app/alert/notification.html', context)



# CREATING A CALLBACK URL

class MpesaCallbackView(views.APIView):
    def post(self, request, format=None):
        body = request.data

        if body:
            mpesa = MpesaResponseBody.objects.create(body=body)

            mpesa_body = mpesa.body
            print(mpesa_body)

            if mpesa_body['stkCallback']['ResultCode'] == 0:
                transaction = Transaction.objects.create(
                    phonenumber=mpesa_body['Body']['stkCallback']['CallbackMetadata']['Item'][-1]["Value"],
                    amount=mpesa_body['Body']['stkCallback']['CallbackMetadata']['Item'][0]["Value"],
                    receipt_no=mpesa_body['Body']['stkCallback']['CallbackMetadata']['Item'][1]["Value"]
                )
                
            return response.Response({"message": "Callback Data received and processed successfully."})
        return response.Response({"failed": "No Callback Data Received"}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, format=None):
        response_bodies = MpesaResponseBody.objects.all()
        serializer = MpesaResponseBodySerializer(response_bodies, many=True)

        return response.Response({"responses": serializer.data})


class TransactionView(views.APIView):
    def get(self, request, format=None):
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)

        return response.Response({"transactions": serializer.data})