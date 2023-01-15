from flask import Flask
from datetime import timedelta
from flask_smorest import Api
from reusables import sessionkey
#import blueprints
from resources.user import blp as UserBlueprint
from resources.tests import blp as TestBlueprint
from resources.logs import blp as LogBlueprint
from resources.stock import blp as StockBlueprint
#import db and models
from db import db
from models import Users, StockShares, StockTransactions


app = Flask(__name__)

# SWAGGER CONGIF
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "ReTrade"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# SQL ALCHEMY CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#connect app to flask-sqlachemy and avoid outside of app context error
db.init_app(app)

#secret key to encrypt session data and session lifetime
app.secret_key = sessionkey #defined in reusables
app.permanent_session_lifetime = timedelta(days=2)
  

api = Api(app)



@app.before_first_request
def create_tables():
        db.create_all()

api.register_blueprint(UserBlueprint)
api.register_blueprint(TestBlueprint)
api.register_blueprint(LogBlueprint)
api.register_blueprint(StockBlueprint)



