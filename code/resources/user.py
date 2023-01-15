from flask import request, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort 
from schemas import UserUpdateSchema
from werkzeug.security import generate_password_hash
from reusables import get_price_stock, login_required, token_required
from models import Users, StockShares, StockTransactions
from db import db


blp = Blueprint("user", __name__, description = "Operations on a logged in user")

@blp.route("/user")
class loggedUser(MethodView):
    #getting user info
    @login_required
    def get(self):
        stocks = StockShares.query.filter_by(userid=session["user_id"]).all()
        user = Users.query.filter_by(userid=session["user_id"]).first()
        all = {"User":user.name, "Email": user.email, "Balance": user.balance, "Stocks": []}
        Total = 0
        for stock in stocks:
            data = get_price_stock(stock.name)
            price = float(data["Global Quote"]["05. price"])
            Asseteve = price*stock.amount
            Total = Total + Asseteve
            json_str = {"name": stock.name, "amount": stock.amount, "userid" : stock.userid, "Current Price": price, "Current total Asset value": Asseteve}
            all["Stocks"].append(json_str)
        all["Total value of assets"] = Total
        return all, 200
    
    #delete user 
     
    @login_required
    @token_required
    def delete(self):
        user = Users.query.filter_by(userid=session["user_id"]).first()
        db.session.delete(user)
        db.session.commit()
        session.clear()
        return {"Result": "User succussfuly deleted"}, 200
    
    #changin user password
    @login_required
    @token_required
    @blp.arguments(UserUpdateSchema)
    def put(self, user_data): 
        #user_data = request.get_json() 
        if "password" in user_data:
            user = Users.query.filter_by(userid=session["user_id"]).first()
            user.password = generate_password_hash(user_data["password"])
            db.session.commit()
            return {"Succuss": "Password is now changed"}, 200
        else:
            abort(403, message="Provide old password to be able to change it")

@blp.route("/user/transactions")
class UserTransaction(MethodView):
    #View transactions of logged in user
    def get(self):
        transactions = StockTransactions.query.filter_by(userid=session["user_id"]).all()
        all = {"transactions": []}
        for tran in transactions:
            json_str = {"id": tran.tid, "name": tran.name, "amount": tran.amount, "price" : tran.price, "ttype": tran.ttype, "userid": tran.userid, "time": tran.time}
            all["transactions"].append(json_str) 
        return all, 200

@blp.route("/user/balance")
class UserShares(MethodView):
    #Increace user current balance 
    @login_required
    def put(self): 
        user_data = request.get_json()
        user = Users.query.filter_by(userid=session["user_id"]).first()
        if "amount" in user_data:
            amount = user_data["amount"]
            user.balance = user.balance + amount
            db.session.commit()
            return {"Status": f"Balance increaced by {amount}"}, 200
        else:
            abort(403, message="Provide amount that needs to be added inside 'amount' key")
