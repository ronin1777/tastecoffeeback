import json
import requests
import logging


# گرفتن یک نمونه از لاگر
logger = logging.getLogger(__name__)


class BasePaymentGateway:
    """
    کلاس پایه برای مدیریت عملیات پرداخت.
    """

    def __init__(self, merchant_id, debug=True):
        self.merchant_id = merchant_id
        self.debug = debug
        if self.debug:
            sandbox = 'sandbox'
        else:
            sandbox = 'www'

        self.ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/v4/payment/request.json"
        self.ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/v4/payment/verify.json"
        self.ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
        # تعیین آدرس‌های API زرین‌پال بر اساس حالت سندباکس
        self.response_messages = {
            -5000: "ناشناس",
            -9: "خطای اعتبار سنجی",
            -10: "ای پی و يا مرچنت كد پذيرنده صحيح نيست",
            -11: "مرچنت کد فعال نیست لطفا با تیم پشتیبانی ما تماس بگیرید",
            -12: "تلاش بیش از حد در یک بازه زمانی کوتاه",
            -15: "ترمینال شما به حالت تعلیق در آمده با تیم پشتیبانی تماس بگیرید",
            -16: "سطح تاييد پذيرنده پايين تر از سطح نقره اي است",
            100: "عملیات موفق",
            101: "قبلا تایید شده",
            -30: "اجازه دسترسی به تسویه اشتراکی شناور ندارید",
            -31: "حساب بانکی تسویه را به پنل اضافه کنید مقادیر وارد شده واسه تسهیم درست نیست",
            -32: "تسهیم شده نامعتبر، مجموع تسهیم شده (شناور) بیش از حداکثر مبلغ است",
            -33: "درصد های تسهیم شده درست نیست",
            -34: "مبلغ از کل تراکنش بیشتر است",
            -35: "تعداد افراد دریافت کننده تسهیم بیش از حد مجاز است",
            -40: "پارامتر های اضافی نامعتبر، مهلت پرداخت نامعتبر است",
            -50: "جلسه نامعتبر، مقادیر مبلغ در وریفای متفاوت است",
            -51: "جلسه نامعتبر، جلسه فعال پرداخت نشده است",
            -52: "خطا، لطفا با تیم پشتیبانی ما تماس بگیرید",
            -53: "اتوریتی برای این مرچنت کد نیست",
            -54: "اتوریتی نامعتبر است",
        }


class Zarinpal(BasePaymentGateway):
    """
    کلاسی برای مدیریت عملیات پرداخت با درگاه زرین‌پال.
    """

    def payment_gateway(self, amount, callback_url, description="درگاه پرداخت ابرتل", email=None, mobile=None):
        """
        ایجاد درخواست پرداخت با استفاده از API REST زرین‌پال.

        :param amount: مبلغ پرداخت (به ریال).
        :param callback_url: آدرس URL برای هدایت کاربر پس از پرداخت.
        :param description: توضیحات پرداخت.
        :param email: ایمیل پرداخت‌کننده.
        :param mobile: شماره موبایل پرداخت‌کننده.
        :return: لینک پرداخت در صورت موفقیت، در غیر این صورت 'Error'.
        """
        logger.debug(
            f"ایجاد درخواست پرداخت با مبلغ: {amount}, آدرس بازگشت: {callback_url}, توضیحات: {description}, ایمیل: {email}, موبایل: {mobile}")
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "description": description,
            "email": email,
            "mobile": mobile,
            "callback_url": callback_url,
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}

        try:
            response = requests.post(self.ZP_API_REQUEST, data=data, headers=headers, timeout=10)
            logger.debug(f"نتیجه درخواست پرداخت: {response.status_code}, {response.text}")

            if response.status_code == 200:
                response = response.json()
                if response.get("data", {}).get("code", 200) == 100:
                    response = response.get("data", {})
                    payment_url = self.ZP_API_STARTPAY + str(response.get("authority"))
                    logger.info(f"درخواست پرداخت موفق بود. لینک پرداخت: {payment_url}")
                    return {'status': True, 'url': payment_url, 'authority': response.get("authority")}
            response = response.json()
            logger.warning(
                f"درخواست پرداخت ناموفق بود: "
                f"{self.response_messages.get(response.get('data', {}).get('code', -5000), 'خطای ناشناخته')}")
            return {'status': False, 'data': response.get('data', {}), 'errors': response.get('errors', {})}
        except requests.exceptions.Timeout:
            logger.error("استثنا: درخواست پرداخت تایم‌اوت شد.")
            return {'status': False, 'code': 'timeout'}
        except requests.exceptions.ConnectionError:
            logger.error("استثنا: خطای ارتباط با سرور.")
            return {'status': False, 'code': 'connection error'}
        except Exception as e:
            logger.error(f"استثنا در حین درخواست پرداخت: {e}")
            return {'status': False, 'code': 'unknown error'}

    def verify_payment(self, authority, amount):
        """
        تایید یک پرداخت با استفاده از API REST زرین‌پال.

        :param authority: کد اتوریتی دریافت شده از درگاه پرداخت.
        :param amount: مبلغ برای تایید (به ریال).
        :return: نتیجه تایید از زرین‌پال.
        """
        logger.debug(f"تایید پرداخت با کد اتوریتی: {authority}, مبلغ: {amount}")
        amount = int(amount)
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "authority": authority,
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}

        try:
            response = requests.post(self.ZP_API_VERIFY, data=data, headers=headers, timeout=10)
            logger.debug(f"نتیجه تایید پرداخت: {response.status_code}, {response.text}")

            if response.status_code == 200:
                response = response.json()
                if response.get('errors') == [] and response.get("data", {}).get("code", 400) in [100, 101]:
                    data = response.get("data")
                    logger.info(f"تایید پرداخت موفق بود. کد پیگیری: {data['ref_id']}")
                    return {'status': True, 'ref_id': data['ref_id'], 'code': data['code'], 'errors': response['errors']}
                else:
                    logger.warning(
                        f"تایید پرداخت ناموفق بود: {self.response_messages.get(response['Status'], 'خطای ناشناخته')}")
                    return {'status': False, 'code': str(response['code'])}
            return {'status': False, 'code': 'http_error'}
        except requests.exceptions.Timeout:
            logger.error("استثنا: تایید پرداخت تایم‌اوت شد.")
            return {'status': False, 'code': 'timeout'}
        except requests.exceptions.ConnectionError:
            logger.error("استثنا: خطای ارتباط با سرور.")
            return {'status': False, 'code': 'connection error'}
        except Exception as e:
            logger.error(f"استثنا در حین تایید پرداخت: {e}")
            return {'status': False, 'code': 'unknown error'}