# Pong 2D

Jeu de ping-pong 2D complet en Python (stdlib uniquement), jouable à 2 joueurs
en local ou contre une IA.

## Exécution

```bash
python main.py
```

Python 3.8+ requis. **Aucune dépendance externe** à installer (tkinter fait
partie de la stdlib ; les sons sont des fichiers WAV générés à la volée).

## Contrôles

- **Joueur 1** : `Z` (ou `W`) = monter, `S` = descendre (clavier ZQSD/QWERTY)
- **Joueur 2** : Flèches `Haut` / `Bas`

## Fonctionnalités implémentées

- 2 joueurs en local (ZQSD vs Flèches) ou 1 joueur contre l'IA (3 niveaux : easy / medium / hard)
- Règles : 11 points par set, 3 sets pour gagner le match, service alterné tous les 2 points (à chaque point à 10-10)
- Gestion des lets (balle touchant le filet → service rejoué)
- Écrans : menu titre, jeu, écran de fin (Rejouer / Menu)
- Sons générés en WAV (rebond raquette, mur, point, let) et joués via le lecteur OS
- Boucle de jeu à fixed timestep 1/60s via `tk.after(16)`
- Cœur du jeu (`pong.core`) 100 % testable sans tkinter

## Fonctionnalités non implémentées

- Manette / gamepad
- Sauvegarde persistante des highscores
- Multijoueur réseau

## Limitations connues

- Le son dépend du lecteur audio par défaut de l'OS (`aplay` Linux, `afplay` macOS, `start` Windows) ; si aucun lecteur n'est disponible, le jeu reste silencieux sans erreur.
- Pas de rebinding des touches (ZQSD / flèches en dur).

## Tests

```bash
python3 -m unittest discover -s . -p "test_*.py"
```
