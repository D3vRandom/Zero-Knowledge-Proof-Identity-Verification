import json
import math
import random

def is_Prime(prime):
    if (prime > 0 and prime < 4):
        return prime
    if (prime % 2 == 0):
        return 0
    i = 3
    while (prime % i != 0 and i < math.ceil(math.sqrt(prime))):
        i += 2
    if (prime % i != 0):
        return prime
    return 0

def gen_Alpha_Q(min, p):
    pm1 = p - 1
    temp = pm1
    temp = temp / 2
    if (temp % 2 == 0):
        temp += 1
    for q in range(int(temp), min, -2):
        if (pm1 % q == 0):
            if (is_Prime(q) > 0):
                for alpha in range(pm1, 2, -1):
                    if(pow(alpha, q, p) == 1):
                        return alpha, q
    return 0, 0

def get_Random_Prime(min, max):
    prime = 0
    while prime == 0:
        prime = gen_Secure_Random(min, max)
        prime = is_Prime(prime)
    return prime

def gen_Secure_Random(min, max):
    systemRandom = random.SystemRandom()
    return systemRandom.randint(min, max)

def lambda_handler(event, context):
    min_P_PrimeComplexity = pow(2,24)
    max_P_PrimeComplexity = pow(2,25)
    alpha = 0
    q = 0
    while alpha == 0 or q == 0:
        p = get_Random_Prime(min_P_PrimeComplexity, max_P_PrimeComplexity)
        alpha, q = gen_Alpha_Q(1, p)
    return {
        "P":p,
        "Q":q,
        "A":alpha
    }
