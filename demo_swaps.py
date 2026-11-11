import pandas as pd
import numpy as np

from tools import schedule, discount, divider
from swaps import calc_tau, par_rate, swap_value, annuity, swap_float_leg

#
# Model some swaps
#

today = pd.Timestamp.today().normalize()
start = today
t0 = 0

# Five-year swap
_, t1 = schedule(
    maturity = start + pd.DateOffset(months = 60), 
    freq     = 0.5, 
    start    = start,
    today = today 
    )
tau1 = calc_tau(t1, t0)
D1 = discount(t1)


# Two-year swap
_, t2 = schedule(
    maturity = start + pd.DateOffset(months = 24), 
    freq     = 0.5, 
    start    = start,
    today = today 
)
tau2 = calc_tau(t2, t0)
D2 = discount(t2)

# Notional
N = 1e6



#
# Check par_rate is fair
#


print("Calculate par rate and value the swap at this rate")

K1 = par_rate(N, t0, t1, D1)
K2 = par_rate(N, t0, t2, D2)

val1 = swap_value( K1, N, D1, t1, t0 )
val2 = swap_value( K2, N, D2, t2, t0 )

print(f"Value of five-year swap: {val1:.2f}")
print(f"Value of two-year swap:  {val2:.2f}")


divider()



#
# Sensitivity to fixed rate
#


bp = 0.0001
d_val1 = swap_value( K1 + bp, N, D1, t1, t0 ) - val1
d_val2 = swap_value( K2 + bp, N, D2, t2, t0 ) - val2

A1 = annuity(tau1, D1)
A2 = annuity(tau2, D2)


#Five-year
print("Five-year swap")
print(f"-N x A x bp               = {-N*A1*bp}")
print(f"Sensitivity for five-year = {d_val1}")

print()

#Two-year
print("Two-year swap")
print(f"-N x A x bp              =  {-N*A2*bp}")
print(f"Sensitivity for two-year =  {d_val2}")

divider()



#
#  Check floating rate pv by discounting future cash flows
#

# Five-year
pv_five_year = 0
times1 = np.concatenate(([t0], t1))
for i in range(1, len(t1)+1):
    di       = discount(times1[i])
    di_minus = discount(times1[i-1])
    F = ( di_minus / di - 1 ) / tau1[i-1]
    pvi = tau1[i-1] * F * N * di
    pv_five_year += pvi

# Two-year
pv_two_year = 0
times2 = np.concatenate(([t0], t2))
for i in range(1, len(t2)+1):
    di       = discount(times2[i])
    di_minus = discount(times2[i-1])
    F = ( di_minus / di - 1 ) / tau2[i-1]
    pvi = tau2[i-1] * F * N * di
    pv_two_year += pvi

print(f"Five-Year")
print(f"Discounted cash flow:  {pv_five_year}")
print(f"N(1 - D(t))         :  {swap_float_leg(N, 0, D1)}")

print()

print(f"Two-Year")
print(f"Discounted cash flow:  {pv_two_year}")
print(f"N(1 - D(t))         :  {swap_float_leg(N, 0, D2)}")

divider()



#
# Calculate DV01 for both swaps
#

print("Calculate DV01")
print("We fix par rate K for each swap\n")

# Offset rates
D1_up = discount(t1, offset=bp)
D2_up = discount(t2, offset=bp)

new_val1 = swap_value(K1, N, D1_up, t1, t0, offset=bp)
new_val2 = swap_value(K2, N, D2_up, t2, t0, offset=bp)

print(f"Five-year DV01: {new_val1 - val1}")
print(f"Two-year  DV01: {new_val2 - val2}")

print("\nCompare respective DV01 to N x A x bp")

print(f"Five-year: {N * A1 * bp}")
print(f"Two-year : {N * A2 * bp}")