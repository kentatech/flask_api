import time
import math
import base64
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth

consumer_key = 'owBOAw7NmTdmhWyksamr1Wx0tJH5cIA9qGTgGP2E5na6enpH'
consumer_secret = 'NN0kQ4pzjqqB1INieMQrd8QooM3gG7A4F4CYyY9gSoXPAIgXLcdAi6u7ArOqHcg0'
short_code ="600988"
app_url="https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
saf_pass_key="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
saf_access_token_api="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
saf_stk_push_api="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
saf_stk_push_query_api="https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"

def get_mpesa_access_token():
    try:
        res = requests.get(saf_access_token_api,auth=HTTPBasicAuth(consumer_key, consumer_secret))
        token = res.json()['access_token']

        headers = {"Authorization": f"Bearer {token}","Content-Type": "application/json"}
    except Exception as e:
        print(str(e), "error getting access token")
        raise e

    return headers

headers = get_mpesa_access_token()
print(headers)

def generate_password():
    timestamp = datetime.now.strftime("%Y%m%d%H%M%S")
    password_str = short_code + saf_pass_key + timestamp
    password_bytes = password_str.encode()
    
    return base64.b64encode(password_bytes).decode("utf-8")

print(get_mpesa_access_token())

#instructions
#ngrok config + take consume key and consume secret
#go to daraja c2b; copy short code and app url for register
#Login Daraja - Go to api - Mpesa Express Simulate (copy pass key)