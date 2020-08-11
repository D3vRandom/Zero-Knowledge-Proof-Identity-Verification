
import datetime
import pymysql
import random
import struct
import json
import math
import os

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

def lambda_handler(event, context):

    if event["Code"] == 250:
        connection = pymysql.connect(endpoint, user=db_username, passwd=db_password, db=database_name)
        cursor = connection.cursor()
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
                'message': "User Added Into Users Table In Bank DB",
                'code': 200
            }
        else:
            return{
                'message': "User Already Exists In Bank",
                'username': username,
                'code': 404
            } 
    elif event["Code"] == 350:
        connection = pymysql.connect(endpoint, user=db_username, passwd=db_password, db=database_name)
        cursor = connection.cursor()
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
            return {
                'code': 200,
                'MESSAGE': "This is your variables",
                'P': P,
                'Q': Q,
                'A': A,
                'V': V
            }
        else:
            return{
                'MESSAGE': "User Not Found"
            }
    elif event["Code"] == 450:
        connection = pymysql.connect(endpoint, user=db_username, passwd=db_password, db=database_name)
        cursor = connection.cursor()
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
                'MESSAGE': "Generating Resonse",
                'Challenge': challenge
            }
        else:
            return{
                'code': 404,
                'MESSAGE': "User Not Found"
            }
    elif event["Code"] == 550:
        connection = pymysql.connect(endpoint, user=db_username, passwd=db_password, db=database_name)
        cursor = connection.cursor()
        msg = "Username Not Found"
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
                    'RESPONSE': "Bank Log In Success"
                    }
            else:
                return {
                    'RESPONSE': "Wrong Passsword"
                }
        else:
            return{
                "message": "User Not Found",
                'username': username
            }
    else:
        return -1
