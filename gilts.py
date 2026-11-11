import numpy as np
from scipy.optimize import brentq
import pandas as pd

from tools import schedule, discount, divider, DATA_DIR, spot_curve

gilts = pd.read_csv(DATA_DIR / "gilts.csv")

#
# Get gilt data
#
def gilt_data(gilt_num, val_date, verbose=False):
    gilt = gilts.loc[gilt_num]

    if verbose: 
        print(gilt)
        divider()

    name, coupon, maturity = gilt["name"], gilt["coupon"], gilt["maturity"]

    # Build the cash flows

    # Get pandas start and end dates
    maturity = pd.Timestamp(maturity)

    dates, t = schedule(maturity, 0.5, val_date, val_date)

    # Pay a coupon at each date
    cf = np.full((len(dates)), np.float64(coupon) / 2)
    cf[-1] += 100

    if verbose:
        # Print data
        for d_i, cf_i in zip(dates, cf):
            print(f"Date: {d_i.strftime('%Y-%m-%d'):<15} Cash flow: {cf_i} ")
        divider()
    
    return {
        "name": name,
        "coupon": coupon,
        "maturity": maturity,
        "dates": dates,
        "cash_flow": cf,
        "times": t,
    }

#
# Given the future cash flows and discount curve, calculate the present value
#
def pv(cf, D):
    return np.dot(cf, D)

#
# Given the cash flows and semi-annually compounded yield, calculate the present value
#
def pv_at_yield(y, times, cf):
    return np.sum(  cf * (1 + y/2)**(-2*times) )


#
# Given the price and cash flows, calculate the semi-annually compounded yield
#
def ytm(price, times, cf):
    return brentq( lambda y: pv_at_yield(y, times, cf) - price, -0.5, 1.0)

#
# Price a specific gilt
#
def price_gilt(cf, t):
    D = discount(t, spot_curve)

    # Call calculation functions
    g_price = pv(cf,D)
    g_ytm = ytm(g_price, t, cf)

    return g_price, g_ytm

#
# Given the cash flows, price and semi-annually compounded yield, calculate both measurements of duration
#
def dur(times, cf, y, P):
    D_mac = np.dot(
        times * np.power((1 + y/2), -2*times) / P,
        cf
    )
    D_mod = D_mac / (1+y/2)

    return D_mac, D_mod

#
# Given the cash flows, price and semi-annually compounded yield, calculate the convexity
#
def convexity(times, cf, y, P):
    C = np.dot(
        times * (times + 0.5) * np.power((1 + y/2), (- 2*times - 2)), 
        cf
    ) / P
    return C


