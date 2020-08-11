from boto.cloudfront.distribution import Distribution
from boto.cloudfront import CloudFrontConnection
from botocore.signers import CloudFrontSigner
import datetime
import json
import jwt
import rsa
import boto3
import random
import math
import pymysql

client = boto3.client('lambda')
JWT_SECRET = 'Some 2048 Char String'
JWT_ALGORITHM = 'HS256'
endpoint = 'DB_ENDPOINT'
db_username = 'DB_USER'
db_password = 'DB_PASSWORD'
database_name = 'DB_NAME'
key_id = 'APKAJKUYEXAMPLE7RD0A'
URL_EXPIRE_TIME = 60
connection = pymysql.connect(endpoint, user=db_username, passwd=db_password, db=database_name)
cursor = connection.cursor()

def gen_Url(url):
	expire_date = (datetime.datetime.utcnow() + datetime.timedelta(seconds=URL_EXPIRE_TIME)).strftime('%Y-%m-%d %H:%M:%S')
	expire_date = datetime.datetime.strptime(expire_date, '%Y-%m-%d %H:%M:%S')
	cf_signer = CloudFrontSigner(key_id, rsa_signer)
	return cf_signer.generate_presigned_url(url, date_less_than=expire_date)

def rsa_signer(message):
    private_key = open('key.pem', 'r').read()
    return rsa.sign(message, rsa.PrivateKey.load_pkcs1(private_key.encode('utf8')),'SHA-1')

def Invoke_Request(input):
	return client.invoke(
			FunctionName='arn:aws:lambda:us-east-1:NUMBER_HERE:function:YOUR_FUNCTIONS_NAME',#arn:aws:lambda:us-east-1:NUMBERS:function:invoke
			InvocationType='RequestResponse', # Use Event to not listen for response.
			Payload=json.dumps(input)
			)

def verify_token(token):
    try:
        decoded = json.loads(json.dumps(jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)))
        return 0, decoded['user_id'], decoded['exp']
    except:
        return -1, '', 0
        
def gen_Secure_Random(min, max):
    systemRandom = random.SystemRandom()
    return systemRandom.randint(min, max)
    
def lambda_handler(event, context):
	
	valid, username, expiry = verify_token(event['cookie'])
	if valid < 0:
		return {
			'Message': "Invaild Token"
		}
	else:
		
		#
	    #Code 50 = Get Variables From Bank
	    #
		if event["Code"] == 50:
			
			requestInput = {'Username': event['Username'], 'Code': event['bankCode'] }
			return json.load(Invoke_Request(requestInput)['Payload'])
		#
		#Code 150 = Establish Commitment For Bank Login & Return Challege
	    #
		elif event["Code"] == 150:
			requestInput = {'Username': event['Username'], 'Commit': event['Commit'], 'Code': event['bankCode'] }
			return json.load(Invoke_Request(requestInput)['Payload'])
		#
		#Code 250 = Compute Bank Verification
	    #
		elif event["Code"] == 250:
			#
			#Implement Downloads Urls
			#
			requestInput = {'Username': event['Username'], 'Y': event['Y'], 'Code': event['bankCode'], 'price': event['price'], 'StoreId': 'ZKStore' }
			resp = json.load(Invoke_Request(requestInput)['Payload'])
			if resp['code'] == 200:
				cursor.execute("INSERT INTO Transactions (username, transnumber, ordertotal, productid) VALUES (%s, %s, %s, %s)", (username, gen_Secure_Random(1, math.pow(2, 16)), event['price'], event['prodId']))
				connection.commit()
				if (event['prodId'] == 1):
					url = gen_Url("https://private.EXAMPLE.com/YouTube_Vanced.apk")
				elif (event['prodId'] == 2):
					url = gen_Url("https://private.EXAMPLE.com/Service_Disabler.apk")
				elif (event['prodId'] == 3):
					url = gen_Url("https://private.EXAMPLE.com/Dcoder_Compiler.apk")
				return { 'code': 200, 'Message': "Successful Payment", 'Url': url }
			return json.load(Invoke_Request(requestInput)['Payload'])
		#
		#Code 250 = Reestablish Bank Communications
		#
		elif event["Code"] == 350:
			requestInput = {'Username': event['Username'], 'P': event["P_Val"], 'Q': event["Q_Val"], 'A': event["A_Val"], 'V': event["V_Val"], 'Code': 350 }
			return json.load(Invoke_Request(requestInput)['Payload'])