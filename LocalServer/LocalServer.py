from flask import Flask, request, jsonify, make_response
import requests
import struct
import random
import math
import os

app = Flask(__name__)
# For some reason only JSON objects are cached between requests.
offset = {}

@app.route('/', methods=['OPTIONS','POST'])
def ReturnData():

    response = make_response()
    if request.method == 'OPTIONS': 

        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    elif request.method == 'POST': 

        code = int(request.form['Code'])
        if code == 100:

            password = request.form['Password']
            p = int(request.form['P'])
            q = int(request.form['Q'])
            alpha = int(request.form['A'])
            priv_Key = covert_String_Int(password, q)
            public_Key = compute_Public_Key(alpha, priv_Key, p, q)
            response = jsonify({"P": p, "Q": q, "A": alpha, "V": public_Key})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        elif code == 200:

            p = int(request.form['P'])
            q = int(request.form['Q'])
            alpha = int(request.form['A'])
            offset['K'] = gen_Secure_Random(1, q - 1)
            r = compute_Public_Commitment(alpha, offset['K'], p)
            response = jsonify({"Commitment": r})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        elif code == 300:

            q = int(request.form['Q'])
            challenge = int(request.form['R'])
            print(request.form['Pass'])
            priv_Key = covert_String_Int(request.form['Pass'], q)
            print("300: %s" % (priv_Key))
            y = compute_Challenge_Response(offset['K'], priv_Key, challenge, q)
            response = jsonify({"Response": y})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

def compute_Public_Key(alpha, priv_Key, p, q):
    return pow(alpha, q - priv_Key, p)

def covert_String_Int(priv_Key, q):
    val = 1
    order = 1
    for char in priv_Key:
        val *= int(math.pow(ord(char), order))
        order += 1
    return val % q

def compute_Public_Commitment(alpha, offset, p):
    return pow(alpha, offset, p)

def gen_Secure_Random(min, max):
    systemRandom = random.SystemRandom()
    return systemRandom.randint(min, max)

def compute_Challenge_Response(offset, priv_Key, challenge, q):
    return offset + priv_Key * challenge % q

if __name__ == '__main__':
    app.debug = True
    app.run(host = '127.0.0.1', port = 5000)