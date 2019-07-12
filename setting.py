class ProConfig:
    DEBUG = False
    DATABASE_URL = ""


class DevConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@127.0.0.1:3306/payment?charset=utf8"
    SQLALCHEMY_TRACK_MODIFICATIONS = False



#761棋牌建立秘钥

APP_ID_761 = "LASDGYOMLHA"
APP_KEY = "SKJCUHNHLLOSJNMN"
HOST = "http://3e22ff7f.ngrok.io"