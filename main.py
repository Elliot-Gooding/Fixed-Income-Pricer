import numpy as np
from scipy.optimize import fsolve


#
# Given D(t), calculate the bond price.
#
times   = [1.0, 2.0, 3.0]
amounts = [4.0, 4.0, 104.0]

D = [0.96, 0.92, 0.88]
price = sum( a*d for a,d in zip(amounts, D) )

print(f"price: {price}")


#
# Given the price and payments, calculate the yield
#
def err(y, P,C,F):
    n = len(amounts)
    tot_err = -P
    for i in range(1,n+1):
        tot_err += C / (1+y)**i
    tot_err += F / (1+y)**n
    return tot_err

y_0 = 0.05
P = 99.04
C = 4
F = 100
y_sol = fsolve(err, x0=y_0, args=(P,C,F))
print(f"y: {y_sol}")