from flask import Flask, escape, request, jsonify, Response
import random
from random import sample
from json import dumps


app = Flask(__name__)


@app.route('/',methods=['GET','POST'])
def response():
    multi_dict = request.args
    array = []
    for key in multi_dict:
        array.append(multi_dict.get(key))
        # print (multi_dict.getlist(key))
    return str(array)
# build_products(14617)

@app.route('/confirmation',methods=['GET','POST'])
def confirmation():
    print('confirmation')
    return 'hi'

if __name__ == "__main__":
    app.run(host='10.4.28.90',port=9000,debug=True)