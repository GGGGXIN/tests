from flask import Flask
from flask_cors import *
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from views import api_b
from setting import ProConfig, DevConfig


def create_app(mode):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    if mode == "pro":
        app.config.from_object(ProConfig)
    else:
        app.config.from_object(DevConfig)
    app.register_blueprint(api_b)
    db.init_app(app)
    return app


if __name__ == '__main__':
    app = create_app("dev")
    app.run(port=8000)
