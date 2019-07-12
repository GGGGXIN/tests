from app import db


class ModelMixin:
    # 记录创建更新时间 以及拓展字段
    created = db.Column(db.Integer, nullable=False)
    updated = db.Column(db.Integer)
    data = db.Column(db.JSON, default={})


class Order(ModelMixin, db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(256), nullable=False, index=True)
    games_order = db.Column(db.String(256))
    pay_order = db.Column(db.String(256))

    # 订单创建金额  实际支付金额 支付时间 支付状态
    amount = db.Column(db.Numeric(asdecimal=True, precision=18, scale=2))
    pay_amount = db.Column(db.Numeric(asdecimal=True, precision=18, scale=2))
    pay_time = db.Column(db.Integer)
    succeeded = db.Column(db.Boolean, default=False)

    # 支付方式 通道id 通道名字
    pay_type = db.Column(db.String(256))
    channel_id = db.Column(db.Integer)
    channel_name = db.Column(db.String(256))

    # 用户相关
    username = db.Column(db.String(256))
    client_ip = db.Column(db.String(128))
    # 回调平台地址
    notify_url = db.Column(db.String(128), nullable=False)


class Gateway(ModelMixin, db.Model):
    __tablename__ = "gateway"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    app_id = db.Column(db.String(128), nullable=False)
    app_key = db.Column(db.String(256), nullable=False)
    notify_url = db.Column(db.String(128), nullable=False)
    callback_url = db.Column(db.String(128))
    pay_url = db.Column(db.String(256))


class Channel(ModelMixin, db.Model):
    __tablename__ = "channel"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    gateway_id = db.Column(db.Integer)
    extra_info = db.Column(db.JSON)
    pay_type = db.Column(db.String(128))
    # 1开启 0 关闭
    status = db.Column(db.Integer)
    pc = db.Column(db.Integer)


if __name__ == '__main__':
    from app import create_app
    app = create_app("dev")
    app_ctx = app.app_context()
    with app_ctx:
        db.create_all()
        # db.drop_all()