from flask import request, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from werkzeug.security import check_password_hash, generate_password_hash
from reusables import gen_pw, send_email, login_required
from datetime import timedelta
import datetime
import jwt
from models import Users
from db import db
from schemas import UserSchema


blp = Blueprint("logs", __name__, description = "Logging a user in and out")

#login
@blp.route("/login")
class Login(MethodView):
    def post(self):
        session.clear()
        user_data = request.get_json()
        #make sure both email and password were provided
        if user_data["email"] and user_data["password"]:
            usr = Users.query.filter_by(email=user_data["email"]).first()
            if usr:
                #compare password hashes
                if check_password_hash(usr.password,user_data["password"]):
                    #make session "permanant"
                    session.permanant = True
                    #create session and remember user
                    session["user_id"] = usr.userid
                    #define JWT and its expiration, in this case it is 2 days
                    token = jwt.encode({"user": user_data["email"], "exp": datetime.datetime.utcnow() + datetime.timedelta(days = 2)}, "key") #CHANGE KEY LATER ON
                    return {"logged in": "yes", "token": token}, 200 #we decode token because it is generated in bytes
                else:
                    abort(401, message="Unauthorized, wrong log in info")
            else:
                abort(403, message="No such user exists")
        else:
            abort(403, message="Include login info")
        
#LOG OUT
@blp.route("/logout")
class Logout(MethodView):
    @login_required
    def post(self):
        session.clear()
        return {"logged out": "yes"}, 200


# Register a new user
@blp.route("/register")
class Register(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        #user_data = request.get_json()
        if user_data["email"] and user_data["name"]:
            #checking if email already exists
            user = Users.query.filter_by(email=user_data["email"]).first()
            #if email exists don't allow account creation  
            if user:
                abort(409, message="Email is already in use")
            else:
                pw = gen_pw()
                #send email
                send_email(user_data["email"], password=pw)
                print(send_email(user_data["email"], password=pw).text)
                #hash password before passing it to db
                pw = generate_password_hash(pw)
                #pass new info to db
                newuser = Users(name=user_data["name"], email=user_data["email"], password=pw, balance=1000)
                db.session.add(newuser)
                db.session.commit()
                #tell user to finish registering using new email
                return {"Created":"finish registration through email"}, 201
    
        