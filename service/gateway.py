import time
import hashlib
import decimal
import uuid
import json
import requests
from service.base import PaymentService
from service.order import orders
from utils.helper import Logger

logger = Logger(__name__)


class JHP(PaymentService):
    """JHP支付"""
    PAY_API = 'https://pay.fastpay365.com/pgw.json'  # 支付接口
    KEY = '4eDApdE4'

    MCH_ID = '8200128'
    NOTIFY_URL = 'http://3e22ff7f.ngrok.io/jhp/notify'
    CALLBACK_URL = ""
    GOODS_NAME = 'online_pay'
    #  响应
    RESPONSE_TYPE__ = "JSON"
    # 签名算法
    SIGN_TYPE = "MD5"
    TIMEOUT_WARN = 2

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

    def for_url(self, path, live=True):
        """生成请求参数路径"""
        return f'{self.pay_api}{path}'

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

        # try:
        #     resp.raise_for_status()
        # except HTTPError as e:
        #     raise exceptions.ChannelRequestError(
        #         status=resp.status_code,
        #         payload=dict(failure_msg=str(e),
        #                      failure_code=resp.status_code,
        #                      payload=payload))

        if verify:
            payload = self.parse_body(resp.content)
            # logger.debug('payment.response', payload=payload, headers=resp.headers)
            self.verify_payload(payload)
            return payload

        return resp

    def parse_body(self, body):
        """
        处理返回的结果, 返回结构化数据供上层调用者使用

        比较常见的响应内容
            - xml
            - json
        :param body:
        :return:
        """
        try:
            return load_json(body)
        except ValueError:
            raise exceptions.ChannelParseError("返回非法格式")

    def verify_payload(self, payload):
        """
        校验结果，如果请求结果失败，则抛出响应的异常
        :param payload:
        :return:
        """
        if payload['resp']['code'] == 'SUCCESS':
            return payload

        raise exceptions.ChannelResponseCodeFail(
            "错误码: %s, %s" % (payload['resp']['code'], payload['resp']['err']))

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
        resp = self.request(payload=payload, verify=False).json()
        print(resp, "@@@@")
        if not resp.get("redirectUrl", None):
            return json.dumps({"code": 4003, "error": "创建订单失败"})
        url = resp["redirectUrl"]
        return json.dumps({"code": 200, "data": {
            'type': 'web',
            'skip': True,
            'url': url,
            'h5_skip': True,
        }})

    def check_result(self, data):
        """
        检查回调通知内容是否成功, 依据具体项目实现
        :param data:
        :return:
        """
        return data['result'] == '710013'

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
        if self.check_result(data):
            return {
                'pay_order': data['transactionId'],
                'pay_amount': decimal.Decimal(data['successMoney']),
                'pay_time': data["timestamp"],
                'games_order': data["orderId"],
                'updated': int(time.time())
            }

        # 失败情况下
        return {'failure_code': data['result'], 'failure_msg': data["result"]}

    def make_notify_response(self, data, recharge=None, **kwargs):
        """
        将处理结果返回给平台
        通常返回的内容，依据平台自行实现
        :param data:
        :param recharge:
        :return:
        """
        if self.check_result(data):
            return 'success'
        return 'failed'

    def on_notify(self, data, recharge=None, channel=None, **kwargs):
        # 验证签名
        if not self.verify_params(data):
            return {"error": "签名有误", "code": 4008}
        payload = self.parse_notify_result(data)

        order = orders.update(payload)
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



jhp = JHP()