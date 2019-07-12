import hashlib
import json
import requests
from exception import ValidationError
from models.order import Channel
from app import db
from setting import APP_KEY
from utils.helper import Logger

logger = Logger(__name__)


class PaymentService:
    def __init__(self):
        pass

    @classmethod
    def get_service(cls, name, **kwargs):
        for klass in cls.__subclasses__():
            if klass.__name__.lower() == name.lower():
                return klass(**kwargs)
            raise ValidationError(f"无效的支付网关{name}")

    def _presign(self, params, key, excludes=[]):
        """签名前预处理参数"""
        return "&".join(
            [F"{key}={params[key]}" for key in sorted(params.keys()) if key not in excludes]) + f"&key={key}"

    def _sign(self, params, key, excludes=[]):
        """签名算法实现"""
        source = self._presign(params, key, excludes)
        print(source)
        sign = hashlib.md5(source.encode('utf8')).hexdigest()
        return sign

    def get_channels(self, agent):
        pc = 1 if agent in ["android", "iphone"] else 0
        return db.session.query(Channel).filter(
            Channel.status == 1,
            Channel.pc != pc,
        ).all()

    def search_channel(self, id):
        return db.session.query(Channel).filter(
            Channel.id == id
        ).one()

    def game_notify(self, url, data):
        headers = {'Content-Type': 'application/json'}
        new_data = dict(
            transaction_no=data["transactionId"],
            order_no=data["orderId"],
            request_amount=data["requestMoney"],
            success_amount=data["successMoney"],
            result="00",
            timestamp=data["timestamp"],
        )
        new_data.setdefault("sign", self._sign(new_data, APP_KEY))
        logger.info("游戏回调内容", new_data)
        resp = requests.request("POST", url=url, headers=headers, data=new_data)
        logger.info("游戏回调结果", resp)
        if resp != "success":
            return json.dumps({"result": 4006, "error": "回调信息有误"})
        return "success"


payments = PaymentService()
