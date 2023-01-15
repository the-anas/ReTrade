from db import db

#USER MODEL

class Users(db.Model): #inheritance from a model class which already contains helpful methods, etc...
    __tablename__ = "users"

    userid = db.Column("userid", db.Integer, primary_key=True)
    name = db.Column("name", db.String(20), nullable=False)
    email = db.Column("email", db.String(20), nullable=False, unique=True)
    password = db.Column("password", db.String(20), nullable=False)
    balance = db.Column("balance", db.Float(precision = 5))
    
    def __init__(self, name, email, password, balance=0):
        self.name = name
        self.email = email
        self.password = password
        self.balance = balance

#OWNED SHARE MODEL

class StockShares(db.Model):
    __tablename__ = "stockshares"

    sid = db.Column("sid", db.Integer, primary_key=True)
    name = db.Column("name", db.String(20), nullable=False)
    amount = db.Column("email", db.Integer, nullable=False)
    userid = db.Column("userid", db.Integer, db.ForeignKey("users.userid"), unique= False, nullable=False)
    
    def __init__(self, name, amount, userid):
        self.name = name
        self.amount = amount
        self.userid = userid


#STOCK TRANSACTIONS MODEL
class StockTransactions(db.Model): 
    __tablename__ = "stransactions"

    tid = db.Column("sid", db.Integer, primary_key=True)
    name = db.Column("name", db.String(20), nullable=False)
    amount = db.Column("email", db.Integer, nullable=False)
    price = db.Column("price", db.Float(precision=5), nullable=False)
    ttype = db.Column("ttype", db.String(20), nullable=False)
    userid = db.Column("userid", db.Integer, db.ForeignKey("users.userid"), unique= False, nullable=False)
    time = db.Column("time", db.DateTime)
    
    def __init__(self, name, amount, price, ttype, userid, time):
        self.name = name
        self.amount = amount
        self.price = price    
        self.ttype = ttype
        self.userid = userid
        self.time = time 
