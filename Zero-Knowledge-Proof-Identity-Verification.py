#!/usr/bin/env python
# coding: utf-8

import random
import math
import os
import struct
'''
Author: ジョシュアモル
Date: April, 22, 2020
Contact: devr4ndom@gmail.com
Version: 2.3
'''

'''
FUNCTIONS:
'''

def is_Prime(prime):
    i = 2
    while (prime % i != 0 and i < prime - 1):
        i += 1
        if i % 500000000 == 0:
            print("i == %d / %d\n%f%% Done....." % (i, prime, i / prime * 100))
    if (prime % i != 0):
        return prime
    return 0

def gen_Alpha_Q(min, p):
    #alphaList = []
    pm1 = p - 1
    temp = pm1
    temp = temp / 2
    if (temp % 2 == 0):
        temp += 1
    for q in range(int(temp), min, -2):
        if (pm1 % q == 0):
            print("Q: %d  Has been found to be a divisor of P: %d - 1\nDetermining Primality of Q" % (q, p))
            if (is_Prime(q) > 0):
                #Looping Alpha's
                print("***********\nDetermining: (Alpha)。。0_0\nThis Should? Be Quicker シ\n***********")
                for alpha in range(pm1, 2, -1):
                    #This if statement speeds up the program dermaticly as it determines if alpha is
                    #vaild before checking all O(N) possibilities to determine minimum period シ 
                    if(pow(alpha, q, p) == 1):
                        for x in range(2, int(p)):
                            calc = pow(alpha, x, p)
                            if (calc == 1 and x == q):
                                #print("*********\nP: %d\nQ: %d\nAlpha: %d\n*********" % (p, q, alpha))
                                #alphaList.append(alpha)
                                return alpha, q
    #print("# Alpha's: %d\nAlphaList Contents: %s" % (len(alphaList), alphaList))
    return 0, 0

def get_Random_Prime(min, max):
    prime = 0
    while prime == 0:
        prime = gen_Secure_Random(min, max)
        prime = is_Prime(prime)
    return prime

def gen_Secure_Random(min, max):
    #print("Min: %d\t Max: %d" % (min, max))
    systemRandom = random.SystemRandom()
    return systemRandom.randint(min, max)

def compute_Public_Key(alpha, priv_Key, p, q):
    return pow(alpha, q - priv_Key, p)

def compute_Public_Commitment(alpha, offset, p):
    return pow(alpha, offset, p)

def compute_Challenge_Response(offset, priv_Key, challenge, q):
    return offset + priv_Key * challenge % q

def compute_Identification_Verification(alpha, response, public_Key, challenge):
    return pow(alpha, response, p) * pow(public_Key, challenge, p) % p
    
'''
START OF PROGRAM:
'''

#These complexity targets will determine the programs difficultly ALL variables generated.
#Ensure a wide range as well sufficently large powers of 2.
min_P_PrimeComplexity = pow(2,25)
max_P_PrimeComplexity = pow(2,30)

#Having some fun with things
print("***********\nDetermining: (P, Q)。。0_0\nPLEASE BE PATIENT。。。\n***********")

#p = 15604671989
#Finds init prime value used as the seed for all future number generations.
p = get_Random_Prime(min_P_PrimeComplexity, max_P_PrimeComplexity)

#Generates q such that q is the largest prime divisor of p-1.
#Generates alpha such that alpha^q mod p = 1 with q being the period.
#Time enhancements have been added to code to reduce execution time.
alpha, q = gen_Alpha_Q(1, p)

#Key Pair
priv_Key = gen_Secure_Random(1, q - 1)
public_Key = compute_Public_Key(alpha, priv_Key, p, q)

#Random number to offset calullates with, helps with keeping your secret... secret シ
offset = gen_Secure_Random(1, q - 1)

#The provers Idendity Commitment to the verifier.
commitment = compute_Public_Commitment(alpha, offset, p)

#How large will the challenge to the Prover be? 
# 1 / 2^difficulty is the probability the a malicous prover will deceive the Verifier.
# ******* 2^80 has the deception probaility of 0.0000000000000000000000008271806125530276748......*********
difficulty = gen_Secure_Random(1, int(math.log(q, 2) + 1))

#Challenge to the prover to verifiy they have the key they claim.
challenge = gen_Secure_Random(1, difficulty)

#This is the response from the prover given the challenge
response = compute_Challenge_Response(offset, priv_Key, challenge, q)

#This is the verification of the response given the commitment.
verification = compute_Identification_Verification(alpha, response, public_Key, challenge)

if (commitment == compute_Identification_Verification(alpha, response, public_Key, challenge)):
    print("***********\n!!!!Verified!!!!\n\nCommitment: %d\tChallenge Response: %d\n***********" % (commitment, verification))
else:
    print("Authentication ERROR")