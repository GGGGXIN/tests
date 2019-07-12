import json
import time

from flask import Blueprint
from flask import request, render_template

from utils.helper import Logger

api_b = Blueprint("api", __name__, url_prefix="/api")

logger = Logger(__name__)


@api_b.route("/create_order", methods=["GET"])
def create_order():
    """玩家创建订单接口"""
    from setting import APP_KEY
    from service.base import payments
    from setting import HOST
    import json
    try:
        data = request.args
        sign = payments._sign(data, APP_KEY, excludes=["sign"])
        if sign != data.get("sign"):
            return json.dumps({"code": 40001, "error": "无效的签名"})
        agent = request.user_agent.platform
        channel_list = payments.get_channels(agent)
        return render_template("payment.html", context=data, channel_list=channel_list, host=HOST)
    except Exception as e:
        logger.error("参数有误", e)
        return json.dumps({"code": 40001, "error": "参数有误"})


@api_b.route("/pay", methods=["POST"])
def pay():
    from decimal import Decimal
    from service.base import payments
    from setting import APP_KEY
    from service.order import orders
    from service.gateway import jhp
    try:
        data = request.form.to_dict()
        data["amount"] = Decimal(data["amount"]).quantize(Decimal("0.00"))
        channel = payments.search_channel(int(data.get("channel_id", 0)))
        if not channel:
            return json.dumps({"code": 40002, "error": "无效的通道"})
        sign = payments._sign(data, APP_KEY, excludes=["sign", "channel_id"])
        if sign != data.get("sign"):
            return json.dumps({"code": 40001, "error": "无效的签名"})
        order_no = f"NO{int(time.time())}"
        order = orders.create_order({"order_no": order_no,
                                     "games_order": data["order_no"],
                                     "amount": data["amount"],
                                     "channel_id": channel.id,
                                     "channel_name": channel.title,
                                     "client_ip": request.remote_addr,
                                     "notify_url": data["notify_url"],
                                     "created": int(time.time())})
        payload = jhp.prepare_charge(order, channel)
        return jhp.platform_pay(payload)
    except Exception as e:
        logger.error("支付失败", e)
        return json.dumps({"code": 4005, "error": "支付失败"})


@api_b.route("/jhp/notify", methods=["POST"])
def notify():
    from service.gateway import jhp
    data = request.form.to_dict()
    if not data:
        data = request.json
    logger.info("回调数据", data)
    return jhp.on_notify(data)

