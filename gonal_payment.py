import math
import random
import gonal_database as database
from src.gonal_admin import *

from yoomoney import *

import requests

comment = COMMENT_PAY

# генерация комментария к оплате
def generate_comment(price):
    key_pass = list("1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm")
    random.shuffle(key_pass)
    key_buy = "".join([random.choice(key_pass) for i in range(12)])

    com = f"{comment}:{key_buy}.{price}"

    return com


class Qiwi:
    def __init__(self):
        self.num = ""
        self.token = ""
        self.update()

    def update(self):
        self.num = database.get_qiwi(0)
        self.token = database.get_qiwi(1)

    # генерация ключа оплаты
    def create_link(self, price):
        com = generate_comment(price)

        url = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={self.num}&amountInteger={price}&amountFraction=0&extra%5B%27comment%27%5D={com}&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"

        return f"{com}", url

    # проверка оплаты
    def payment_ver(self, comment, price):
        request = requests.Session()
        request.headers["authorization"] = "Bearer " + self.token
        params_get = {"rows": 10, "operation": "IN"}
        qiwi_get = request.get(
            f"https://edge.qiwi.com/payment-history/v2/persons/{self.num}/payments",
            params=params_get)
        qiwi_get = qiwi_get.json()["data"]

        is_buy_item = False

        comment_qiwi = []
        amount_qiwi = []
        currency_qiwi = []

        for i in range(len(qiwi_get)):
            # обработка последних 10 платежей
            comment_qiwi.append(qiwi_get[i]["comment"])
            amount_qiwi.append(qiwi_get[i]["sum"]["amount"])
            currency_qiwi.append(qiwi_get[i]["sum"]["currency"])

        for j in range(len(comment_qiwi)):
            # проверка если оплата присутсвует
            if str(comment) in str(comment_qiwi[j]) and str(price) == str(amount_qiwi[j]) and str(
                    currency_qiwi[j]) == "643":
                is_buy_item = True
                break

        return is_buy_item

    # доступен ли кошелек
    def check_available(self):
        request = requests.Session()
        request.headers["authorization"] = "Bearer " + self.token
        param = {"rows": 5, "operation": "IN"}
        qiwi_Get = request.get(f"https://edge.qiwi.com/payment-history/v2/persons/{self.num}/payments",
                               params=param)

        if qiwi_Get.status_code == 200:
            return True
        else:
            return False

    # доступен ли кошелек (с параметрами)
    def check_available_data(self, token, number):
        request = requests.Session()
        request.headers["authorization"] = "Bearer " + token
        parameters = {"rows": 5, "operation": "IN"}
        qiwi_Get = request.get(f"https://edge.qiwi.com/payment-history/v2/persons/{number}/payments",
                               params=parameters)

        if qiwi_Get.status_code == 200:
            return True
        else:
            return False


# ЮМани, который все так просят
class YooMoney:
    def __init__(self):
        self.num = ""
        self.token = ""
        self.refresh()

        self.client_id = ""
        self.redirect_uri = ""

    def refresh(self):
        self.num = database.get_yoo(0)
        self.token = database.get_yoo(1)

    # ссылка на оплату
    def create_link(self, price):
        com = generate_comment(price)

        quickpay = Quickpay(
            receiver=self.num,
            quickpay_form="shop",
            targets="Оплата счёта",
            paymentType="SB",
            sum=price,
            label=com
        )

        return com, quickpay.base_url

    # проверка оплаты
    def payment_ver(self, comment, money):
        client = Client(self.token)
        history = client.operation_history(label=comment)

        for operation in history.operations:
            yoo_comment = str(operation.label)
            yoo_money = math.ceil(operation.amount)

            if yoo_comment == comment and yoo_money == int(money):
                return True

        return False

    # генерация ссылки
    def gen_auth(self, client_id, redirect_uri):
        self.client_id = client_id
        self.redirect_uri = redirect_uri

        data = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': 'account-info operation-history operation-details'
        }

        r = requests.post("http://yoomoney.ru/oauth/authorize", params=data)
        return r.url

    # создание токена
    def gen_token(self, url):
        data = url.split("?")
        code = data[1].split("=")[1]

        auth = {
            'code': code,
            'client_id': self.client_id,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
        }

        r = requests.post("http://yoomoney.ru/oauth/token", params=auth)
        if r.status_code == 200:
            response = r.json()

            token = response["access_token"]

            yoo_data = token.split(".", 2)
            database.input_yoo_money(yoo_data[0], token)
            self.refresh()
            return True
        else:
            return False

    # проверка кошелька
    def check_yoo(self):
        request = requests.Session()
        request.headers["Authorization"] = "Bearer " + self.token

        r = request.get("http://yoomoney.ru/api/account-info")
        if r.status_code == 200:
            return True
        else:
            return False