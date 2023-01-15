from flask import request, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort 
from werkzeug.security import generate_password_hash
from models import Users, StockShares, StockTransactions
from db import db


blp = Blueprint("tests", __name__, description = "Data that helps when testing the API")

# Get all transactions
@blp.route("/transactions") 
class Transactions(MethodView):
    def get(self):
        transactions = StockTransactions.query.all()
        all = {"transactions": []}
        for tran in transactions:
            json_str = {"id": tran.tid, "name": tran.name, "amount": tran.amount, "price" : tran.price, "ttype": tran.ttype, "userid": tran.userid, "time": tran.time}
            all["transactions"].append(json_str) 
        return all, 200

# Get all owned stocks
@blp.route("/owned")
class Owned(MethodView):
    def get(self):
        stocks = StockShares.query.all()
        all = {"Stocks": []}
        for stock in stocks:
            json_str = {"id": stock.sid, "name": stock.name, "amount": stock.amount, "userid" : stock.userid}
            all["Stocks"].append(json_str) 
        return all, 200

#Get info about current user
@blp.route("/whoami")
class Whoami(MethodView):
    def get(self):
        usr = Users.query.filter_by(userid=session["user_id"]).first()
        return {"Current user": {
            "Name": usr.name, 
            "User ID": usr.userid, 
            "email": usr.email

        }}, 200

@blp.route("/testusers")
class All(MethodView):
    # View all users
    def get(self):   
        users = Users.query.all()
        print(users)
        all = {"Users": []}
        for user in users:
            json_str = {"name": user.name, "email": user.email, "balance" : user.balance, "password": user.password}
            all["Users"].append(json_str) 
        return all, 200

    # register a new user, shorter process, won't be available for users
    def post(self):
        user_data= request.get_json()
        print(user_data)
        user_data["password"] = generate_password_hash(user_data["password"])
        user = Users(**user_data)
        db.session.add(user)
        db.session.commit()
        return {"Worked": "yes"}, 201