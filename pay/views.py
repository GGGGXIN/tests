import json
import uuid
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import payments
from .settings import APP_KEY


class Order(APIView):

    def post(self, request):
         data = request.data
         sign = payments.sign(data, APP_KEY, excludes=["sign"])
         print(sign)
         if sign != data.get("sign"):
             return Response(json.dumps({"code": 40001, "error": "无效的签名"}, ensure_ascii=False))
         agent = request.META.get('HTTP_USER_AGENT', None)
         channel = payments.get_channels(agent, data["type"])
         print(channel)
         if not channel:
             return Response(json.dumps({"code": "4004", "error": "无可用通道"}, ensure_ascii=False))
         order_no = f"NO{uuid.uuid4()}"
         order = payments.create_order({"order_no": order_no,
                                      "games_order": data["order_no"],
                                      "amount": data["amount"],
                                      "channel_id": channel.id,
                                      "channel_name": channel.title,
                                      "client_ip": request.META.get("REMOTE_ADDR", ""),
                                      "notify_url": data["notify_url"],
                                      "created": int(time.time())})
         server = payments.get_service(channel.gateway_name)
         if not server:
             return Response(json.dumps({"code": "4004", "error": "无可用通道"}, ensure_ascii=False))
         payload = server.prepare_charge(order, channel)
         return Response(server.platform_pay(payload))