#!/usr/bin/env python
# coding: utf-8

import random
import math
import os
import struct
'''
Author: Joshua Mol
Date: March, 23, 2020
Contact: joshua_mol@hotmail.ca
Version: 1.0
'''

'''
FUNCTIONS:
'''

def is_Prime(prime):
    print("Checking if %d is prime???" % (prime))
    i = 2
    while prime % i != 0 and i < prime - 1:
        i += 1
        if i % 100000000 == 0:
            print("i == %d / %d\n%f%% Done....." % (i, prime, i/prime*100))
    if prime % i != 0:
        return prime
    print("NOPE divisable by %d" % (i))
    return 0

def get_Prime_List(max):
    list = []
    for x in range(1, max):
        check = is_Prime(x)
        if check != 0:
            list.append(check)
    return list

def get_Random_Prime(min, max):
    prime = 0
    while prime == 0:
        prime = gen_Secure_Random(min, max)
        prime = is_Prime(prime)
    return prime

def get_Prime_Divisor(min, p):
    print(p)
    p -= 1
    print(p)
    prime = 0
    while prime == 0:
        prime = gen_Secure_Random(min, p)
        if p % prime == 0:
            prime = is_Prime(prime)
        else: 
            prime = 0
    return prime

def compute_Public_Key(alpha, a, p, q):
    return pow(alpha, q - a, p)

def compute_Public_Identification(alpha, k, p):
    return pow(alpha, k, p)

def compute_Challenge_Response(k, a, r, q):
    return k + a * r % q

def compute_Identification_Verification(alpha, y, v, r):
    return pow(alpha, y, p) * pow(v, r, p) % p
    
def gen_Secure_Random(min, max):
    #print("Min: %d\t Max: %d" % (min, max))
    systemRandom = random.SystemRandom()
    return systemRandom.randint(min, max)



'''
START OF PROGRAM:
'''
min_Q_PrimeComplexity = pow(2,13)
min_P_PrimeComplexity = pow(2,20)
max_P_PrimeComplexity = pow(2,30)
print("Finding (P, Q).......")
#p = get_Random_Prime(min_P_PrimeComplexity, max_P_PrimeComplexity)
p = 88667
#q = get_Prime_Divisor(min_Q_PrimeComplexity, p)
q = 1031
# print("P: %d \t Q: %d" % (p, q))
t = 10
# alpha = gen_Secure_Random(min_Q_PrimeComplexity, p - 1)
alpha = 70322

# a = Private Key
# a = gen_Secure_Random(min_Q_PrimeComplexity, q - 1)
a = 755


# v = Public Key
v = compute_Public_Key(alpha, a, p, q)
#print(v)

# k = Random Number for offset.
k = gen_Secure_Random(pow(2, 8), q - 1)
#k = 543

gamma = compute_Public_Identification(alpha, k, p)
#print("Gamma: %d" % (gamma))

# r = random challenge *********(This Step is for BOB)**********
r = gen_Secure_Random(min_P_PrimeComplexity, max_P_PrimeComplexity)
#r = 1000


# y = Response to challenge
y = compute_Challenge_Response(k, a, r, q)
#print(y)

verification = compute_Identification_Verification(alpha, y, v, r)
if gamma == verification:
    print("Verified\nGamma: %d\tChallenge Response: %d" % (gamma, verification))
else:
    print("Authentication ERROR")


