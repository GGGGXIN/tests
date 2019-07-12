# by gaoxin
from app import db
from models.order import Order


class OrderService:
    def create_order(self, info):
        order = Order(**info)
        db.session.add(order)
        db.session.commit()
        return order

    def get_order(self, order_no, channel):
        return db.session.query(Order).filter(
            Order.order_no == order_no,
            Order.channel_id == channel.id
        ).one()

    def update(self, payload):
        return db.session.query(Order).filter(
            Order.games_order == payload.pop("games_order")
        ).update(**payload)


orders = OrderService()