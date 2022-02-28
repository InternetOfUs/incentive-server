from flask import Flask, escape, request
dataa = []
app = Flask(__name__)
@app.route('/json', methods=['GET', 'POST'])
def json():
    if request.method == 'POST':
        content = request.get_json()
        dataa.append(content)
        return "Thanks", 200
    else :
        return dataa.pop()
# def add_message(uuid):
#     if request.method == 'POST':
#         content = request.get_json(silent=True)
#         # data.append(content)
#         return uuid , 200
#     else:
#         return dataa.pop()

