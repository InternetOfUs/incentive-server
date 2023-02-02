import os
import requests

print('call incentive_server messages')
url = f'http://nginx/api/StartIncentivesMassages/'
r = requests.get(url, headers={"x-wenet-component-apikey": os.environ.get('COMP_AUTH_KEY')})
print(f'Done incentive_server messages: {r.status_code}')
