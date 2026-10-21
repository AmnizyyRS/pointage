# Tests visuels

Scripts Playwright (Python) qui ouvrent l'appli dans un iPhone simulé (390×844), avec une heure fixée et une API de transport simulée, puis prennent des captures dans `tests/shots/`.

```bash
python3 -m http.server 8765 &      # depuis la racine du dépôt
python3 tests/shot.py inside light # scénarios : inside, pause, morning, done ; thème light ou dark
python3 tests/prof.py onb          # profils : alex, onb, nuit, fixe, forfait, motion
python3 tests/chat_test.py variable # accueil en conversation : variable ou equipes
```
