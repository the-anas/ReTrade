from flask import request, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort 
from schemas import TransactionSchema, StockSharesSchema, StockSharesUpdateSchema
from reusables import get_price_stock, login_required, token_required, daily_data, weekly_data, monthly_data
import datetime
from models import Users, StockShares, StockTransactions
from db import db
from datetime import timedelta
from schemas import TransactionSchema

blp = Blueprint("stock", __name__, description = "Operations on shares of stock")

@blp.route("/stock")
class Stock(MethodView):
    #get the price of a stock
    @login_required
    def get(self):
        user_data = request.get_json()
        if "symbol" in user_data:
            data = get_price_stock(user_data["symbol"])
            if data["Global Quote"] == {}:
                abort(404, message="Not Found, no such stock exists")
                #return {"Not Found": "No such stock exists"}
            else: #parsing files to get proper output
                price = data["Global Quote"]["05. price"]
                symbol = user_data['symbol'].upper()
                return {"symbol": symbol, "price": price}, 200
            
        else:
            abort(400, message="You must input data correctly")
    

    #get a plot of how the stock has been performing
    @login_required
    def post(self): 
        user_data = request.get_json()
        if "time frame" in user_data and "symbol" in user_data:
            if user_data["time frame"]=="monthly":
                return monthly_data(user_data["symbol"])
            elif user_data["time frame"]=="weekly":
                return weekly_data(user_data["symbol"]) 
            elif user_data["time frame"]=="daily":
                return daily_data(user_data["symbol"])
        else:
            abort(403, message="Include time frame and symbol fields")


    


#buy stock
@blp.route("/stock/buy")
class BuyStock(MethodView):
    @login_required
    @token_required
    def post(self):
        user_data = request.get_json()
        if "symbol" in user_data and "amount" in user_data:
            data = get_price_stock(user_data["symbol"])
            if data["Global Quote"] == {}:
                abort(404, message="No such stock exists")
            else: #parsing to get proper output
                price = float(data["Global Quote"]["05. price"])
                cost = price * user_data["amount"]
                symbol = user_data['symbol'].upper()                            
                #check user can afford stock
                userinfo = Users.query.filter_by(userid=session["user_id"]).first()
                balance = float(userinfo.balance)
                if balance >= cost:
                    old = balance
                    balance = balance - cost
                    #add to transactions in the DB
                    transaction = StockTransactions(name=user_data["symbol"], amount=user_data["amount"], price=cost, ttype="buy", userid=session["user_id"], time=datetime.datetime.utcnow() + datetime.timedelta(hours=1))
                    db.session.add(transaction)
                    db.session.commit()
                    #update balance in db
                    userinfo.balance=balance
                    db.session.commit

                    #check if a user owns this stock
                    owned = StockShares.query.filter_by(userid=session["user_id"], name=symbol).first()
                    if owned: #if so update entry for that stock
                        owned.amount= owned.amount + user_data["amount"]
                        db.session.commit()
                        return {"Succuessful": {
                        "old balance": old, 
                        "new balance": balance, 
                        "cost": cost, 
                        "symbol": symbol, 
                        "amount": user_data["amount"]
                    }}, 200

                    else: #if not include a new row in db
                        newstock = StockShares(name=symbol, amount=user_data["amount"], userid=session["user_id"])
                        db.session.add(newstock)
                        db.session.commit()

                    return {"Succuessful": {
                        "old balance": old, 
                        "new balance": balance, 
                        "cost": cost, 
                        "symbol": symbol, 
                        "amount": user_data["amount"]
                    }}, 200
                else:
                    abort(403, message=f"You do not have sufficient balance. Your balance is {balance} and the total cost is {cost}")
                    """
                    return {"Balance insufficient": {
                        "Balance": balance, 
                        "Cost": cost
                    }}, 200"""
            
        else:
            abort(403, message="Input data corrcetly")

#sell stock
@blp.route("/stock/sell")
class SellStock(MethodView):
    @login_required
    @token_required
    def post(self):
        user_data = request.get_json()
        if "symbol" in user_data and "amount" in user_data:
            data = get_price_stock(user_data["symbol"])
            if data["Global Quote"] == {}:
                abort(404, message="No such stock exists")
            else: #parsing files to get proper output
                price = float(data["Global Quote"]["05. price"])
                profit = price * user_data["amount"]
                symbol = user_data['symbol'].upper() 
                # check user owns stock
                owned = StockShares.query.filter_by(userid=session["user_id"], name=symbol).first()
                if owned:
                    #get user balance and number of owned shares
                    ownedamount = owned.amount
                    usr = Users.query.filter_by(userid=session["user_id"]).first()
                    balance = usr.balance

                    #check user owns sufficient stocks:
                    if user_data["amount"]<= ownedamount:
                        #update balance 
                        balance = balance+profit
                        usr.balance = balance
                        db.session.commit()
                        #update owned shares
                        ownedamount = ownedamount - user_data["amount"]
                        owned.amount = ownedamount
                        db.session.commit()
                        #update transactions
                        transaction = StockTransactions(name=user_data["symbol"], amount=user_data["amount"], price=profit, ttype="sell", userid=session["user_id"], time=datetime.datetime.utcnow()+ datetime.timedelta(hours=1))
                        db.session.add(transaction)
                        db.session.commit()
                        #delete rows from owned shares where the amount is 0
                        emptyrows = StockShares.query.filter_by(userid=session["user_id"], amount=0).all()
                        for row in emptyrows:
                            db.session.delete(row)
                            db.session.commit()
                            

                        return {"Succussflly sold": {
                            "symbol": symbol, 
                            "amount": user_data["amount"], 
                            "Remaining share of that stock": ownedamount, 
                            "Profit": profit, 
                            "balance": balance
                        }}

                    else:
                        abort(404, message=f"You do not own enough of this stock to sell {user_data['amount']} shares")
                else:
                    abort(403, message="You do not own this stock")
