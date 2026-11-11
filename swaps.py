import numpy as np

from tools import discount

#
# Calculate the time between each payment, starting at t0
#
def calc_tau(t, t0):
    tau = np.diff(t, prepend=t0)
    return tau

#
# Calculate the annuity
#
def annuity(tau, D):
    A = np.dot(tau, D)
    return A

#
# Calculate the present value of the cash flows of the floating leg
#
def swap_float_leg(N, t0, D, offset=0):
    D0 = discount(t0, offset)
    Dt = D[-1]
    pv = N*(D0 - Dt)
    return pv

#
# Calculate the present value of the cash flows of the fixed leg
#
def swap_fixed_leg(N,A,K):
    return N*A*K

#
# Calculate the fixed rate which matches the value of the floating leg
#
def par_rate(N, t0, t, D):
    A = annuity(calc_tau(t, t0), D)
    fl = swap_float_leg(N, t0, D)
    K = fl / (A*N)
    return K

#
# Given some fixed rate, calculate the value of a swap (for either party)
#
def swap_value(K, N, D, t, t0, offset=0, fixed_payer=True):
    tau = calc_tau(t,t0)
    A = annuity(tau, D)
    pv = ( swap_float_leg(N, t0, D, offset) - swap_fixed_leg(N,A,K) ) * ( 1 if fixed_payer else -1 )
    return pv
