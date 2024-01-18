def Deposit(request):
    if request.method == 'POST':
        number = request.POST['number']
        amount = request.POST['amount']
        user = request.user

        if len(number) == 12 and (number.startswith('254') or number.startswith('2547')):
            access_token = MpesaAccessToken.validated_mpesa_access_token
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
            headers = {"Authorization": "Bearer %s" % access_token}
            payload = {
                "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
                "Password": LipanaMpesaPpassword.decode_password,
                "Timestamp": LipanaMpesaPpassword.lipa_time,
                "CheckoutRequestID": "<provide_checkout_request_id_received_from_stk_push>"
            }
            response = requests.post(api_url, json=payload, headers=headers)

            if response.status_code == 200:
                mpesa_response = response.json()

                # Check if the STK push was successful
                if 'ResultCode' in mpesa_response and mpesa_response['ResultCode'] == '0':
                    # Save the Pay and MpesaPayment models if the STK push is successful
                    deposit = Pay.objects.create(
                        client=user.client,
                        amount=amount,
                        number=number,
                    )
                    deposit.save()

                    mpesa_payment = MpesaPayment.objects.create(
                        amount=amount,
                        description="Payment via STK push",
                        type="STK Push",
                        reference=mpesa_response.get('CheckoutRequestID', ''),
                        first_name=user.client.first_name,
                        middle_name=user.client.last_name,
                        last_name="",
                        phone_number=number,
                        organization_balance=mpesa_response.get('OrgAccountBalance', 0.0)
                    )
                    mpesa_payment.save()

                    messages.success(request, 'STK Push successful')
                else:
                    # Handle cases where the STK push failed
                    messages.error(request, f'STK Push failed: {mpesa_response["ResultDesc"]}')
            else:
                messages.error(request, 'M-Pesa API call failed')
                
            return redirect('deposit')
        else:
            messages.error(request, f"Phone number '{number}' is not valid or wrong format")
            return redirect('deposit')
    else:
        return render(request, 'app/transaction/deposit.html')
    return render(request, 'app/transaction/deposit.html')
