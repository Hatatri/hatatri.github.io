# hatatri.github.io

[![Déploiement GitHub Pages](https://github.com/Hatatri/hatatri.github.io/actions/workflows/deploy-pages.yml/badge.svg?branch=main)](https://github.com/Hatatri/hatatri.github.io/actions/workflows/deploy-pages.yml)
[![Ajouter un projet](https://github.com/Hatatri/hatatri.github.io/actions/workflows/add-repository.yml/badge.svg)](https://github.com/Hatatri/hatatri.github.io/actions/workflows/add-repository.yml)
[![Site](https://img.shields.io/website?url=https%3A%2F%2Fhatatri.github.io&label=site&up_message=en%20ligne&down_message=hors%20ligne)](https://hatatri.github.io)
[![Jekyll](https://img.shields.io/badge/Jekyll-3.10-cc0000?logo=jekyll&logoColor=white)](https://jekyllrb.com)
[![Dernier commit](https://img.shields.io/github/last-commit/Hatatri/hatatri.github.io)](https://github.com/Hatatri/hatatri.github.io/commits/main)

Site personnel de **Hicham ATATRI**, professeur agrégé d'informatique en CPGE.
*Transmettre le savoir, former les ingénieurs de demain.*

🌐 **https://hatatri.github.io** · 🗂️ [Projets](https://hatatri.github.io/projets/) · 🗓️ [Chronologie](https://hatatri.github.io/projets/chronologie/) · 📰 [Flux RSS](https://hatatri.github.io/projets/feed.xml)

---

## Sommaire

1. [Structure du dépôt](#structure-du-dépôt)
2. [Fonctionnement du workflow](#fonctionnement-du-workflow)
3. [Ajouter un projet](#ajouter-un-projet)
4. [Vérifier le site en local](#vérifier-le-site-en-local)
5. [Mise en route (une seule fois)](#mise-en-route-une-seule-fois)
6. [Dépannage](#dépannage)

---

## Structure du dépôt

```
.
├── _config.yml                    Configuration Jekyll (thème Cayman, collection projects, plugins)
├── _data/
│   ├── repositories.yml           ★ Liste des projets validés (source de vérité unique)
│   └── categories.yml             Catégories (id, libellé, emoji, description)
├── _includes/
│   ├── nav.html                   Menu de navigation
│   ├── repo-card.html             Carte d'un projet (badges, tags, date, liens)
│   └── date-fr.html               Formatage des dates en français
├── _layouts/
│   ├── default.html               Layout Cayman surchargé (français, menu, RSS, favicon)
│   └── project.html               Page détaillée d'un projet
├── _projects/                     Pages détaillées facultatives (<slug>.md)
├── projets/
│   ├── index.md                   /projets/ : statistiques, filtres, cartes
│   ├── chronologie.md             /projets/chronologie/ : timeline par mois
│   └── feed.xml                   /projets/feed.xml : flux RSS des nouveaux projets
├── assets/
│   ├── css/style.scss             Styles du thème + personnalisations
│   ├── js/projects.js             Filtres (recherche, catégorie, tags) — URL partageable
│   └── favicon.svg
├── scripts/
│   ├── validate_data.py           Validation YAML + schéma des données (utilisé par la CI)
│   ├── add_repository.py          Ajout d'un dépôt à partir de l'API GitHub
│   └── requirements.txt           Dépendances Python (PyYAML, html5validator)
├── .github/
│   ├── workflows/deploy-pages.yml Build + tests + déploiement
│   ├── workflows/add-repository.yml Ajout automatique d'un projet validé
│   ├── ISSUE_TEMPLATE/nouveau-projet.yml  Formulaire « Proposer un projet »
│   └── dependabot.yml             Mises à jour des actions, gems et paquets pip
├── index.md                       Page d'accueil (la section « Projets » lit _data/repositories.yml)
├── Gemfile / Gemfile.lock         Environnement Ruby identique à GitHub Pages + HTMLProofer
├── cv.pdf, Hicham ATATRI.png      CV et photo de profil
└── README.md                      Ce fichier (exclu du site)
```

## Fonctionnement du workflow

Fichier : [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml)

```
 push sur main ─┐
 pull request ──┼──► validate ──► build ──► test ──► deploy ──► https://hatatri.github.io
 manuel ────────┘    (YAML)      (Jekyll)  (HTML,    (main
                                            liens)    uniquement)
```

| Job | Rôle | Détails |
|---|---|---|
| **validate** | Refuse les données incorrectes **avant** le build | `scripts/validate_data.py` : syntaxe YAML de `_config.yml`, `_data/`, `.github/` et des front matter ; schéma de `repositories.yml` (champs obligatoires, slug unique, date valide et non future, catégorie connue, URL `https://`, tags…). `actionlint` vérifie les workflows. Les erreurs apparaissent en annotations sur la PR. |
| **build** | Construit le site | `actions/configure-pages@v5` + `actions/jekyll-build-pages@v1` (mêmes versions que GitHub Pages), puis `actions/upload-pages-artifact`. |
| **test** | Contrôle qualité du site **généré** | Validation HTML5/CSS par le *Nu Html Checker* (W3C) et vérification des liens internes, ancres, images, scripts, favicon et Open Graph par *HTMLProofer*. Les deux contrôles tournent même si l'un échoue. |
| **deploy** | Publie le site | `actions/deploy-pages@v4`, environnement `github-pages`, uniquement sur `main` (jamais pour une PR). |

**Bonnes pratiques mises en œuvre**

- **Permissions minimales** : lecture seule par défaut ; `pages: write` et `id-token: write` uniquement pour le job `deploy`.
- **Concurrence** : une PR mise à jour annule son run précédent ; sur `main`, les runs sont mis en file et un déploiement en cours n'est jamais interrompu (`group: pages-deploy`).
- **Un seul build** : le job `test` contrôle exactement l'artefact qui sera déployé.
- **Cache** : gems via `ruby/setup-ruby` (`bundler-cache: true`, groupe `:test` uniquement) et paquets Python via `actions/setup-python` (`cache: pip`).
- **Rapports** : chaque job écrit un résumé (onglet *Summary* du run) ; en cas d'échec les dernières lignes des logs y sont affichées et les rapports complets sont archivés (artefact `rapports-qualite`, 14 jours).
- **Logs détaillés** : lancer le workflow manuellement en cochant *verbose*, ou *Re-run jobs ▸ Enable debug logging*.
- **Dependabot** maintient les versions des actions, des gems et des paquets pip.

## Ajouter un projet

Toutes les pages (Projets, Chronologie, RSS, statistiques, section « Projets » de l'accueil) sont générées à partir de **`_data/repositories.yml`**. Ajouter un projet = ajouter une entrée dans ce fichier. Trois méthodes :

### Méthode 1 — En un clic depuis GitHub (recommandée)

1. Onglet **Actions** ▸ **Ajouter un projet** ▸ **Run workflow**.
2. Saisir le dépôt (`Hatatri/mon-depot`), la catégorie, éventuellement les tags et « Afficher sur la page d'accueil ».
3. Le workflow lit le nom, la description, le langage, le site web et les *topics* via l'API GitHub, ajoute l'entrée, la valide, commite sur `main` et lance le déploiement. Le projet est en ligne en 2 à 3 minutes.

### Méthode 2 — Proposition puis validation (formulaire)

1. Quiconque remplit le formulaire **[Proposer un projet](https://github.com/Hatatri/hatatri.github.io/issues/new?template=nouveau-projet.yml)** (lien aussi présent en bas de la page Projets).
2. Pour **valider**, le propriétaire du dépôt pose le label **`validé`** sur l'issue.
3. Le workflow ajoute le projet, déploie le site, commente et ferme l'issue. En cas d'erreur (dépôt privé, introuvable, déjà présent…), il commente l'issue avec le lien du log.

> Seul le propriétaire (`Hatatri`) peut déclencher l'ajout : un label posé par un autre compte est ignoré.

### Méthode 3 — Manuellement

Ajouter un bloc à la fin de `_data/repositories.yml` :

```yaml
- slug: jumeau-numerique-bananeraie        # unique, minuscules et tirets
  name: Jumeau numérique d'une bananeraie
  description: Modèle et capteurs pour suivre l'irrigation et la croissance des bananiers.
  category: recherche                      # id de _data/categories.yml
  repo: Hatatri/jumeau-numerique-bananeraie
  homepage: https://exemple.org            # facultatif
  language: Python                         # facultatif (alimente les statistiques)
  tags: [digital-twin, agriculture, iot]   # facultatif
  added: 2026-10-10                        # date d'ajout, AAAA-MM-JJ sans guillemets
  status: en-developpement                 # actif | en-developpement | archive
  featured: true                           # facultatif : visible sur l'accueil
```

Ou, en ligne de commande (métadonnées lues sur GitHub) :

```bash
pip install -r scripts/requirements.txt
python3 scripts/add_repository.py Hatatri/mon-depot --category enseignement --tags python,cpge --dry-run  # aperçu
python3 scripts/add_repository.py Hatatri/mon-depot --category enseignement --tags python,cpge
python3 scripts/validate_data.py
git add _data/repositories.yml && git commit -m "Ajouter le projet mon-depot" && git push
```

**Page détaillée (facultatif)** : créer `_projects/<slug>.md` avec un `title` dans le front matter et un texte libre en Markdown ; la carte du projet pointera alors vers `/projets/<slug>/`. Exemple : [`_projects/mp-psi-algorithmique.md`](_projects/mp-psi-algorithmique.md).

**Nouvelle catégorie** : l'ajouter dans `_data/categories.yml` **et** dans les listes `options` de `.github/workflows/add-repository.yml` et `.github/ISSUE_TEMPLATE/nouveau-projet.yml` (le validateur signale tout oubli).

## Vérifier le site en local

Prérequis : Ruby 3.x (`ruby -v`), Bundler, Python 3 ; Java 11+ pour la validation HTML.

```bash
# 1. Installer l'environnement identique à GitHub Pages (une fois)
bundle config set --local path vendor/bundle
bundle install

# 2. Aperçu avec rechargement automatique → http://localhost:4000
bundle exec jekyll serve --livereload

# 3. Reproduire les contrôles de la CI
pip install -r scripts/requirements.txt
python3 scripts/validate_data.py                               # données
bundle exec jekyll build                                       # build
html5validator --root _site --also-check-css                   # HTML/CSS
bundle exec htmlproofer _site --disable-external --no-enforce-https   # liens internes
```

> Sous Windows, utiliser [RubyInstaller](https://rubyinstaller.org) (avec DevKit) ou WSL.

## Mise en route (une seule fois)

1. **Settings ▸ Pages ▸ Build and deployment ▸ Source : « GitHub Actions »** (sinon l'ancien build automatique continue de publier le site sans les contrôles).
2. **Settings ▸ Actions ▸ General ▸ Workflow permissions** : laisser « Read repository contents » ; les droits nécessaires sont déclarés dans chaque workflow.
3. **Issues ▸ Labels** : créer les labels `nouveau-projet` et `validé`.
4. Fusionner la branche dans `main` : le premier déploiement démarre automatiquement (onglet **Actions**).
5. Si `main` est protégée par une règle exigeant une PR, autoriser `github-actions[bot]` à pousser, ou utiliser la méthode 3.

## Dépannage

| Symptôme | Cause probable / solution |
|---|---|
| Job **validate** rouge | Lire le résumé du run : fichier, ligne et champ fautif sont indiqués. Reproduire avec `python3 scripts/validate_data.py`. |
| Job **test** rouge, *Nu Html Checker* | HTML invalide (balise mal fermée, attribut interdit, espace dans une URL…). Le log indique fichier, ligne et colonne. |
| Job **test** rouge, *HTMLProofer* | Lien interne vers une page/ancre inexistante, image manquante, `alt` absent. Corriger le lien ou le slug. |
| Job **deploy** : « Ensure GitHub Pages has been enabled » | Étape 1 de la mise en route non effectuée. |
| Ajout automatique : « dépôt introuvable » | Dépôt privé ou faute de frappe dans `propriétaire/nom`. |
| Badges des cartes vides | Les badges sont servis par shields.io ; ils s'affichent dès que le dépôt est public. |

---

© Hicham ATATRI — tous droits réservés (texte, photo et CV).
