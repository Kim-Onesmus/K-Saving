from django.conf import settings
from twilio.rest import client
import random


class MessaHandler:
    
    phone_number = None
    otp = None
    
    def __init__(self, phone_number, otp) -> None:
        self.phone_number = phone_number
        self.otp = otp
        
        
    def send_otp_on_phone(self):
        client = client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
        
        message = client.messages.create(
            body=f'Your OTP is {self.otp}',
            from_='+254792613079',
            to='self.phone_number' ,
        )