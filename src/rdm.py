import math
from random import random


def exp(la):
    return -1 / la * math.log(random())

def discrete_uniform(n):
    return 1 + int(random() * n)

def discrete_random(dist):
    sdist = sorted(dist, key=lambda x : x[1], reverse=True) # sort by probability in descending order
    u = random()

    lower_bound = -1 # this is just to hold the condition for p1
    upper_bound = 0

    for a_i, p_i in sdist:
        upper_bound += p_i # upper_bound is sum p_i, i = 1,...,j
        if lower_bound < u <= upper_bound:
            return a_i
        lower_bound = upper_bound  # lower bound is sum p_i, i = 1,...,j-1 def rdv(values, probabilities):



def normal(mean, variance):
    u = random()
    y = exp(1)

    if u <= math.pow(math.e, (-1 * math.pow(y - 1, 2)) / 2):
        ud = discrete_uniform(2)
        if ud == 1:
            y *= -1

        return y * math.sqrt(variance) + mean

    return normal(mean, variance)

