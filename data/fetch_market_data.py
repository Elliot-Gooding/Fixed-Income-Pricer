"""
Download real UK government bond (gilt) data and save it as two CSV files.

  gilts.csv       name, coupon (% per year), maturity date for every gilt
  spot_curve.csv  Bank of England spot rates (%) by maturity in years

pip install requests pandas openpyxl
"""
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).parent
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ---- 1. Gilts: from the UK Debt Management Office ----
# Saved by hand from https://www.dmo.gov.uk/data/XmlDataReport?reportCode=D1A
# (the site blocks scripted downloads with a CAPTCHA)
root = ET.parse(HERE / "XmlDataReport.xml").getroot()
gilts = pd.DataFrame([el.attrib for el in root.iter("View_GILTS_IN_ISSUE")])
gilts = gilts[gilts["INSTRUMENT_TYPE"].str.contains("Conventional")]  # plain fixed-coupon gilts

FRACTIONS = {"¼": .25, "½": .5, "¾": .75, "⅛": .125, "⅜": .375, "⅝": .625, "⅞": .875}

def coupon_from_name(name):
    """'4¼% Treasury Gilt 2055' -> 4.25, '4 1/8% Treasury Gilt 2029' -> 4.125"""
    m = re.match(r"\s*(\d+)?\s*(?:([¼½¾⅛⅜⅝⅞])|(\d+)/(\d+))?\s*%", name)
    frac = FRACTIONS[m.group(2)] if m.group(2) else (
        int(m.group(3)) / int(m.group(4)) if m.group(3) else 0)
    return float(m.group(1) or 0) + frac

gilts = pd.DataFrame({
    "name": gilts["INSTRUMENT_NAME"],
    "coupon": gilts["INSTRUMENT_NAME"].map(coupon_from_name),
    "maturity": pd.to_datetime(gilts["REDEMPTION_DATE"]).dt.date,
}).sort_values("maturity")
gilts.to_csv(HERE / "gilts.csv", index=False)
print(gilts.to_string(index=False))

# ---- 2. Spot curves: from the Bank of England ----
url = ("https://www.bankofengland.co.uk/-/media/boe/files/statistics/"
       "yield-curves/latest-yield-curve-data.zip")
zf = zipfile.ZipFile(io.BytesIO(requests.get(url, headers=HEADERS).content))

def boe_spot_curve(zf, file_keyword):
    """Latest spot curve (years, %) from the BoE workbook whose name contains file_keyword."""
    xlsx = next(n for n in zf.namelist() if file_keyword in n.lower())
    book = pd.ExcelFile(io.BytesIO(zf.read(xlsx)))
    sheet = next(s for s in book.sheet_names if "spot" in s.lower() and "short" not in s.lower())
    raw = book.parse(sheet, header=None)

    header_row = next(i for i in range(len(raw)) if "year" in str(raw.iat[i, 0]).lower())
    maturities = pd.to_numeric(raw.iloc[header_row, 1:], errors="coerce")
    latest = raw.dropna(subset=[1]).iloc[-1]
    curve = pd.DataFrame({"years": maturities.values,
                          "spot_rate_pct": pd.to_numeric(latest.iloc[1:], errors="coerce").values})
    return curve.dropna(), latest.iloc[0]

for keyword, filename in [("nominal", "spot_curve.csv"), ("ois", "ois_curve.csv")]:
    curve, as_of = boe_spot_curve(zf, keyword)
    curve.to_csv(HERE / filename, index=False)
    print(f"\n{keyword} spot curve for {as_of}:")
    print(curve.to_string(index=False))