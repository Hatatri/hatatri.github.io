#!/usr/bin/env python3
"""Valide les fichiers YAML et les données du site avant le build Jekyll.

Contrôles effectués :
  1. Syntaxe YAML : _config.yml, _data/*.yml, .github/**/*.yml
  2. Syntaxe du front matter de toutes les pages (.md, .html, .xml)
  3. Schéma de _data/categories.yml et _data/repositories.yml
     (champs obligatoires, types, formats, unicité des slugs, catégories connues…)
  4. Cohérence de la collection _projects/ avec _data/repositories.yml
  5. Cohérence des catégories proposées par le workflow « Ajouter un projet »
     et par le formulaire d'issue « Proposer un projet »

Les erreurs sont affichées au format des annotations GitHub Actions
(::error file=…::message) : elles apparaissent directement dans l'onglet
« Files changed » d'une pull request et dans le résumé du workflow.

Usage : python3 scripts/validate_data.py        (code de sortie 1 si erreur)
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML est requis : pip install -r scripts/requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data"
IN_CI = os.environ.get("GITHUB_ACTIONS") == "true"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPO_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]{1,100}$")
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9+#.-]*$")
URL_RE = re.compile(r"^https://[^\s]+$")
STATUSES = {"actif", "en-developpement", "archive"}
# Slugs interdits : ils entreraient en conflit avec les pages de /projets/
RESERVED_SLUGS = {"chronologie", "feed", "index"}
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
SKIP_DIRS = {".git", "_site", "vendor", "node_modules", ".jekyll-cache", ".bundle"}

errors: list[str] = []
warnings: list[str] = []


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def error(path: Path, message: str, line: int | None = None) -> None:
    loc = f"file={rel(path)}" + (f",line={line}" if line else "")
    errors.append(f"::error {loc}::{message}" if IN_CI else f"ERREUR  {rel(path)}{':' + str(line) if line else ''} — {message}")


def warning(path: Path, message: str) -> None:
    warnings.append(f"::warning file={rel(path)}::{message}" if IN_CI else f"ATTENTION {rel(path)} — {message}")


def load_yaml(path: Path, text: str | None = None):
    """Charge un document YAML ; enregistre une erreur (avec la ligne) si invalide."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8") if text is None else text)
    except yaml.YAMLError as exc:
        line = exc.problem_mark.line + 1 if getattr(exc, "problem_mark", None) else None
        error(path, f"YAML invalide : {getattr(exc, 'problem', exc)}", line)
    except UnicodeDecodeError:
        error(path, "le fichier n'est pas encodé en UTF-8")
    return None


def iter_files(*patterns: str):
    for pattern in patterns:
        for path in sorted(ROOT.glob(pattern)):
            if path.is_file() and not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
                yield path


# --------------------------------------------------------------------------- 1
def check_yaml_files() -> None:
    for path in iter_files("_config.yml", "_data/*.yml", "_data/*.yaml", ".github/**/*.yml"):
        load_yaml(path)


# --------------------------------------------------------------------------- 2
def check_front_matter() -> dict[str, dict]:
    """Vérifie le front matter des pages et renvoie celui des documents _projects/."""
    projects: dict[str, dict] = {}
    for path in iter_files("**/*.md", "**/*.html", "**/*.xml"):
        if path.name == "README.md" or path.parts[-2:-1] == ("ISSUE_TEMPLATE",):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            if path.parent.name == "_projects":
                error(path, "front matter manquant (le fichier doit commencer par ---)")
            continue
        match = FRONT_MATTER_RE.match(text)
        if not match:
            error(path, "front matter non fermé (ligne --- manquante)", 1)
            continue
        data = load_yaml(path, match.group(1))
        if data is not None and not isinstance(data, dict):
            error(path, "le front matter doit être un dictionnaire clé: valeur", 1)
            continue
        if path.parent.name == "_projects":
            projects[path.stem] = (data or {}) | {"__path__": path}
    return projects


# --------------------------------------------------------------------------- 3
def check_categories() -> set[str]:
    path = DATA / "categories.yml"
    cats = load_yaml(path)
    if not isinstance(cats, list) or not cats:
        error(path, "doit contenir une liste non vide de catégories")
        return set()
    ids: set[str] = set()
    for i, cat in enumerate(cats, 1):
        if not isinstance(cat, dict):
            error(path, f"catégorie n°{i} : un dictionnaire est attendu")
            continue
        for key in ("id", "label"):
            if not cat.get(key):
                error(path, f"catégorie n°{i} : champ « {key} » obligatoire")
        cid = str(cat.get("id", ""))
        if cid and not SLUG_RE.match(cid):
            error(path, f"catégorie « {cid} » : l'id doit être en kebab-case (ex. mon-id)")
        if cid in ids:
            error(path, f"catégorie « {cid} » déclarée deux fois")
        ids.add(cid)
    return ids


def check_repositories(categories: set[str]) -> set[str]:
    path = DATA / "repositories.yml"
    repos = load_yaml(path)
    if repos is None:
        return set()
    if not isinstance(repos, list):
        error(path, "doit contenir une liste de projets (chaque entrée commence par « - slug: … »)")
        return set()

    slugs: set[str] = set()
    github_repos: set[str] = set()
    today = dt.date.today()
    allowed = {"slug", "name", "description", "category", "added", "repo", "url",
               "homepage", "language", "tags", "status", "featured"}

    for i, repo in enumerate(repos, 1):
        if not isinstance(repo, dict):
            error(path, f"entrée n°{i} : un dictionnaire est attendu")
            continue
        label = f"projet « {repo.get('slug', f'n°{i}')} »"

        for key in ("slug", "name", "description", "category", "added"):
            if repo.get(key) in (None, ""):
                error(path, f"{label} : champ « {key} » obligatoire")
        for key in sorted(set(repo) - allowed):
            warning(path, f"{label} : champ inconnu « {key} » (faute de frappe ?)")

        slug = repo.get("slug")
        if slug is not None:
            slug = str(slug)
            if not SLUG_RE.match(slug):
                error(path, f"{label} : slug invalide (minuscules, chiffres et tirets uniquement)")
            if slug in RESERVED_SLUGS:
                error(path, f"{label} : le slug « {slug} » est réservé")
            if slug in slugs:
                error(path, f"{label} : slug déjà utilisé par un autre projet")
            slugs.add(slug)

        for key in ("name", "description", "language"):
            if key in repo and not isinstance(repo[key], str):
                error(path, f"{label} : « {key} » doit être une chaîne de caractères")

        if repo.get("category") and repo["category"] not in categories:
            error(path, f"{label} : catégorie « {repo['category']} » inconnue "
                        f"(valeurs possibles : {', '.join(sorted(categories))})")

        added = repo.get("added")
        if added is not None:
            if not isinstance(added, dt.date) or isinstance(added, dt.datetime):
                error(path, f"{label} : « added » doit être une date AAAA-MM-JJ sans guillemets")
            elif added > today + dt.timedelta(days=1):
                error(path, f"{label} : la date d'ajout {added} est dans le futur")

        if not repo.get("repo") and not repo.get("url"):
            error(path, f"{label} : renseigner « repo » (propriétaire/nom) ou « url »")
        if repo.get("repo"):
            full = str(repo["repo"])
            if not REPO_RE.match(full):
                error(path, f"{label} : « repo » doit être au format propriétaire/nom")
            if full.lower() in github_repos:
                error(path, f"{label} : le dépôt {full} est déjà référencé")
            github_repos.add(full.lower())
        for key in ("url", "homepage"):
            if repo.get(key) and not URL_RE.match(str(repo[key])):
                error(path, f"{label} : « {key} » doit être une URL https://")

        tags = repo.get("tags", [])
        if not isinstance(tags, list):
            error(path, f"{label} : « tags » doit être une liste, ex. [python, cpge]")
        else:
            for tag in tags:
                if not isinstance(tag, str) or not TAG_RE.match(tag):
                    error(path, f"{label} : tag « {tag} » invalide (minuscules, sans espace)")
            if len(tags) != len(set(tags)):
                warning(path, f"{label} : tags en double")

        if repo.get("status", "actif") not in STATUSES:
            error(path, f"{label} : « status » doit valoir {' | '.join(sorted(STATUSES))}")
        if "featured" in repo and not isinstance(repo["featured"], bool):
            error(path, f"{label} : « featured » doit valoir true ou false")

    print(f"✔ {len(repos)} projet(s) lu(s) dans {rel(path)}")
    return slugs


# --------------------------------------------------------------------------- 4
def check_project_pages(projects: dict[str, dict], slugs: set[str]) -> None:
    for name, front in projects.items():
        path = front["__path__"]
        if name not in slugs:
            error(path, f"aucune entrée « slug: {name} » dans _data/repositories.yml pour cette page")
        if not front.get("title"):
            error(path, "champ « title » obligatoire dans le front matter")


# --------------------------------------------------------------------------- 5
def check_category_choices(categories: set[str]) -> None:
    """Les listes de catégories du workflow et du formulaire doivent suivre categories.yml."""
    workflow_path = ROOT / ".github" / "workflows" / "add-repository.yml"
    if workflow_path.exists():
        workflow = load_yaml(workflow_path) or {}
        # PyYAML (YAML 1.1) lit la clé « on » comme le booléen True
        triggers = workflow.get("on", workflow.get(True)) or {}
        options = (((triggers.get("workflow_dispatch") or {}).get("inputs") or {})
                   .get("category", {}).get("options"))
        if options is not None and set(options) != categories:
            error(workflow_path, "les options de l'entrée « category » doivent correspondre "
                                 f"aux id de _data/categories.yml ({', '.join(sorted(categories))})")

    form_path = ROOT / ".github" / "ISSUE_TEMPLATE" / "nouveau-projet.yml"
    if form_path.exists():
        form = load_yaml(form_path) or {}
        for field in form.get("body", []):
            if field.get("id") == "category":
                options = (field.get("attributes") or {}).get("options") or []
                if set(options) != categories:
                    error(form_path, "les options du champ « Catégorie » doivent correspondre "
                                     f"aux id de _data/categories.yml ({', '.join(sorted(categories))})")


def main() -> int:
    check_yaml_files()
    projects = check_front_matter()
    categories = check_categories()
    slugs = check_repositories(categories)
    check_project_pages(projects, slugs)
    check_category_choices(categories)

    for line in warnings + errors:
        print(line)
    if errors:
        print(f"\n✘ {len(errors)} erreur(s), {len(warnings)} avertissement(s).")
        return 1
    print(f"✔ Données valides ({len(warnings)} avertissement(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
