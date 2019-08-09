import hashlib
import requests
import json
from . import models
from .settings import APP_KEY


class PaymentService:

    @classmethod
    def get_service(cls, name, **kwargs):
        print(name)
        for klass in cls.__subclasses__():
            if klass.__name__.lower() == name.lower():
                return klass(**kwargs)
            return False

    def presign(self, params, key, excludes=[]):
        """签名前预处理参数"""
        return "&".join(
            [F"{key}={params[key]}" for key in sorted(params.keys()) if key not in excludes]) + f"&key={key}"

    def sign(self, params, key, excludes=[]):
        """签名算法实现"""
        source = self.presign(params, key, excludes)
        print(source)
        sign = hashlib.md5(source.encode('utf8')).hexdigest()
        print("sign", sign)
        return sign

    def get_channels(self, agent, type):
        pc = 0 if agent in ["android", "iphone"] else 1
        if type not in ["wx", "alipay"]:
            pc = 2
        return models.Channel.objects.filter(
            status=1, pc=pc, pay_type=type,
        ).first()

    def create_order(self, info):
        return models.Order.objects.create(**info)

    def game_notify(self, url, data):
        headers = {'Content-Type': 'application/json'}
        new_data = dict(
            transaction_no=data["transactionId"],
            order_no=data["orderId"],
            request_amount=data["requestMoney"],
            # success_amount=data["successMoney"],
            success_amount="100.00",
            result="00",
            timestamp=data["timestamp"],
        )
        new_data.setdefault("sign", self.sign(new_data, APP_KEY))
        print("游戏回调内容", new_data)
        resp = requests.request("POST", url=url, headers=headers, data=json.dumps(new_data))
        print("游戏回调结果", resp.content)
        res = str(resp.content, encoding='utf8')
        if res != "success":
            return json.dumps({"result": 4006, "error": "回调信息有误"}, ensure_ascii=False)
        return "success"


payments = PaymentService()
