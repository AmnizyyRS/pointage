from playwright.sync_api import sync_playwright
import sys
OUT = "tests/shots/chat-"
kind = sys.argv[1]; theme = sys.argv[2] if len(sys.argv) > 2 else "light"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, color_scheme=theme); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://localhost:8765/index.html")
    W = lambda sel: pg.wait_for_selector(sel, timeout=8000)
    def click(sel): W(sel); pg.click(sel); pg.wait_for_timeout(150)
    click("[data-v=go]")
    W("#c-in"); pg.fill("#c-in", "Léa"); click("#c-go")
    W("#c-skip"); pg.fill("#c-in", "Martin"); click("#c-go")
    W("#c-skip"); pg.fill("#c-in", "Clinique du Lac"); click("#c-go")
    click("[data-v=FR]")
    pg.wait_for_selector("[data-v=equipes]"); pg.screenshot(path=OUT + kind + "-type.png")
    click(f"[data-v={kind}]")
    if kind == "equipes":
        click("[data-m=n]"); pg.screenshot(path=OUT + kind + "-multi.png"); click("#c-go")
        click("[data-v='1']"); click("#c-go")
    elif kind == "variable":
        W("#c-plus"); pg.screenshot(path=OUT + kind + "-num.png"); click("[data-q='35']"); click("#c-go")
        click("#c-go"); W("input.c-time"); pg.screenshot(path=OUT + kind + "-time.png"); click("#c-go"); click("#c-skip")
    click("[data-v='45']"); click("[data-v='20']"); click("#c-go")
    W("[data-v=ok]"); pg.wait_for_timeout(300); pg.screenshot(path=OUT + kind + "-recap.png")
    # retour arrière puis on revient
    click("#cb-back"); pg.screenshot(path=OUT + kind + "-back.png"); click("#c-go")
    click("[data-v=ok]"); pg.wait_for_timeout(700)
    pg.screenshot(path=OUT + kind + "-today.png")
    print(kind, pg.evaluate("JSON.stringify({n:window.__b.state().settings.name,t:window.__b.state().settings.type,r:window.__b.state().settings.rotation,a:window.__b.state().settings.rotAnchor,p:window.__b.state().settings.pauseMin,o:window.__b.state().settings.offered,s:window.__b.state().settings.sched,ob:window.__b.state().settings.onboarded})"), "errors:", errs)
    b.close()
