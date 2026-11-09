import sqlite3
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

DATA = Path("/opt/ginfinity/data")
LOG = Path("/opt/ginfinity/radar.log")
app = FastAPI(title="G RADAR HUB")

def count_db(name, table=None):
    p = DATA / name
    if not p.exists():
        return 0
    try:
        con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        if table:
            n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        else:
            tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            n = con.execute(f"SELECT COUNT(*) FROM {tables[0][0]}").fetchone()[0] if tables else 0
        con.close()
        return n
    except Exception:
        return 0

def tail_log():
    if not LOG.exists():
        return "no log"
    return "\n".join(LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-6:])

@app.get("/health")
def health():
    return {"status": "online", "port": 8091}

@app.get("/", response_class=HTMLResponse)
def home():
    labs = count_db("labs.db")
    orch = count_db("orch.db")
    nodes = count_db("nodes.db")
    radar = count_db("radar_log.db")
    capital = count_db("capital_radar.db", "transactions")
    log = tail_log().replace("<", "<")
    return f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>G∞ RADAR HUB</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#031018;color:#9fe7ff;font-family:Consolas,monospace}}
.top{{display:flex;justify-content:space-between;padding:.6rem 1rem;border-bottom:1px solid #0e4a66;background:#041824}}
.grid{{display:grid;grid-template-columns:220px 1fr 240px;gap:.6rem;padding:.6rem}}
.card{{background:rgba(4,28,48,.85);border:1px solid #0e6a8a;border-radius:8px;padding:.7rem;box-shadow:0 0 18px rgba(0,180,255,.12)}}
h1{{margin:0;font-size:1.1rem;letter-spacing:.12em;color:#7fdfff}}
.big{{font-size:1.6rem;color:#e8fbff}}
.bar{{height:8px;background:#0a3044;border-radius:6px;overflow:hidden;margin:.3rem 0}}
.bar span{{display:block;height:100%;background:linear-gradient(90deg,#0aa,#3cf);width:72%}}
a{{color:#7fdfff}}
pre{{white-space:pre-wrap;font-size:.75rem;color:#8fd}}
.map{{height:280px;background:
radial-gradient(circle at 30% 40%, rgba(0,180,255,.25), transparent 40%),
radial-gradient(circle at 70% 50%, rgba(0,120,200,.2), transparent 35%),
#041820;border:1px solid #0e6a8a;border-radius:8px;position:relative}}
.dot{{position:absolute;width:6px;height:6px;background:#7fdfff;border-radius:50%;box-shadow:0 0 8px #7fdfff}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="top">
<div>GT · G∞ RADAR HUB</div>
<div>PORT 8091 · LIVE</div>
<div>NO PAYMENTS</div>
</div>
<div class="grid">
<div>
<div class="card"><div>LABS</div><div class="big">{labs}</div><div class="bar"><span></span></div></div>
<div class="card"><div>ORCH</div><div class="big">{orch}</div><div class="bar"><span style="width:55%"></span></div></div>
<div class="card"><div>NODES</div><div class="big">{nodes}</div><div class="bar"><span style="width:80%"></span></div></div>
<div class="card"><div>API CHECKS</div><div class="big">{radar}</div></div>
</div>
<div>
<div class="map">
<div class="dot" style="left:22%;top:40%"></div>
<div class="dot" style="left:48%;top:35%"></div>
<div class="dot" style="left:70%;top:48%"></div>
<div class="dot" style="left:60%;top:62%"></div>
<div style="position:absolute;bottom:8px;left:10px">GLOBAL NODE MAP · ARCHITECTURAL</div>
</div>
<div class="card" style="margin-top:.6rem">
<b>LINKS</b><br>
<a href="http://2.31.193.108:8090/">Capital Radar :8090</a><br>
API Monitor · GitHub + OpenAlex · 60s<br>
Hub · this screen
</div>
</div>
<div>
<div class="card"><div>CAPITAL REQUESTS</div><div class="big">{capital}</div><div>pending/confirmed</div></div>
<div class="card"><div>UPTIME SIGNAL</div><div class="big">OK</div><div>github · openalex</div></div>
<div class="card"><div>VOLUME</div><div class="big">LIVE</div><div class="bar"><span style="width:64%"></span></div></div>
</div>
</div>
<div class="card" style="margin:.6rem">
<div>RADAR LOG</div>
<pre>{log}</pre>
</div>
</body></html>"""
