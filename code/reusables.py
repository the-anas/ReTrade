import requests
from functools import wraps
from flask import session, request, send_file
import string
import random
import jwt
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import io
from flask_smorest import abort

sessionkey = "key"

key = "ZNAOQNV7FG88SNA7"

plt.switch_backend('agg') #avoid loop outside main thread error, allows plt to work with backends

def daily_data(symbol):
    plt.clf()
    ts = TimeSeries(key=key, output_format='pandas')
    data, meta = ts.get_daily_adjusted(symbol)
    plt.plot(data['4. close'])
    plt.title(f'Daily closing price for {symbol} stock')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

def weekly_data(symbol):
    plt.clf()
    ts = TimeSeries(key=key, output_format='pandas')
    data, meta = ts.get_weekly_adjusted(symbol)
    plt.plot(data['4. close'])
    plt.title(f"Weekly closing price for {symbol} stock")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')
    
def monthly_data(symbol):
    plt.clf()
    ts = TimeSeries(key=key, output_format='pandas')
    data, meta = ts.get_monthly_adjusted(symbol)
    plt.plot(data['4. close'])
    plt.title(f'Monthly closing price for {symbol} stock')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')
    
    

def get_price_stock(symbol):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={key}'
    r = requests.get(url)
    data = r.json()
    return data
    

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return {"Unathourized":"User not logged in"}, 401
        return f(*args, **kwargs)
    return decorated_function



def send_email(email, password):
    apikey = "key-ff1fe9c3f6f3bda4938446103829df69"
    domain = "sandboxe838aec0d31f4d4e87c7fee2d734678a.mailgun.org"
    return requests.post(
		f"https://api.mailgun.net/v3/{domain}/messages",
		auth=("api", apikey),
		data={"from": f"<mailgun@{domain}>",
			"to": [email],
			"subject": "Registration at ReTrade",
			"text": f"To confirm that you do indeed own this email, please log in using the follwoing password at first: {password}     You can change this password later on"})


def gen_pw():
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(10))
    return result_str

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'x-access' not in request.headers:
            abort(403, message="Missing token")
        token = request.headers['x-access'] #use this to get token, try to use headers
        try:
            data = jwt.decode(token,"key", algorithms=['HS256']) #edit this key later
        except:
            return {"message": "token is invalid"}, 403
        return f(*args, **kwargs)
    return decorated
