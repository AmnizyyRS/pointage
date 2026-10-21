const CACHE = "balancier-v17";
const SHELL = ["./", "index.html", "manifest.webmanifest", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "favicon.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: "reload" }))))); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
// Réseau d'abord, sans le cache HTTP (GitHub Pages garde les pages 10 min), mais 2 s au plus : avec un réseau faible
// (tram, sous-sol), on ouvre la copie locale et la nouvelle version est quand même enregistrée pour la prochaine fois.
// Les autres sites (API des transports) ne passent pas par ici : une erreur réseau reste une erreur réseau.
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;
  const key = req.url.split("#")[0];
  const local = () => caches.match(key).then(r => r || caches.match(req)).then(r => r || caches.match("index.html"));
  const net = fetch(req.url, { cache: "no-store", credentials: "same-origin" }).then(r => {
    if (r.ok) { const copy = r.clone(); return caches.open(CACHE).then(c => c.put(key, copy)).then(() => r, () => r); }
    return r;
  });
  e.waitUntil(net.catch(() => {}));
  const slow = new Promise(res => setTimeout(res, 2000)).then(local).then(r => r || net);
  e.respondWith(Promise.race([net, slow]).catch(local));
});
