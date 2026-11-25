import requests
from auth import Auth
from api import LocketAPI
import json


auth = Auth('your_email@gmail.com', 'your_password') 
token = auth.get_token()

api = LocketAPI(token)

account_info = api.GetAccountInfo()
# print(json.dumps(account_info, indent=4))  
momment = api.getLastMoment()
print(momment)