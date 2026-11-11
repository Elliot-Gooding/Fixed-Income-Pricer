# Fixed Income Pricer

A small Python library for pricing UK government bonds (gilts) and GBP SONIA interest rate swaps off real market curves, with the standard risk measures for each.

## What it does

**Gilts**
- Builds the semi-annual coupon schedule for any conventional gilt in issue
- Prices it by discounting each cash flow off the Bank of England nominal spot curve
- Solves for the yield to maturity
- Computes duration (Macaulay & modified) and convexity

**Swaps**
- Values the fixed and floating legs of a vanilla swap off the Bank of England OIS (SONIA) curve
- Solves for the par swap rate
- Computes the PV01 (sensitivity to the fixed rate) and DV01 (sensitivity to a parallel shift in the curve)

## Data

| File | Source |
|---|---|
| `data/gilts.csv` | UK Debt Management Office: conventional gilts in issue |
| `data/spot_curve.csv` | Bank of England nominal (gilt) spot curve, 0.5–40 years |
| `data/ois_curve.csv` | Bank of England OIS (SONIA) spot curve, 0.5–25 years |

The DMO blocks scripted downloads so `data/fetch_market_data.py` rebuilds all three sourced from `XmlDataReport.xml` which is saved by hand from the [DMO website](https://www.dmo.gov.uk/data/XmlDataReport?reportCode=D1A). The BoE curves are downloaded automatically.

## Usage

```bash
pip install -r requirements.txt
python data/fetch_market_data.py   # optional: refresh market data
python demo_gilts.py               # price a gilt and compute its risk measures
python demo_swaps.py               # price swaps and check the results
```

## Method

**Discounting.** Since BoE spot rates are continuously compounded, the discount factors are $D(t) = e^{-z(t)t}$. However $z(t)$ may not necessary lie nicely on the curve, so we linearly interpolate between curve points where necessary.

**Gilts.** The price of a gilt is simply the present value of its cash flows, that is, $P = \sum_i c_i D(t_i)$. The yield is then the rate $y$ at which

$$P = \sum_i c_i \left(1 + \tfrac{y}{2}\right)^{-2t_i}$$

which can be found numerically. Then, duration and convexity are taken as derivatives of this expression with respect to $y$.

**Swaps.** With discounting and projection on the same OIS curve, the floating leg telescopes to $N\,(1 - D(T))$. The fixed leg is $N K A$, where $A = \sum_i \tau_i D(t_i)$ is the annuity, so the par rate is

$$K = \frac{1 - D(T)}{A}.$$

We check this in `demo_swaps.py` numerically by valuing the floating leg cash flow by cash flow using forward rates and confirming the result matches the closed form, and that a swap struck at $K$ has zero value.

### PV01 vs DV01

We calculate two sensitivities in the demo which look similar but differ by a small percent:

- **PV01**: move the fixed rate by 1bp, which equals exactly $N \cdot A \cdot 1\text{bp}$, because the fixed leg is linear in $K$.
- **DV01**: move the whole curve up by 1bp, which gives a slightly larger change. 

## Assumptions and limitations

- **Dirty prices only.** Accrued interest, clean prices and the gilt ex-dividend period are not modelled.
- **Simplified day counts.** Year fractions use actual/365.25. Real gilts use actual/actual, and SONIA swaps pay annually on Act/365F; these swaps pay semi-annually.
- **Extrapolation.** Beyond the end of each curve (40y gilt, 25y OIS), rates are held flat. This affects the longest gilts (2065–2073).
- **Valuation date.** The curves are a snapshot from the latest BoE release, while the demos value as of today.
- **Single-curve pricing.** One curve is used for both projection and discounting, which is standard for SONIA swaps.
- **Conventional gilts only.** Index-linked gilts are excluded.

## Possible extensions

- Key-rate (bucketed) DV01s, for hedging against specific parts of the curve
- Clean prices and accrued interest, so model prices can be compared with market quotes
- Asset-swap spreads: each gilt's yield against the OIS swap rate at the same maturity
- Index-linked gilts priced off the BoE real/inflation curves
- Unit tests for pricing identities (par swap = 0; a bond whose coupon equals its yield prices at 100)

## Structure

```
tools.py      curve interpolation, discount factors, cash flow schedules
gilts.py      gilt cash flows, pricing, yield, duration, convexity
swaps.py      annuity, swap legs, par rate, swap valuation
demo_*.py     worked examples and numerical checks
data/         market data and the script that fetches it
```