import numpy as np
from scipy.optimize import fsolve, brentq
import pandas as pd


gilts = pd.read_csv('gilts.csv')
spot_curve = pd.read_csv('spot_curve.csv')

#
# Build the cash flow schedule, with payments at tau intervals
#
def schedule(maturity, freq, start, today):
    # Collect all dates on which payments are made, working backwards from the expiry date
    dates = []
    d = maturity
    while d > start:
        dates.append(d)
        d -= pd.DateOffset(months = int(12*freq))
    dates.reverse()
    dates = pd.Series(dates)

    # Calculate relative times of payments
    t = (dates - today).dt.days.values / 365.25

    return dates, t


#
# Get gilt data
#
def gilt_data(gilt_num, verbose=False):
    gilt = gilts.loc[gilt_num]
    print(gilt)

    name, coupon, maturity = gilt["name"], gilt["coupon"], gilt["maturity"]

    # Build the cash flows

    # Get pandas start and end dates
    maturity = pd.Timestamp(maturity)
    today = pd.Timestamp.today()

    dates, t = schedule(maturity, 0.5, today, today)

    # Pay a coupon at each date
    cf = np.full((len(dates)), np.float64(coupon) / 2)
    cf[-1] += 100

    if verbose:
        # Print data
        for d_i, cf_i in zip(dates, cf):
            print(f"Date: {d_i.strftime('%Y-%m-%d'):<15} Cash flow: {cf_i} ")

    
    return {
        "name": name,
        "coupon": coupon,
        "maturity": maturity,
        "dates": dates,
        "cash_flow": cf,
        "times": t,
    }


#
# Calculate continuously compounding discount curve
#
def discount(t):
    # Get the respective spot rates
    z = np.interp(
        t,
        spot_curve["years"],
        spot_curve["spot_rate_pct"]
    ) / 100

    # Calculate discount
    D = np.exp( -z * t )

    return D


#
# Given the future cash flows and discount curve, calculate the present value
#
def pv(cf, D):
    return np.dot(cf, D)

#
# Given the cash flows and yield, calculate the present value
#
def pv_at_yield(y, times, cf):
    return np.sum(  cf / (1 + y)**times )


#
# Given the price and cash flows, calculate the yield
#
def ytm(price, times, cf):
    return brentq( lambda y: pv_at_yield(y, times, cf) - price, -0.5, 1.0)

#
# Price a specific gilt
#
def price_gilt(cf, t):
    D = discount(t)

    # Call calculation functions
    gPrice = pv(cf,D)
    gYTM = ytm(gPrice, t, cf)

    return gPrice, gYTM

gilt_num = 50
gd = gilt_data(gilt_num)
t = gd["times"]
cf = gd["cash_flow"]

P, y = price_gilt(gd["cash_flow"], gd["times"])

print(f"Dirty price: {P}")
print(f"Yield to maturity: {y*100}%")

#
# Given the cash flows and price, calculate both measurements of duration
#
def dur(times, cf, y, P):
    D_mac = np.dot(
        times * np.power((1 + y), -times) / P,
        cf
    )
    D_mod = D_mac / (1+y)

    return D_mac, D_mod

#
# Given the cash flows and price, calculate the convexity
#
def convexity(times, cf, y, P):
    C = np.dot(
        times * (times + 1) * np.power((1 + y), (- times - 2)), 
        cf
    ) / P
    return C

D_mac, D_mod  = dur(t, cf, y, P)
C = convexity(t, cf, y, P)

print(f"Duration: {D_mod}")
print(f"Convexity: {C}")

def calc_tau(t, t0):
    tau = np.diff(t, prepend=t0)
    return tau

def annuity(tau, D):
    A = np.dot(tau, D)
    return A

def swap_float_leg(N, t0, D):
    D0 = discount(t0)
    Dt = D[-1]
    pv = N*(D0 - Dt)
    return pv

def swap_fixed_leg(N,A,K):
    return N*A*K

def par_rate(N, t0, t, D):
    A = annuity(calc_tau(t, t0), D)
    fl = swap_float_leg(N, t0, D)
    K = fl / (A*N)
    return K

def swap_value(K, N, D, tau, t0, fixed_payer=True):
    A = annuity(tau, D)
    pv = ( swap_float_leg(N, t0, D) - swap_fixed_leg(N,A,K) ) * ( 1 if fixed_payer else -1 )
    return pv


