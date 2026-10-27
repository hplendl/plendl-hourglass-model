import sys, markdown
src, html_out = sys.argv[1], sys.argv[2]
title = sys.argv[3] if len(sys.argv) > 3 else "Predictive Hourglass Model"
md=open(src,encoding="utf-8").read()
md=md.replace("\\(I_t = D_t \\times r_t\\)","<i>I<sub>t</sub> = D<sub>t</sub> × r<sub>t</sub></i>")
body=markdown.markdown(md,extensions=["tables"])
css="""body{font-family:'DejaVu Sans',Arial,sans-serif;font-size:10.5pt;line-height:1.4;margin:0;color:#111}
h1{font-size:18pt;color:#1f2a44}h2{font-size:13.5pt;color:#1f2a44;border-bottom:1px solid #1f2a44;padding-bottom:2px;margin-top:18px}
h3{font-size:11.5pt;color:#1f2a44}table{border-collapse:collapse;width:100%;margin:8px 0;font-size:8.6pt}
tr{page-break-inside:avoid}th{background:#1f2a44;color:#fff;text-align:left;padding:3px 5px}td{border-bottom:1px solid #ddd;padding:3px 5px;vertical-align:top}
tr:nth-child(even) td{background:#f4f6f9}a{color:#1f4fa0}img{max-width:100%}em{color:#444}@page{size:Letter;margin:0.6in}"""
open(html_out,"w",encoding="utf-8").write(f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{css}</style></head><body>{body}</body></html>")
