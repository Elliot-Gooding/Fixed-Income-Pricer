import pandas as pd
from gilts import gilt_data, price_gilt, dur, convexity
from tools import divider

today = pd.Timestamp.today().normalize()

gilt_num = 50
gd = gilt_data(gilt_num, today, verbose=True)
t = gd["times"]
cf = gd["cash_flow"]

P, y = price_gilt(gd["cash_flow"], gd["times"])

print(f"Dirty price: {P}")
print(f"Yield to maturity: {y*100}%")


divider()

D_mac, D_mod  = dur(t, cf, y, P)
C = convexity(t, cf, y, P)

print(f"Duration: {D_mod}")
print(f"Convexity: {C}")
