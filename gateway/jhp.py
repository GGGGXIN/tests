import json
import uuid
import time
import requests
import decimal
import hashlib

from pay.utils import PaymentService
from pay.models import Order


class JHP(PaymentService):
    """JHP支付"""
    PAY_API = 'https://pay.fastpay365.com/pgw.json'  # 支付接口
    KEY = '4eDApdE4'

    MCH_ID = '8200128'
    NOTIFY_URL = 'http://52.79.227.102:8000/jhp/notify'
    CALLBACK_URL = ""
    GOODS_NAME = 'online_pay'
    #  响应
    RESPONSE_TYPE__ = "JSON"
    # 签名算法
    SIGN_TYPE = "MD5"
    TIMEOUT_WARN = 5

    def __init__(self,
                 mch_id=MCH_ID,
                 pay_api=PAY_API,
                 key=KEY,
                 goods_name=GOODS_NAME,
                 notify_url=NOTIFY_URL,
                 callback_url=CALLBACK_URL,
                 **kwargs):
        self.mch_id = mch_id

        self.pay_api = pay_api
        self.key = key

        self.notify_url = notify_url
        self.callback_url = callback_url
        self.goods_name = goods_name
        self.timestamp = int(time.time())
        super(JHP, self).__init__(**kwargs)

    def prepare_charge(self, order, channel, **kwargs):
        """
        预备支付参数
        :param recharge: 存款订单
        :param payee: 收款对象, 后台配置
        :param kwargs:
        :return:
        """
        return dict(json.loads(channel.extra_info),
                    faceMoney=order.amount,
                    inOrderId=order.games_order,
                    clientIp=order.client_ip,
                    Uid=str(uuid.uuid4())
                    )

    def platform_pay(self, payload):
        """
        支付平台下单接口
        :param order: 订单对象
        :param channel: 存款渠道
        :param payload: 下单所必须的参数，由 prepare_charge 所提供
        :param kwargs:
        :return: 返回支付页面
        """
        resp = self.request(payload=payload, verify=False)
        print(resp, "@@@@")
        if not resp.get("redirectUrl", None):
            return json.dumps({"code": 4003, "error": "创建订单失败"})
        url = resp["redirectUrl"]
        return json.dumps({"code": 200, "url": url}, ensure_ascii=False)

    def request(self, method="POST", payload=None, data=None, json=None, live=True, verify=True, **kwargs):
        """
        通用 HTTP 请求处理，
        方法支持: GET, POST, PUT, DELETE
        正文体支持: FORM, JSON

        1. 自动处理请求路径
        2. 响应体内容解析
        3. 返回结果解析
            - 错误结果会抛出异常，调用者需要处理异常，如果是APIError可以直接返回给客户端,框架有自动处理此类异常的显示

        POST + form: method=POST
        :param path:  请求路径
        :param payload:  Post 请求参数，可以是form
        :param json: POST 请求的json 字段
        :param method: 方法
        :param live: 是否是生产环境请求
        :param verify: 是否同步校验返回结果
        :param kwargs:
        :return:
        """
        method = method.lower()
        url = self.pay_api
        payload = self._preprocess_params(payload)
        payload['sign'] = self._sign(payload)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # logger.debug('payment.request', url=path, method=method, payload=payload)
        print("####", payload)
        start = time.time()
        try:
            resp = requests.request(method, url=url, headers=headers, data=payload, **kwargs)
            print(resp)
        except Exception as e:
            # logger.exception('error.jhp', exc_info=True)
            # raise exceptions.ChannelConnectionError(str(e))
            print(e)
        elapsed = time.time() - start
        # logger.debug('payment.response_time', gateway=self, elapsed=elapsed, url=self.pay_api, method=method,
        #              payload=payload)
        if elapsed >= self.TIMEOUT_WARN:
            # logger.warn('payment.response_warn', gateway=self, elapsed=elapsed, url=self.pay_api, method=method,
            #             payload=payload)
            print("超时")
            return {"error": "超时"}
        return resp.json()

    def _preprocess_params(self, params):
        """
        预处理参数, 可以自动填充请求所需要的公共参数，
        以及在这里加入签名信息
        :param params:
        :return:
        """
        params.setdefault('payFromAccount', self.mch_id)
        params.setdefault('name', self.goods_name)
        params.setdefault('timestamp', self.timestamp)
        params.setdefault('inNotifyUrl', self.notify_url)
        params.setdefault('sign', self._sign(params))
        return params

    def on_notify(self, data, recharge=None, channel=None, **kwargs):
        # 验证签名
        if not self.verify_params(data):
            return {"error": "签名有误", "code": 4008}
        payload = self.parse_notify_result(data)

        order_id = Order.objects.update(**payload)
        order = Order.objects.get(id=order_id)
        if not order:
            return json.dumps({"result": 4007, "error": "不存在的订单"})
        url = order.notify_url
        self.game_notify(url, data)

    def verify_params(self, params):
        """验签"""
        key = params['sign']
        sign = self._sign(params)
        if sign != key:
            return False
        return params

    def parse_notify_result(self, data):
        """
        处理回调结果，将对方数据格式，转换为我们需要的数据结构
        一般我们需要几个数据
            - trans_no: 对方平台订单ID，如果没有提供则为 None
            - amount_paid: 实际支付金额
            - fee: 手续费
            - time_paid: 支付时间

        失败的情况下返回
            { failure_code, failure_msg }

        :param data:
        :return:

        """
        # 成功状态下
        if data['result'] == '710013':
            return {
                'pay_order': data['transactionId'],
                'pay_amount': decimal.Decimal(data['successMoney']),
                'pay_time': data["timestamp"],
                'games_order': data["orderId"],
                'updated': int(time.time())
            }

        # 失败情况下
        return {'failure_code': data['result'], 'failure_msg': data["result"]}

    def _presign(self, params):
        """签名前预处理参数"""
        excludes = ["sign", "wap", "clientIp", "Uid", "endTime", "beginTime"]
        return "&".join(
            [F"{key}={params[key]}" for key in sorted(params.keys()) if key not in excludes]) + f"&key={self.KEY}"

    def _sign(self, params):
        """签名算法实现"""
        source = self._presign(params)
        sign = hashlib.md5(source.encode('utf8')).hexdigest()
        return sign


jhp = JHP()