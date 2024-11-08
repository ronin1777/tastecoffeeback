from kavenegar import *
from tastecofee.settings import KAVENEGAR_API_KEY, MELIPAYAMAK_API

import requests
def send_otp_code(phonenumber, otp):
    try:
        api = KavenegarAPI(KAVENEGAR_API_KEY)
        params = {
            'sender': '',
            'receptor': phonenumber,
            'message': f"سلام به سایت taset-coffee خوش امدید.\nرمز یک بار مصرف: {otp} ",
        }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
            print(e)
    except HTTPException as e:
            print(e)


def send_sms_to_admin(admin_phone, user_phone, user_name):
    try:
        api = KavenegarAPI(KAVENEGAR_API_KEY)
        params = {
            'sender': '',
            'receptor': admin_phone,
            'message': f"ادمین جان یک سفارش برای کاربر {user_name} به شماره {user_phone} ثبت شده است.!\nهست!؟"

        }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
            print(e)
    except HTTPException as e:
            print(e)



# def melipayamak_send_sms(to, text, from_number=None):

#     username = MELIPAYAMAK_USERNAME
#     password = MELIPAYAMAK_PASSWORD
#     api = Api(username, password)
#     sms = api.sms()
#     from_number = MELIPAYAMAK_SEND_NUMBER
#     response = sms.send(to, from_number, text)
#     print(f"SMS Response: {response}")
#     return response




# def melipayamak_send_sms(to, text):
#     """
#     ارسال پیامک با استفاده از API ملی پیامک
#     :param to: شماره گیرنده (به فرمت '09xxxxxxxxx')
#     :param text: متن پیامک
#     :return: نتیجه ارسال پیامک به صورت دیکشنری
#     """
#     url = 'https://console.melipayamak.com/api/send/simple/10b62aa0c79249bf9e4b2f2407679bb1'
    
#     data = {
#         'from': MELIPAYAMAK_SEND_NUMBER,
#         'to': to,
#         'text': text
#     }
    
#     try:
#         response = requests.post(url, json=data)
#         print(response)
#         response.raise_for_status()
#         return response.json() 
#     except requests.exceptions.RequestException as e:
#         print(f"Error sending SMS: {e}")
#         return {"status": "failed", "error": str(e)}


def melipayamak_send_sms(phone_number, otp_code):
    """
    Sends an OTP SMS to the specified phone number using Melipayamak's shared service.
    
    Args:
        phone_number (str): The recipient's phone number.
        otp_code (int): The OTP code to be sent.
        
    Returns:
        dict: The response from the API, including recId and status.
    """
    # اطلاعات مورد نیاز برای ارسال پیامک
    url = MELIPAYAMAK_API
    data = {
        "bodyId": 265084,  # bodyId الگوی تأییدشده شما در ملی پیامک
        "to": phone_number,
        "args": [str(otp_code)]  # ارسال کد تایید به عنوان متغیر اول در آرایه
    }
    
    try:
        response = requests.post(url, json=data)
        response_data = response.json()
        print(response)

        
        # بررسی وضعیت ارسال و نمایش پیام در صورت نیاز
        if response.status_code == 200:
            return response_data
        else:
            return {"error": "Failed to send SMS", "details": response_data}
    
    except requests.exceptions.RequestException as e:
        return {"error": "An error occurred while sending the SMS", "details": str(e)}
    

def send_order_notification(user_name, user_phone, order_id):
    """
    Sends an OTP SMS to the specified phone number using Melipayamak's shared service.
    
    Args:
        phone_number (str): The recipient's phone number.
        otp_code (int): The OTP code to be sent.
        
    Returns:
        dict: The response from the API, including recId and status.
    """
    # اطلاعات مورد نیاز برای ارسال پیامک
    url = MELIPAYAMAK_API
    data = {
        "bodyId": 265613, 
        "to": '09156599198',
        "args": [str(user_name), str(user_phone), str(order_id)]
    }
    
    try:
        response = requests.post(url, json=data)
        response_data = response.json()
        print(response)

        
        # بررسی وضعیت ارسال و نمایش پیام در صورت نیاز
        if response.status_code == 200:
            return response_data
        else:
            return {"error": "Failed to send SMS", "details": response_data}
    
    except requests.exceptions.RequestException as e:
        return {"error": "An error occurred while sending the SMS", "details": str(e)}