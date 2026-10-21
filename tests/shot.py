import json, sys, datetime
from playwright.sync_api import sync_playwright
OUT = "tests/shots/"
days = {}
import random
random.seed(3)
base = datetime.date(2026, 9, 21)
for i in range(31):
    d = base + datetime.timedelta(days=i)
    if d.weekday() >= 5: continue
    if d.isoformat() in ("2026-10-08", "2026-10-09"):
        days[d.isoformat()] = {"punches": [], "type": "maladie"}; continue
    a = 6*60+50 + random.randint(0, 80); out = a + 504 + 30 + random.randint(-20, 30)
    f = lambda m: "%02d:%02d" % (m//60, m%60)
    days[d.isoformat()] = {"punches": [f(a), f(12*60), f(12*60+30), f(out)], "type": "work"}
days["2026-10-19"] = {"punches": ["07:00", "12:00", "12:30", "16:00"], "type": "work"}
days["2026-10-20"] = {"punches": ["08:20", "12:00", "12:30", "17:00"], "type": "work"}
days["2026-10-21"] = {"punches": ["06:58", "11:45", "12:20", "16:13"], "type": "work"}
scen = sys.argv[1] if len(sys.argv) > 1 else "inside"
today = {"inside": ["07:12", "09:45", "10:00", "12:14", "12:48"], "pause": ["07:12", "09:45", "10:00", "12:14"], "morning": [], "done": ["07:12", "12:14", "12:48", "16:05"]}[scen]
if today: days["2026-10-22"] = {"punches": today, "type": "work", "pause": scen == "pause"}
for k in ["2026-12-22", "2026-12-23", "2026-12-24", "2026-12-28", "2026-12-29", "2026-12-30"]:
    days[k] = {"punches": [], "type": "conge"}
theme = sys.argv[2] if len(sys.argv) > 2 else "light"
state = {"settings": {"name": "Alex", "theme": theme, "transit": {"home": "Bonneville", "work": "Genève, Route des Jeunes", "margin": 5}}, "days": days}
conn = {"connections": [{"from": {"departure": "2026-10-22T15:57:00+0200", "delay": 0}, "to": {"arrival": "2026-10-22T17:05:00+0200"}, "duration": "00d01:08:00", "transfers": 1,
  "sections": [{"journey": {"category": "T", "number": "15", "to": "Genève, gare Cornavin"}, "departure": {"departure": "2026-10-22T15:57:00+0200", "station": {"name": "Genève, Grand-Lancy"}, "delay": 0}, "arrival": {"arrival": "2026-10-22T16:12:00+0200", "station": {"name": "Lancy-Pont-Rouge"}}},
               {"journey": {"category": "SL", "number": "L3", "to": "Annemasse"}, "departure": {"departure": "2026-10-22T16:20:00+0200", "station": {"name": "Lancy-Pont-Rouge"}, "delay": 2, "platform": "2"}, "arrival": {"arrival": "2026-10-22T17:05:00+0200", "station": {"name": "Bonneville"}}}]}]}
hour = {"inside": 14, "pause": 13, "morning": 7, "done": 16}[scen]
minute = {"inside": 40, "pause": 20, "morning": 5, "done": 30}[scen]
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, timezone_id="Europe/Zurich", locale="fr-CH", color_scheme=theme)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
    pg.route("https://transport.opendata.ch/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(conn), headers={"Access-Control-Allow-Origin": "*"}))
    pg.clock.install(time=datetime.datetime(2026, 10, 22, hour, minute, tzinfo=datetime.timezone(datetime.timedelta(hours=2))))
    pg.add_init_script("localStorage.setItem('pointage.v1', %s)" % json.dumps(json.dumps(state)))
    pg.goto("http://localhost:8765/index.html")
    pg.clock.run_for(1500)
    pg.wait_for_timeout(300)
    tag = scen + "-" + theme
    pg.screenshot(path=OUT + tag + "-today.png", full_page=True)
    if scen == "inside":
        for t in ["track", "abs", "set"]:
            pg.click(f".tab[data-tab={t}]"); pg.wait_for_timeout(200)
            pg.screenshot(path=OUT + tag + "-" + t + ".png", full_page=True)
        pg.click(".tab[data-tab=track]"); pg.click("[data-mode=month]"); pg.wait_for_timeout(200)
        pg.screenshot(path=OUT + tag + "-month.png", full_page=True)
        pg.click(".tab[data-tab=today]"); pg.click("#act-fix"); pg.wait_for_timeout(200)
        pg.screenshot(path=OUT + tag + "-edit.png")
    print(tag, "errors:", errs)
    b.close()
