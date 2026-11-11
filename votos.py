"""Lista os comentarios de um post do Zernio (POST_ID) em cada rede e conta votos A/B."""
import json, os, re, urllib.request, urllib.parse
API = "https://zernio.com/api/v1"; KEY = os.environ["ZERNIO_API_KEY"]
PID = os.environ.get("SO") or "6af2f3e8def51f9d167965eb"
def get(path):
    req = urllib.request.Request(API + path, headers={"Authorization": f"Bearer {KEY}"})
    try:
        with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[:300]
st, d = get("/accounts")
accs = [a for a in (d.get("accounts", []) if isinstance(d, dict) else []) if "eurekando" in f'{a.get("username","")} {a.get("displayName","")}'.lower()]
tot = {"A": 0, "B": 0}
for a in accs:
    aid = a.get("_id") or a.get("id")
    st, r = get(f"/inbox/comments/{PID}?" + urllib.parse.urlencode({"accountId": aid, "limit": 100}))
    cs = r.get("comments", []) if isinstance(r, dict) else []
    print(f"== {a.get('platform')} status {st} comentarios {len(cs)}", "" if cs else str(r)[:200])
    for c in cs:
        msg = (c.get("message") or c.get("text") or "").strip()
        m = re.match(r"^\W*([AaBb])\b", msg)
        v = m.group(1).upper() if m else ("A" if re.search(r"\babr(e|ir|a)\b", msg, re.I) else "B" if re.search(r"fechad|n[aã]o abr", msg, re.I) else "-")
        if v in tot: tot[v] += 1
        print(f"  [{v}] {msg[:140]}")
print("TOTAL", tot)
