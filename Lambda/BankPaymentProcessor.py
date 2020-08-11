import pymysql
import random
import math

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
store = 'ZKStore'

def lambda_handler(event, context):
    connection = pymysql.connect(endpoint, user=db_username, passwd=db_password, db=database_name)
    cursor = connection.cursor()
    #
    #Code 50 = Get User Variables From Bank Database
    #
    if event["Code"] == 50:
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
                'P': P,
                'Q': Q,
                'A': A,
                'V': V
            }
        else:
            return {
                'code': 500,
                'message': "Username Doesn't Exist With Our Bank. Please Consider Registering."
            }
    #
    #Code 150 = Establish Commitment For Login & Return Challege
    #
    elif event["Code"] == 150:
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
                'message': "User Found!! Bank Payment Processor Challege",
                'Challenge': challenge
            }
        else:
            return{
                'code': 404,
                'message': "Username Doesn't Exist With Our Bank. Stop Messing Around!!"  
            }
    #
    #Code 250 = Compute Verification
    #
    elif event["Code"] == 250:
        connection = pymysql.connect(endpoint, user=db_username, passwd=db_password, db=database_name)
        cursor = connection.cursor()
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
                total = float(event["price"])
                recvUser = event["StoreId"]
                cursor.execute("INSERT INTO Transactions (username, transnumber, accountdebt, accountcredit) VALUES (%s, %s, %s, 0.00)", (username, gen_Secure_Random(1, math.pow(2, 16)), total))
                cursor.execute("INSERT INTO Transactions (username, transnumber, accountdebt, accountcredit) VALUES (%s, %s, 0.00, %s)", (recvUser, gen_Secure_Random(1, math.pow(2, 16)), total))
                connection.commit()
                return {
                    'code': 200,
                    'message': "Bank Processor Log In Success",
                    'total': total,
                    'StoreId': recvUser
                    } 
            else:
                return {
                    'code': 404,
                    'message': "Wrong Passsword"
                }
                
        else:
            return {
                'message': "Username Doesn't Exist With Our Bank. Stop Messing Around!!",
                'username': username
            }
    elif event["Code"] == 350:
        username = event['Username']
        P_Val = int(event["P"])
        Q_Val = int(event["Q"])
        A_Val = int(event["A"])
        V_Val = int(event["V"])
        cursor.execute("Select Count(username) From Users Where username=%s", username)
        row = cursor.fetchone()
        if row[0] == 0:
            return {
                'code': 500,
                'Message': "Registration Utilizing Rotating Functionality Is Prohibited"
            }
        else:
            cursor.execute("UPDATE Users SET p = %s, q = %s, a = %s, v = %s, r = NULL, commitment = NULL  WHERE username = %s;", (P_Val, Q_Val, A_Val, V_Val, username))
            connection.commit()
            return{
                'code': 200,
                'MESSAGE': "User Bank Variables Have Been Rotated",
            }
    else:
        return -1