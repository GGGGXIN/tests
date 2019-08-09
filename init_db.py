import time

JHP = dict(
    title="JHP支付",
    app_id="8200128",
    app_key="4eDApdE4",
    pay_url="https://pay.fastpay365.com/pgw.json",
    created=int(time.time())
)
channels = [
    {
        "title": "JHP支付宝扫码",
        "extra_info": '{"payTypeId": 2, "wap": "false"}',
        "pay_type": "alipay",
        "status": 1,
        "pc": 1,
    },
    {
        "title": "JHP支付宝H5",
        "extra_info": '{"payTypeId": 4, "wap": "true"}',
        "pay_type": "alipay",
        "status": 1,
        "pc": 0,
    },
    {
        "title": "JHP微信扫码",
        "extra_info": '{"payTypeId": 1, "wap": "false"}',
        "pay_type": "wx",
        "status": 1,
        "pc": 1,
    },
    {
        "title": "JHP微信H5",
        "extra_info": '{"payTypeId": 3, "wap": "true"}',
        "pay_type": "wx",
        "status": 1,
        "pc": 0
    },
    {
        "title": "银联扫码",
        "extra_info": '{"payTypeId": 8, "wap": "false"}',
        "pay_type": "union_bank",
        "status": 1,
        "pc": 2
    },

]

from pay.models import Channel, Gateway


def init_jhp():
    gateway = Gateway.objects.create(**JHP)
    for channel in channels:
        channel.setdefault("gateway_id", gateway.id)
        channel.setdefault("gateway_name", "jhp")
        channel.setdefault("created", int(time.time()))
        Channel.objects.create(**channel)


if __name__ == '__main__':
    init_jhp()