import time
from app import db
from models.order import Gateway, Channel

JHP = dict(
    title="JHP支付",
    app_id="8200128",
    app_key="4eDApdE4",
    notify_url="",
    callback_url="",
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
        "pay_type": "union",
        "status": 1,
        "pc": 2
    },

]


def update():
    try:
        gateway = db.session.query(Gateway).filter(
            Gateway.title == JHP["title"]
        ).one()
    except Exception as e:
        gateway = Gateway(**JHP)
        db.session.add(gateway)
        db.session.commit()
    for channel in channels:
        channel.setdefault("gateway_id", gateway.id)
        channel.setdefault("created", int(time.time()))
        db.session.add(Channel(**channel))
    db.session.commit()
    db.session.close()


if __name__ == "__main__":
    from app import create_app

    app = create_app("dev")
    app_ctx = app.app_context()
    with app_ctx:
        update()