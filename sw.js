const CACHE = "balancier-v13";
const SHELL = ["./", "index.html", "manifest.webmanifest", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "favicon.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: "reload" }))))); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
// Réseau d'abord, sans le cache HTTP (GitHub Pages garde les pages 10 min), puis copie locale pour le hors-ligne
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const same = new URL(req.url).origin === self.location.origin;
  const net = same ? fetch(req.url, { cache: "no-store", credentials: "same-origin" }) : fetch(req);
  e.respondWith(net.then(r => {
    if (same && r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req.url.split("#")[0], copy)); }
    return r;
  }).catch(() => caches.match(req.url.split("#")[0]).then(r => r || caches.match(req)).then(r => r || caches.match("index.html"))));
});
