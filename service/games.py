import json
import hashlib
import time
from urllib import parse, request

from utils.helper import AESCoder


class GameService():
    """
    agent  int 代理id
    timestamp int 时间戳秒
    acc string 用户账号
    orderid  流水号 string
    money 金额 float
    sign  md5
    """
    API_URL = "http://tapi.761city.com:10018/"
    AGENT = "1190"
    KEY = "b02ea4615c89f7873a4cabfbe9e68963"

    def create_recharge(self):
        #上分
        recharge_path = self.API_URL + "agent/payup"
        acc = "quanyou"
        orderid = "NO2019062867854325"
        money = 100.00
        timestamp = int(time.time())
        params = {"money": money, "acc": acc, "orderid": orderid}
        aes_coder = AESCoder(self.KEY)
        data = aes_coder.encrypt(json.dumps(params))
        sign = hashlib.md5((self.AGENT + str(timestamp) + self.KEY).encode("utf-8")).hexdigest()
        url_params = {
            "agent": self.AGENT,
            "timestamp": timestamp,
            "sign": sign,
            "params": str(data, encoding="utf-8")
        }
        values = parse.urlencode(url_params).encode("utf-8")
        print(values)
        res = request.Request(recharge_path, values)
        response = request.urlopen(res)
        print(response.read().decode())


game_services = GameService()