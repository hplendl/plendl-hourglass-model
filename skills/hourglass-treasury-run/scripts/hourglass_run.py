#!/usr/bin/env python3
"""Weekly Predictive Hourglass run (lightweight wrapper around the existing 2000+ trend-line build).
  python3 hourglass_run.py --mode prep [--date YYYY-MM-DD] [--no-refresh]
  python3 hourglass_run.py --mode post [--date ...]        # SKIP if this ISO week is logged; else builds if needed, prints READY
  python3 hourglass_run.py --record URL [--date ...]       # after posting: append to the posted log
Works in $HG_OUT_DIR/<date>/ on COPIES of model.py, hist_2000.py, make_pdf.py and data/.
Never writes into the model folder. Paths: HG_MODEL_DIR, HG_OUT_DIR, HG_POSTED_LOG env vars."""
import argparse, datetime as dt, json, os, shutil, subprocess, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
HG = os.environ.get("HG_MODEL_DIR", HERE)          # folder with model.py, hist_2000.py, make_pdf.py, data/
LOG = os.environ.get("HG_POSTED_LOG", os.path.join(HERE, "hourglass_posted.tsv"))
OUT = os.environ.get("HG_OUT_DIR", os.path.join(HERE, "out"))
FINAL = ("5/5 The model runs the values: historic trend lines are measured, extended by calculation into future projected trends, "
         "and the resulting figures at each point and moment in time are reported without narrative.")
BANNED = ("crisis", "collapse", "hyperinflation", "breaks", "breach", "runaway", "educated guess", "dramatic",
          "catastroph", "doom", "explode", "skyrocket", "spiral", "death", "bankrupt", "shocking", "alarming", "unsustainable")
FD = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
REFRESH = {"dtp_latest.json": f"{FD}/v2/accounting/od/debt_to_penny?sort=-record_date&page[size]=1",
           "hist_debt_outstanding.json": f"{FD}/v2/accounting/od/debt_outstanding?filter=record_fiscal_year:gte:1999&sort=record_date&page[size]=100"}

def wk(d): y, w, _ = d.isocalendar(); return f"{y}-W{w:02d}"

def posted_this_week(d):
    if os.path.exists(LOG):
        for l in open(LOG):
            p = l.rstrip("\n").split("\t")
            if len(p) >= 3 and p[0] != "date" and wk(dt.date.fromisoformat(p[0])) == wk(d): return p[2]
    return None

def refresh(data):
    got = {}
    for f, u in REFRESH.items():
        try:
            j = json.load(urllib.request.urlopen(urllib.request.Request(u.replace("[", "%5B").replace("]", "%5D"), headers={"User-Agent": "Mozilla/5.0"}), timeout=30))
            assert j.get("data"); json.dump(j, open(f"{data}/{f}", "w")); got[f] = j["data"][-1 if "hist" in f else 0]["record_date"]
        except Exception as e: got[f] = f"FAILED, cached used: {e!r}"[:160]
    return got

def validate(posts):
    errs = []
    if len(posts) != 5: errs.append(f"expected 5 posts, got {len(posts)}")
    for i, p in enumerate(posts, 1):
        if not p.isascii(): errs.append(f"post {i} not ASCII")
        if len(p) > 280: errs.append(f"post {i} is {len(p)} chars")
        if not p.startswith(f"{i}/5 "): errs.append(f"post {i} numbering")
        for w in BANNED:
            if w in p.lower(): errs.append(f"post {i} has '{w}'")
    if posts and posts[-1] != FINAL: errs.append("final post is not the fixed sentence")
    return errs

def prep(D, do_refresh):
    w = f"{OUT}/{D.isoformat()}"; os.makedirs(w, exist_ok=True)
    if os.path.exists(f"{w}/data"): shutil.rmtree(f"{w}/data")
    shutil.copytree(f"{HG}/data", f"{w}/data")
    for f in ("model.py", "hist_2000.py", "make_pdf.py"): shutil.copy(f"{HG}/{f}", w)
    shutil.copy(f"{HERE}/build_md_template.py", f"{w}/build.py")
    vint = refresh(f"{w}/data") if do_refresh else {"refresh": "skipped"}
    r = subprocess.run([sys.executable, "build.py"], cwd=w, env={**os.environ, "HG_RUN_DATE": D.isoformat()}, capture_output=True, text=True)
    if r.returncode: print("ERROR: model build failed\n" + r.stderr[-1500:]); sys.exit(1)
    b = json.load(open(f"{w}/build_result.json")); tag = b["tag"]
    subprocess.run([sys.executable, "make_pdf.py", f"{tag}.md", f".{tag}.html", "Predictive Hourglass Model"], cwd=w, check=True)
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    pdf_ok = False
    if chrome:
        subprocess.run([chrome, "--headless", "--no-sandbox", "--no-pdf-header-footer", f"--print-to-pdf={w}/{tag}.pdf", f"file://{w}/.{tag}.html"],
                       capture_output=True, timeout=120); pdf_ok = os.path.exists(f"{w}/{tag}.pdf")
    errs = validate(b["posts"])
    md = open(f"{w}/{tag}.md").read()
    if not md.isascii(): errs.append(".md not ASCII")
    if not os.path.exists(f"{w}/{tag}_chart.png"): errs.append("chart missing")
    if not pdf_ok: errs.append("PDF not produced")
    thread = {"run_date": D.isoformat(), "week": wk(D), "chart": f"{w}/{tag}_chart.png", "chart_on_post": 3,
              "md": f"{w}/{tag}.md", "pdf": f"{w}/{tag}.pdf",
              "data_vintage": vint, "dtp_date": b["dtp_date"], "fits": b["fits"], "cases": b["cases"],
              "posts": [{"n": i, "chars": len(p), "text": p} for i, p in enumerate(b["posts"], 1)], "errors": errs}
    json.dump(thread, open(f"{w}/thread.json", "w"), indent=1)
    return w, thread

def main():
    a = argparse.ArgumentParser(); a.add_argument("--mode", choices=["prep", "post"]); a.add_argument("--date")
    a.add_argument("--no-refresh", action="store_true"); a.add_argument("--record"); a = a.parse_args()
    D = dt.date.fromisoformat(a.date) if a.date else dt.date.today()
    if a.record:
        if posted_this_week(D): print(f"SKIP: week {wk(D)} already logged"); return
        new = not os.path.exists(LOG)
        with open(LOG, "a") as f:
            if new: f.write("date\tweek\turl\n")
            f.write(f"{D.isoformat()}\t{wk(D)}\t{a.record}\n")
        print(f"RECORDED: {D} {a.record}"); return
    if a.mode == "post":
        u = posted_this_week(D)
        if u: print(f"SKIP: already posted ({wk(D)}: {u})"); return
    w = f"{OUT}/{D.isoformat()}"
    if a.mode == "post" and os.path.exists(f"{w}/thread.json") and not json.load(open(f"{w}/thread.json"))["errors"]:
        t = json.load(open(f"{w}/thread.json"))
    else:
        w, t = prep(D, not a.no_refresh)
    status = "ERROR" if t["errors"] else "READY"
    print(f"{status}: {w}/thread.json" + (f" errors={t['errors']}" if t["errors"] else ""))
    print(json.dumps({"dtp": t["dtp_date"], "vintage": t["data_vintage"], "chars": [p["chars"] for p in t["posts"]],
                      "cases": {k[:6]: v for k, v in t["cases"].items()}, "R2": {k: round(v, 3) for k, v in t["fits"].items() if k.startswith("r2")}}))
    sys.exit(1 if t["errors"] else 0)

if __name__ == "__main__": main()
