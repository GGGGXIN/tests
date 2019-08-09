from rest_framework.views import APIView
from rest_framework.response import Response
from gateway.jhp import jhp
from init_db import init_jhp


class JHPView(APIView):
    def post(self, request):
        data = request.data
        print("回调数据", data)
        return Response(jhp.on_notify(data))

    def get(self, request):
        init_jhp()
        return Response("ok")