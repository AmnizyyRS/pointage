import json, sys, datetime
from playwright.sync_api import sync_playwright
OUT = "tests/shots/p-"
TZ = datetime.timezone(datetime.timedelta(hours=2))
def run(tag, state, at, actions):
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, timezone_id="Europe/Zurich", locale="fr-CH")
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.route("https://transport.opendata.ch/**", lambda r: r.fulfill(status=200, content_type="application/json", body='{"connections":[]}', headers={"Access-Control-Allow-Origin": "*"}))
        pg.clock.install(time=at)
        if state is not None: pg.add_init_script("localStorage.setItem('pointage.v1', %s)" % json.dumps(json.dumps(state)))
        pg.goto("http://localhost:8765/index.html"); pg.clock.run_for(1200); pg.wait_for_timeout(200)
        for a in actions:
            if a[0] == "shot": pg.screenshot(path=OUT + tag + "-" + a[1] + ".png", full_page=a[2] if len(a) > 2 else False)
            elif a[0] == "click": pg.click(a[1]); pg.wait_for_timeout(150)
            elif a[0] == "fill": pg.fill(a[1], a[2])
            elif a[0] == "eval": print(tag, a[1], "→", pg.evaluate(a[1]))
        print(tag, "errors:", errs); b.close()

T = lambda d, h, m: datetime.datetime(2026, 10, d, h, m, tzinfo=TZ)
which = sys.argv[1]
if which == "alex":
    st = {"settings": {"name": "Alex", "sched": [0,504,504,504,504,504,0], "offered": 20, "minOut": 945}, "days": {"2026-10-21": {"punches": ["06:58","11:45","12:20","16:13"], "type": "work"}, "2026-10-22": {"punches": ["07:12"], "type": "work"}}}
    run("alex", st, T(22, 10, 0), [("shot", "today"), ("eval", "window.__b.state().settings.onboarded"), ("click", ".tab[data-tab=set]"), ("shot", "set", True), ("click", "#st-work"), ("shot", "worksheet")])
elif which == "onb":
    run("onb", None, T(22, 7, 30), [("shot", "0"), ("click", "#ob-next"), ("fill", "#ob-first", "Léa"), ("fill", "#ob-last", "Martin"), ("fill", "#ob-co", "Clinique du Lac"), ("shot", "1"), ("click", "#ob-next"),
        ("click", "[data-region=FR]"), ("shot", "2"), ("click", "#ob-next"), ("click", "[data-wtype=equipes]"), ("shot", "3"), ("click", "#ob-next"), ("shot", "4", True), ("click", "#ob-next"), ("shot", "5"), ("click", "#ob-next"), ("shot", "today"),
        ("eval", "JSON.stringify(window.__b.planFor('2026-10-22'))")])
elif which == "nuit":
    st = {"settings": {"onboarded": True, "name": "Léa", "type": "equipes", "holidays": "FR", "rotation": ["n"], "days": [False,True,True,True,True,True,False], "rotAnchor": "2026-10-19"},
          "days": {"2026-10-21": {"punches": ["21:58"], "type": "work"}}}
    run("nuit", st, T(22, 2, 30), [("eval", "window.__b.activeKey()"), ("shot", "today"), ("click", "#act-main"), ("eval", "JSON.stringify(window.__b.state().days['2026-10-21'])"), ("shot", "after")])
elif which == "fixe":
    st = {"settings": {"onboarded": True, "name": "Marc", "type": "fixe", "holidays": "GE"}, "days": {"2026-10-22": {"punches": ["08:07", "12:00", "12:45"], "type": "work"}}}
    run("fixe", st, T(22, 14, 0), [("shot", "today"), ("click", ".tab[data-tab=track]"), ("shot", "track")])
elif which == "forfait":
    days = {}
    for d in range(1, 22):
        dt = datetime.date(2026, 10, d)
        if dt.weekday() < 5: days[dt.isoformat()] = {"punches": ["08:30", "12:30", "13:30", "18:40"], "type": "work"}
    days["2026-10-22"] = {"punches": ["08:40"], "type": "work"}
    st = {"settings": {"onboarded": True, "name": "Sophie", "type": "forfait", "holidays": "FR"}, "days": days}
    run("forfait", st, T(22, 19, 30), [("shot", "today"), ("click", ".tab[data-tab=track]"), ("shot", "track"), ("click", ".tab[data-tab=abs]"), ("shot", "abs")])
if which == "motion":
    st = {"settings": {"name": "Alex", "sched": [0,504,504,504,504,504,0], "offered": 20, "minOut": 945}, "days": {"2026-10-21": {"punches": ["06:58","11:45","12:20","16:13"], "type": "work"}, "2026-10-22": {"punches": ["07:12"], "type": "work"}}}
    run("motion", st, T(22, 10, 0), [
        ("click", "#act-fix"), ("eval", "document.getElementById('scrim').hidden"), ("click", "[data-type=conge]"), ("eval", "document.querySelectorAll('.sheet').length"),
        ("click", "#ed-cancel"), ("eval", "new Promise(r=>setTimeout(()=>r(document.getElementById('scrim').hidden),400))"),
        ("click", "#act-pause"), ("eval", "document.getElementById('toast').className"), ("shot", "toast"),
        ("click", ".tab[data-tab=track]"), ("click", "[data-mode=month]"), ("eval", "new Promise(r=>setTimeout(()=>r(getComputedStyle(document.querySelector('.seg')).getPropertyValue('--k')),300))"),
        ("click", "#tr-prev"), ("shot", "track"),
        ("click", ".tab[data-tab=set]"), ("click", "[data-theme=dark]"), ("eval", "document.documentElement.dataset.theme"), ("click", "#st-redo"), ("click", "#ob-next"), ("eval", "document.querySelector('.onb-in').className")])
