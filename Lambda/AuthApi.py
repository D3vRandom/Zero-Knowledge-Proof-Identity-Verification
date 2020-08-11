from boto.cloudfront.distribution import Distribution
from boto.cloudfront import CloudFrontConnection
from botocore.signers import CloudFrontSigner
import datetime
import pymysql
import random
import struct
import boto3 #Maybe Remove
import json
import math
import jwt
import rsa
import os

def gen_Url():
	expire_date = (datetime.datetime.utcnow() + datetime.timedelta(seconds=URL_EXPIRE_TIME)).strftime('%Y-%m-%d %H:%M:%S')
	expire_date = datetime.datetime.strptime(expire_date, '%Y-%m-%d %H:%M:%S')
	cf_signer = CloudFrontSigner(key_id, rsa_signer)
	return cf_signer.generate_presigned_url(url, date_less_than=expire_date)

def generate_token(username):
    payload = {
        'user_id': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    gen_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return gen_token

def verify_token(token):
    try:
        decoded = json.loads(json.dumps(jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)))
        return 0, decoded['user_id'], decoded['exp']
    except:
        return -1, '', 0

def rsa_signer(message):
    private_key = open('key.pem', 'r').read()
    return rsa.sign(message, rsa.PrivateKey.load_pkcs1(private_key.encode('utf8')),'SHA-1')

def gen_Secure_Random(min, max):
    systemRandom = random.SystemRandom()
    return systemRandom.randint(min, max)

def compute_Identification_Verification(alpha, response, public_Key, challenge, p):
    return pow(alpha, response, p) * pow(public_Key, challenge, p) % p


#
#
#HANDLER STARTS HERE
#
#

endpoint = 'DB_ENDPOINT'
db_username = 'DB_USER'
db_password = 'DB_PASSWORD'
database_name = 'DB_NAME'
url = "AUENTICATED_URL"
key_id = 'APKAJKUYEXAMPLE7RD0A'
JWT_SECRET = 'Some 2048 Char String'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600
URL_EXPIRE_TIME = 480
        
def lambda_handler(event, context):
    connection = pymysql.connect(endpoint, user=db_username, passwd=db_password, db=database_name)
    cursor = connection.cursor()
    
    if event["Code"] == 250:

        username = event["Username"]
        P_Val = int(event["P_Val"])
        Q_Val = int(event["Q_Val"])
        A_Val = int(event["A_Val"])
        V_Val = int(event["V_Val"])
        cursor.execute("Select Count(username) From Users Where username=%s", username)
        row = cursor.fetchone()
        if row[0] == 0:
            cursor.execute("INSERT INTO Users (username, p, q, a, v) VALUES (%s, %s, %s, %s, %s)", (username, P_Val, Q_Val, A_Val, V_Val))
            connection.commit()
            return{
                'code': 200,
                'token': generate_token(username),
                'username': username,
                'url': gen_Url(),
                'message': "User Added Into Users Table",
                'P_Val': P_Val,
                'Q_Val': Q_Val,
                'A_Val': A_Val,
                'V_Val': V_Val
            }
        else:
            return{
                'code': 500,
                "message": "User Already Exists",
                'user': username
            } 
    elif event["Code"] == 350:

        username = event["Username"]
        cursor.execute("Select Count(username) From Users Where username=%s", username)
        row = cursor.fetchone()
        if row[0] == 1:
            cursor.execute("SELECT p, q, a, v FROM Users WHERE username=%s", username)
            row = cursor.fetchone()
            P = row[0]
            Q = row[1]
            A = row[2]
            V = row[3]
            return{
                'code': 200,
                'MESSAGE': "User Found These are you variables",
                'P': P,
                'Q': Q,
                'A': A,
                'V': V
            }
        else:
            return{
                'code': 500,
                'MESSAGE': "User Not Found"
            }
    elif event["Code"] == 450:

        username = event["Username"]
        commitment = event["Commit"]
        cursor.execute("Select Count(username) From Users Where username=%s", username)
        row = cursor.fetchone()
        if row[0] == 1:
            cursor.execute("Select q From Users Where username=%s", username)
            row = cursor.fetchone()
            q = row[0]
            bits = math.floor(math.log(q, 2)+1)
            t = bits - 1
            challenge = gen_Secure_Random(1, math.pow(2,t))
            cursor.execute("UPDATE Users SET commitment=%s, r=%s WHERE username=%s", (commitment, challenge, username))
            connection.commit()
            return{
                'code': 200,
                'MESSAGE': "Found User",
                'Challenge': challenge
            }
        else:
            return{
                'code': 500,
                'MESSAGE': "User Not Found",
                'user': username
            }
    elif event["Code"] == 550:

        username = event["Username"]
        y = int(event["Y"])
        cursor.execute("Select Count(username) From Users Where username=%s", username)
        row = cursor.fetchone()
        if row[0] == 1:
            cursor.execute("Select p, q, a, v, r, commitment From Users Where username=%s", username)
            row = cursor.fetchone()
            p = row[0]
            q = row[1]
            a = row[2]
            v = row[3]
            r = row[4]
            commit = row[5]
            verification = compute_Identification_Verification(a, y, v, r, p)
            if commit == verification:
                return {
                    'code': 200,
                    'msg': "LogIn Success",
                    'token': generate_token(username)
                }
            else:
                return {
                    'code': 500,
                    'msg': "Wrong Passsword"
                }
        else:
            return{
                "message": "User Not Found",
                'username': username
            }
    elif event["Code"] == 650:
        token = event['cookie']
        valid, username, expiry = verify_token(token)
        if valid < 0:
            return {
                'Message': "Invaild Token"
            }
        else:
            P_Val = int(event["P_Val"])
            Q_Val = int(event["Q_Val"])
            A_Val = int(event["A_Val"])
            V_Val = int(event["V_Val"])
            cursor.execute("Select Count(username) From Users Where username=%s", username)
            row = cursor.fetchone()
            if row[0] == 0:
                return {
                    'code': 500,
                    'Message': "Registration Utilizing Login Functionality Is Prohibited"
                }
            else:
                cursor.execute("UPDATE Users SET p = %s, q = %s, a = %s, v = %s, r = NULL, commitment = NULL  WHERE username = %s;", (P_Val, Q_Val, A_Val, V_Val, username))
                connection.commit()
                return{
                    'code': 200,
                    'MESSAGE': "User Variables Have Been Rotated",
                    'url': gen_Url()
                }
    else:
        return -1