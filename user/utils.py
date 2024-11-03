from kavenegar import *
from tastecofee.settings import KAVENEGAR_API_KEY

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