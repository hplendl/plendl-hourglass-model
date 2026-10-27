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
    "FYOINT": ("Federal Outlays: Interest (net interest), fiscal year", "millions $", "annual FY"),
    "FYGFD":  ("Gross Federal Debt, fiscal year end", "billions $", "annual FY"),
    "GFDEBTN": ("Federal Debt: Total Public Debt", "millions $", "quarterly"),
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

def fetch_all(api_key=None):
    return {s: fetch(s, api_key) for s in SERIES}
