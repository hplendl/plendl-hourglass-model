"""Download series from FRED (Federal Reserve Bank of St. Louis).

With FRED_API_KEY set, the official API is used; otherwise the public
keyless fredgraph CSV endpoint is used. Both return the same observations.
"""
import csv, io, os, json, time, urllib.parse
import requests

# Every series the model uses. Units are FRED's native units.
SERIES = {
    "FYFR":   ("Federal Receipts, fiscal year", "millions $", "annual FY"),
    "FYONET": ("Federal Net Outlays, fiscal year", "millions $", "annual FY"),
    "FYOINT": ("Federal Outlays: Interest, fiscal year", "millions $", "annual FY"),
    "FYGFD":  ("Gross Federal Debt, fiscal year end (reference only)", "billions $", "annual FY"),
    "GFDEBTN": ("Federal Debt: Total Public Debt (reference only)", "millions $", "quarterly"),
    "MTSR133FMS": ("Monthly Treasury Statement: Total Receipts", "millions $", "monthly"),
    "MTSO133FMS": ("Monthly Treasury Statement: Total Outlays", "millions $", "monthly"),
    "A091RC1Q027SBEA": ("Federal government current expenditures: Interest payments", "billions $ SAAR", "quarterly"),
    "FGRECPT": ("Federal government current receipts", "billions $ SAAR", "quarterly"),
    "CURRCIR": ("Currency in Circulation", "billions $", "monthly"),
}

def _get(url, tries=4):
    for i in range(tries):
        try:
            # FRED's CDN stalls some default library user agents; a plain curl-style header works.
            r = requests.get(url, headers={"User-Agent": "curl/8.5.0", "Accept": "*/*"}, timeout=60)
            r.raise_for_status()
            return r.text
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))

def fetch(series_id, api_key=None):
    """Return list of (date 'YYYY-MM-DD', float) observations, missing values dropped."""
    api_key = api_key or os.environ.get("FRED_API_KEY")
    out = []
    if api_key:
        q = urllib.parse.urlencode({"series_id": series_id, "api_key": api_key, "file_type": "json"})
        for o in json.loads(_get(f"https://api.stlouisfed.org/fred/series/observations?{q}"))["observations"]:
            if o["value"] not in (".", ""):
                out.append((o["date"], float(o["value"])))
    else:
        rows = list(csv.reader(io.StringIO(_get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"))))
        for d, v in rows[1:]:
            if v not in (".", ""):
                out.append((d, float(v)))
    return out

DTP_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny"

def fetch_debt_to_penny(since="1999-09-01"):
    """US Treasury 'Debt to the Penny' (total public debt outstanding, daily, $). Keyless public API.
    Used for fiscal-year-end debt (last record on/before 30 Sep) and the latest starting debt D0."""
    r = requests.get(DTP_URL, params={"fields": "record_date,tot_pub_debt_out_amt", "filter": f"record_date:gte:{since}",
                                      "sort": "record_date", "page[size]": 10000},
                     headers={"User-Agent": "curl/8.5.0", "Accept": "*/*"}, timeout=60)
    r.raise_for_status()
    return [(x["record_date"], float(x["tot_pub_debt_out_amt"])) for x in r.json()["data"]]

def fetch_all(api_key=None):
    raw = {s: fetch(s, api_key) for s in SERIES}
    raw["DEBT_TO_PENNY"] = fetch_debt_to_penny()
    return raw
