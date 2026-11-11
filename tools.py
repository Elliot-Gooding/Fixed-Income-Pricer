from pathlib import Path

import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).parent / "data"

spot_curve = pd.read_csv(DATA_DIR / "spot_curve.csv")
ois_curve  = pd.read_csv(DATA_DIR / "ois_curve.csv")

#
# Text divider
#
def divider(): print("\n" + "~"*50 + "\n")


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
# Get the respective spot rates
#
def spot_rate(t, curve, offset=0):
    z = np.interp(
        t,
        curve["years"],
        curve["spot_rate_pct"]
    ) / 100
    return z + offset


#
# Calculate continuously compounding discount curve
#
def discount(t, curve, offset=0):
    z = spot_rate(t, curve, offset)

    # Calculate discount
    D = np.exp( -z * t )

    return D