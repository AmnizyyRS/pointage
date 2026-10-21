# Balancier. — mémoire du projet pour Claude Code

Balancier. est une appli de pointage **pour le salarié** (pas pour l'employeur) : un geste pour pointer, l'heure à laquelle on peut partir, le compteur d'heures sup, les absences, et le bon transport pour rentrer. Version web installable (PWA) utilisée tous les jours par son créateur, Alex, horloger à Genève (frontalier, Haute-Savoie).

- En ligne : https://amnizyyrs.github.io/pointage/ (GitHub Pages, branche `main`, dépôt public)
- Langue de l'interface : **français, tutoiement**, phrases simples, sans jargon.

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | Toute l'appli : HTML + CSS + JS dans un seul fichier, sans dépendance ni build |
| `sw.js` | Service worker : réseau d'abord **sans cache HTTP** (`cache: "no-store"`), copie locale pour le hors-ligne |
| `manifest.webmanifest` | Nom « Balancier. », couleurs, icônes |
| `apple-touch-icon.png`, `icon-192.png`, `icon-512.png`, `favicon.png`, `icon.svg` | Icône « B. » : B noir dessiné sur mesure + 3 points violets (#6B4EFF) en traînée |

## Publier une version

1. Modifier `index.html`.
2. Incrémenter `const CACHE = "balancier-vNN"` dans `sw.js`.
3. Mettre à jour `const APP_VERSION` dans `index.html` (affiché en bas de Réglages, sert à vérifier que l'iPhone a la bonne version).
4. Vérifier la syntaxe : `node -e "const h=require('fs').readFileSync('index.html','utf8');new Function(h.slice(h.indexOf('<script>')+8,h.lastIndexOf('</script>')))"`.
5. `git commit` puis `git push origin main`. Suivre le déploiement : `gh api repos/AmnizyyRS/pointage/actions/runs --jq '.workflow_runs[0]'` (workflow « pages build and deployment », ~40 s).
6. Sur l'iPhone : la nouvelle version s'installe quand l'appli passe en arrière-plan (rechargement silencieux, jamais sous les yeux). Si l'icône change, il faut réinstaller l'appli (Exporter → ajouter depuis Safari → Importer → supprimer l'ancienne).

## Données (localStorage, clé `pointage.v1`)

`state = { settings, days }`. Tout reste sur le téléphone ; sauvegarde par Exporter/Importer (JSON) dans Réglages. Toujours passer par `migrateSettings()` et `norm()` pour rester compatible avec les anciennes données.

**Journée** `days["AAAA-MM-JJ"]` : `{ punches: ["07:12","12:14",...], type: "work|conge|rtt|maladie|recup|ferie", half, remote, pause, shift }`
- Pointages en alternance entrée/sortie. `pause: true` = la dernière sortie est une pause en cours (la journée n'est pas finie).
- Heures ≥ 24:00 autorisées (`"29:05"` = 05:05 le lendemain) pour les postes de nuit ; affichage avec `clock()` (modulo 24 h), stockage avec `hhmm()`.
- `shift` : poste forcé pour ce jour (équipes), `"off"` = repos.

**Réglages** (principaux) : `type` (`variable|fixe|partiel|equipes|forfait`), `name`, `lastName`, `company`, `holidays` (`GE|FR|none`), `sched[7]` (minutes nettes par jour, index `getDay()`), `rate`, `fixed[7]` (`{s,e}`), `shifts[]` + `rotation[]` + `rotAnchor`, `days[7]`, `forfaitDays`, `pauseMin`, `offered`, `skipLunch` (`deduct|count`), `winStart`, `minOut`, `clampStart`, `maxWeek`, `vacDays`, `remoteCap`, `transit {home, work, margin}`, `accent` (`violet` par défaut), `theme`, `onboarded`.

## Règles de calcul (fonction `calc`)

- Travail brut = somme des plages entrée→sortie (jusqu'à maintenant si la journée est en cours).
- La **plus longue pause** = pause de midi, non payée, minimum `pauseMin`.
  - `skipLunch: "deduct"` : s'il manque des minutes de midi, elles sont déduites.
  - `skipLunch: "count"` (cas d'Alex) : le temps de midi non pris compte comme du travail.
- Les autres pauses sont **payées** jusqu'à `offered` minutes par jour.
- `net = brut + offertes − midi manquant` ; `solde = net − dû`.
- Dû du jour : `targetFor()` via `planFor()` selon le profil ; 0 si férié, congé, RTT, maladie (moitié si demi-journée).
- Fixe / équipes : dû = amplitude prévue − pause de midi si amplitude > 5 h 30 + pause.
- Forfait jours : pas d'heures dues ; on compte les jours, l'amplitude (13 h max) et le repos de 11 h.
- `activeKey()` : la journée « en cours » est hier si un poste de nuit est encore ouvert.
- `minOut` (sortie au plus tôt) ne s'applique qu'aux profils variable et partiel.

Profil de référence (Alex) : horaire variable, 42 h sur lun–ven (8 h 24/jour), arrivée dès 06:30, pas de sortie avant 15:45, 20 min de pauses payées, midi 30 min, `skipLunch: "count"`, fériés de Genève.

## Organisation du code (`index.html`)

- Rendu : `render()` → `renderToday()` / `renderTrack()` / `renderAbs()` / `renderSettings()` selon l'onglet.
- Aujourd'hui : compteur + courbe 30 jours, 4 actions rondes (Entrée/Sortie/Reprise, Pause/Terminer, Absence, Corriger), carte « Sortie possible », projection « Si tu sors à », trajet, totaux Travail/Pauses/Compté, activité du jour façon relevé bancaire.
- Fenêtres : `openSheet()` / `closeSheet()` (glisser vers le bas pour fermer, classes `settled`, `closing`, `dragging`). `openDay()` (corriger une journée), `openRange()` (poser une absence), `openWork()` (type d'horaires), `openProfile()`.
- Accueil : `openOnboarding()` = conversation façon messagerie, questions définies dans `steps()` selon le profil, retour en arrière par `marks[]`.
- Profil partagé accueil/réglages : `draftFrom()`, `applyDraft()`, `detailsHTML()`, `bindDetails()`, `checkDraft()`.
- Trajets : API publique `transport.opendata.ch/v1/connections` (Suisse + Léman Express), rafraîchie toutes les 3 min. Les lignes uniquement françaises peuvent manquer.
- Fériés : `holidaysOf(region, année)` (Genève, France), Pâques par l'algorithme grégorien.
- Debug : `window.__b` expose `calc`, `calcK`, `planFor`, `activeKey`, `state`, `showTab`, `openOnboarding`.

## Design

- Direction « A1 · compteur façon néobanque » : fond gris lavande clair, cartes blanches très arrondies **en relief** (`--relief`, `--relief-sm`, `--pressed`), accent **violet** (#6B4EFF), dégradé violet → rose sur les jauges, police système SF.
- Mode sombre complet (tokens redéfinis sous `:root[data-theme="dark"]`), 4 couleurs d'accent au choix.
- Mouvement court et doux (`--ease`), jamais tape-à-l'œil : onglets, fenêtres, sélecteurs qui glissent, chiffres qui défilent, barres qui poussent. « Réduire les animations » remplace tout par des fondus.
- Maquettes de référence sur le canevas Design (claude.ai, privé) : https://claude.ai/artifact/BEuWu4q5np36KLUazZp14f

## Tester

Scripts Playwright dans `tests/` (Chromium headless, iPhone 390×844, `page.clock.install` pour fixer l'heure, API transport simulée avec `page.route`). Servir le dossier avec `python3 -m http.server 8765`. Les champs `type=time` s'affichent en AM/PM dans Chromium headless : c'est normal, l'iPhone affiche 24 h.

## Pistes ouvertes

- Retour d'Alex sur les trajets réels (adresses domicile/travail) : jamais testé avec les vrais horaires.
- Idées « compagnon » à prioriser : vérification de fiche de paie, notification « pars maintenant », optimiseur de ponts, mode voiture/douane, résumé du dimanche, alertes santé.
- Appli iPhone native (SwiftUI) puis App Store en 2027, Premium (3,49 €/mois · 29,99 €/an · 69,99 € à vie), offre Entreprise dès 2028 (3 €/salarié/mois).
- Rédiger ensemble les conditions d'utilisation et la politique de confidentialité avant l'App Store.
