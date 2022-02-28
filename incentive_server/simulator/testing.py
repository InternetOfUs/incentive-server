import requests
url = 'http://127.0.0.1:5000/json'
data = requests.get(url).json()
print (data)