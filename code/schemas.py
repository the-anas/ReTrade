from marshmallow import Schema, fields

#Schema for registering a new user
class UserSchema(Schema):
    userid = fields.Int(dump_only=True) 
    name = fields.Str(required=True)
    email = fields.Email(required=True) 

#Schema for updating user info
class UserUpdateSchema(Schema):
    balance = fields.Float()
    password = fields.Str()

#Schema for recording a transaction
class TransactionSchema(Schema):
    tid = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    amount = fields.Int(required=True)
    price = fields.Float(required=True)
    ttype = fields.Str(required=True)
    userid = fields.Int(required=True) 
    time = fields.DateTime(required=True)

#Schema for buying a stock that is not previously owned
class StockSharesSchema(Schema):
    sid = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    amount = fields.Int(requried=True)
    userid = fields.Int(required=True)

#Schema for updating owned amount of stock after sell or buy
class StockSharesUpdateSchema(Schema):
    amount = fields.Int()

    