#!/usr/bin/env python3
"""Ajoute un dépôt GitHub validé dans _data/repositories.yml.

Les métadonnées (nom, description, langage, site web, topics) sont lues via
l'API GitHub ; les valeurs passées en option sont prioritaires.

Exemples :
  python3 scripts/add_repository.py Hatatri/mon-depot --category enseignement --tags python,cpge
  python3 scripts/add_repository.py Hatatri/mon-depot --category recherche --featured --dry-run
  python3 scripts/add_repository.py --from-issue corps_issue.md      # utilisé par la CI

Variable d'environnement facultative : GITHUB_TOKEN (évite la limite de 60 requêtes/h).
Si GITHUB_OUTPUT est défini (GitHub Actions), le script y écrit slug=… et name=….
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "_data" / "repositories.yml"
CATEGORIES_FILE = ROOT / "_data" / "categories.yml"
REPO_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]{1,100}$")
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9+#.-]*$")


def fail(message: str) -> None:
    print(f"::error::{message}" if os.environ.get("GITHUB_ACTIONS") else f"ERREUR — {message}")
    sys.exit(1)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_issue_form(body: str) -> dict[str, str]:
    """Extrait les champs d'une issue créée avec .github/ISSUE_TEMPLATE/nouveau-projet.yml.

    Le formulaire est rendu en Markdown sous la forme « ### Libellé\\n\\nvaleur ».
    """
    fields: dict[str, str] = {}
    for block in re.split(r"^###\s+", body, flags=re.MULTILINE)[1:]:
        title, _, value = block.partition("\n")
        value = value.strip()
        fields[title.strip().lower()] = "" if value == "_No response_" else value
    mapping = {
        "dépôt github": "repo",
        "catégorie": "category",
        "tags": "tags",
        "nom affiché": "name",
        "description": "description",
    }
    result = {mapping[k]: v for k, v in fields.items() if k in mapping}
    # « Projet phare » est une case à cocher : « - [X] Afficher ce projet… »
    result["featured"] = "true" if re.search(r"- \[[xX]\]", fields.get("projet phare", "")) else ""
    return result


def github_api(full_name: str) -> dict:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{full_name}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "hatatri-site"},
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            fail(f"le dépôt {full_name} est introuvable (ou privé)")
        fail(f"API GitHub : HTTP {exc.code} {exc.reason}")
    except urllib.error.URLError as exc:
        fail(f"API GitHub injoignable : {exc.reason}")
    return {}


def build_entry(args: argparse.Namespace, existing: list[dict]) -> dict:
    full_name = args.repo.strip().removeprefix("https://github.com/").strip("/")
    if not REPO_RE.match(full_name):
        fail(f"« {args.repo} » n'est pas au format propriétaire/nom")

    if any(str(r.get("repo", "")).lower() == full_name.lower() for r in existing):
        fail(f"le dépôt {full_name} figure déjà dans {DATA_FILE.name}")

    categories = {c["id"] for c in yaml.safe_load(CATEGORIES_FILE.read_text(encoding="utf-8"))}
    if args.category not in categories:
        fail(f"catégorie « {args.category} » inconnue (choix : {', '.join(sorted(categories))})")

    meta = github_api(full_name)
    if meta.get("private"):
        fail(f"le dépôt {full_name} est privé : il ne peut pas être publié sur le site")
    if meta.get("archived"):
        print(f"⚠ le dépôt {full_name} est archivé : statut « archive » appliqué")

    full_name = meta.get("full_name", full_name)  # casse officielle
    name = " ".join((args.name or meta.get("name") or full_name.split("/")[1]).split())
    description = " ".join((args.description or meta.get("description") or "").split())
    if not description:
        fail("aucune description : en ajouter une sur GitHub ou utiliser --description")

    tags = [t.strip().lower() for t in (args.tags or "").replace(";", ",").split(",") if t.strip()]
    if not tags:
        tags = list(meta.get("topics") or [])[:8]
    bad = [t for t in tags if not TAG_RE.match(t)]
    if bad:
        fail(f"tags invalides : {', '.join(bad)} (minuscules, sans espace)")

    slug = args.slug or slugify(full_name.split("/")[1])
    taken = {str(r.get("slug")) for r in existing}
    base, n = slug, 2
    while slug in taken:
        slug, n = f"{base}-{n}", n + 1

    entry: dict = {
        "slug": slug,
        "name": name,
        "description": description,
        "category": args.category,
        "repo": full_name,
    }
    homepage = (meta.get("homepage") or "").strip()
    if homepage.startswith("https://"):
        entry["homepage"] = homepage
    if meta.get("language"):
        entry["language"] = meta["language"]
    if tags:
        entry["tags"] = tags
    entry["added"] = dt.date.today()
    entry["status"] = "archive" if meta.get("archived") else "actif"
    if args.featured:
        entry["featured"] = True
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repo", nargs="?", help="dépôt GitHub au format propriétaire/nom")
    parser.add_argument("--from-issue", metavar="FICHIER", help="lire les champs depuis le corps d'une issue « Nouveau projet »")
    parser.add_argument("--category", help="id de catégorie (_data/categories.yml)")
    parser.add_argument("--tags", help="tags séparés par des virgules (défaut : topics GitHub)")
    parser.add_argument("--name", help="nom affiché (défaut : nom du dépôt)")
    parser.add_argument("--description", help="description (défaut : description GitHub)")
    parser.add_argument("--slug", help="identifiant (défaut : nom du dépôt en kebab-case)")
    parser.add_argument("--featured", action="store_true", help="afficher le projet sur la page d'accueil")
    parser.add_argument("--dry-run", action="store_true", help="afficher l'entrée sans modifier le fichier")
    args = parser.parse_args()

    if args.from_issue:
        fields = parse_issue_form(Path(args.from_issue).read_text(encoding="utf-8"))
        args.repo = args.repo or fields.get("repo")
        args.category = args.category or fields.get("category")
        args.tags = args.tags or fields.get("tags")
        args.name = args.name or fields.get("name")
        args.description = args.description or fields.get("description")
        args.featured = args.featured or fields.get("featured") == "true"
    if not args.repo or not args.category:
        parser.error("le dépôt et --category sont obligatoires")

    existing = yaml.safe_load(DATA_FILE.read_text(encoding="utf-8")) or []
    entry = build_entry(args, existing)
    block = yaml.safe_dump([entry], allow_unicode=True, sort_keys=False, default_flow_style=None, width=1000)

    if args.dry_run:
        print(block)
        return

    # Ajout en fin de fichier : préserve les commentaires et la mise en forme existants.
    content = DATA_FILE.read_text(encoding="utf-8").rstrip("\n")
    DATA_FILE.write_text(f"{content}\n\n{block}", encoding="utf-8")
    print(f"✔ « {entry['name']} » ajouté à {DATA_FILE.relative_to(ROOT)} :\n\n{block}")

    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
            name = " ".join(str(entry["name"]).split())
            out.write(f"slug={entry['slug']}\nname={name}\nrepo={entry['repo']}\n")


if __name__ == "__main__":
    main()
