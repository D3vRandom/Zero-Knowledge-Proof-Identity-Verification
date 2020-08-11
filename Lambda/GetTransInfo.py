import json
import jwt
import pymysql
import datetime
import array

endpoint = 'DB_ENDPOINT'
db_username = 'DB_USER'
db_password = 'DB_PASSWORD'
database_name = 'DB_NAME'
JWT_SECRET = 'Some 2048 Char String'
JWT_ALGORITHM = 'HS256'

def verify_token(token):
    try:
        decoded = json.loads(json.dumps(jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)))
        return  0, decoded['user_id'], decoded['exp']
    except:
        return -1, '', 0

def lambda_handler(event, context):
	token = event['cookie']
	valid, username, expiry = verify_token(token)
	if valid < 0:
		return {
			'Message': "Invaild Token"
		}
	else:
		connection = pymysql.connect(endpoint, user=db_username, passwd=db_password, db=database_name)
		cursor = connection.cursor()
		cursor.execute("Select Count(username) From Transactions Where username=%s", username)
		row = cursor.fetchone()
		length = row[0]
		if row[0] >= 1:
			cursor.execute("Select * From Transactions Where username=%s", username)
			row = cursor.fetchall()
			strings = []
			for record in row:
				strings.append(str(record[0]) + ":" + str(record[1])  + ":" + str(record[2])  + ":" + str(record[3])  + ":" + str(record[4]) + ":")
			string = ""
			for strin in strings:
				string = string + strin
			return {
				'length': length,
				'string': string
			}