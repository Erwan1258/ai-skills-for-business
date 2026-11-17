"""Outils mis à disposition de l'agent de cadrage.

Chaque outil est une fonction Python simple, testable sans LLM, exposée à l'agent
via le décorateur @tool. Les écritures de fichiers sont limitées à deux dossiers
(cadrages/ et skills_proposes/) : l'agent ne peut jamais modifier les skills en production.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date
from pathlib import Path

from langchain_core.tools import tool

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
CADRAGES_DIR = ROOT / "cadrages"
PROPOSED_SKILLS_DIR = ROOT / "skills_proposes"

CRITERIA = ("volume", "gain_de_temps", "faisabilite", "faible_risque")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:60] or "sans-titre"


def parse_frontmatter(content: str) -> dict[str, str]:
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    meta: dict[str, str] = {}
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
    return meta


# ---------------------------------------------------------------- Logique métier (testable)
def list_skills_impl() -> list[dict[str, str]]:
    skills = []
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        skills.append({"name": meta.get("name", path.parent.name), "description": meta.get("description", "")})
    return skills


def read_skill_impl(name: str) -> str:
    path = SKILLS_DIR / slugify(name) / "SKILL.md"
    if not path.exists():
        available = ", ".join(s["name"] for s in list_skills_impl())
        return f"Skill « {name} » introuvable. Skills disponibles : {available}"
    return path.read_text(encoding="utf-8")


def score_impl(volume: int, gain_de_temps: int, faisabilite: int, faible_risque: int) -> dict:
    notes = dict(zip(CRITERIA, (volume, gain_de_temps, faisabilite, faible_risque)))
    for critere, note in notes.items():
        if not 1 <= int(note) <= 5:
            raise ValueError(f"La note « {critere} » doit être comprise entre 1 et 5 (reçu : {note}).")
    total = sum(int(n) for n in notes.values())
    if total >= 14:
        verdict = "Candidat prioritaire"
    elif total >= 10:
        verdict = "À approfondir"
    else:
        verdict = "À écarter ou à repenser"
    return {"notes": notes, "total": total, "sur": 20, "verdict": verdict}


def save_fiche_impl(titre: str, contenu_markdown: str) -> Path:
    CADRAGES_DIR.mkdir(exist_ok=True)
    path = CADRAGES_DIR / f"{date.today().isoformat()}-{slugify(titre)}.md"
    path.write_text(contenu_markdown.strip() + "\n", encoding="utf-8")
    return path


def draft_skill_impl(nom: str, description: str, instructions_markdown: str) -> Path:
    slug = slugify(nom)
    if (SKILLS_DIR / slug).exists():
        raise ValueError(f"Un skill « {slug} » existe déjà en production : proposez plutôt une évolution.")
    description = " ".join(description.split())  # une seule ligne dans l'en-tête
    body = instructions_markdown.strip()
    body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", body, flags=re.DOTALL)  # retire un éventuel en-tête dupliqué
    folder = PROPOSED_SKILLS_DIR / slug
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "SKILL.md"
    path.write_text(f"---\nname: {slug}\ndescription: {description}\n---\n\n{body}\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------- Outils exposés à l'agent
@tool
def lister_skills() -> str:
    """Liste les skills IA déjà disponibles (nom + description). À appeler AVANT de proposer
    un nouveau skill, pour vérifier si un skill existant répond déjà au besoin."""
    skills = list_skills_impl()
    if not skills:
        return "Aucun skill disponible."
    return "\n".join(f"- {s['name']} : {s['description']}" for s in skills)


@tool
def lire_skill(nom: str) -> str:
    """Renvoie le contenu complet d'un skill existant (SKILL.md). Utile pour vérifier en détail
    s'il couvre le besoin, ou comme modèle de format avant d'en rédiger un nouveau."""
    return read_skill_impl(nom)


@tool
def calculer_score(volume: int, gain_de_temps: int, faisabilite: int, faible_risque: int) -> str:
    """Calcule le score de priorisation d'un cas d'usage sur 20. Chaque critère est noté de 1 à 5 :
    volume (fréquence × nombre d'utilisateurs), gain_de_temps (par utilisation),
    faisabilite (tâche de texte avec règles claires = élevée), faible_risque (5 = données non
    sensibles et erreur sans conséquence, 1 = données très sensibles ou impact fort)."""
    try:
        result = score_impl(volume, gain_de_temps, faisabilite, faible_risque)
    except ValueError as err:
        return f"Erreur : {err}"
    notes = ", ".join(f"{k} = {v}/5" for k, v in result["notes"].items())
    return f"Score : {result['total']}/20 ({notes}). Verdict : {result['verdict']}."


@tool
def enregistrer_fiche_cadrage(titre: str, contenu_markdown: str) -> str:
    """Enregistre la fiche de cadrage finale (Markdown) dans le dossier cadrages/.
    À appeler une fois que toutes les sections sont renseignées et le score calculé."""
    path = save_fiche_impl(titre, contenu_markdown)
    return f"Fiche enregistrée : {path.relative_to(ROOT)}"


@tool
def proposer_nouveau_skill(nom: str, description: str, instructions_markdown: str) -> str:
    """Rédige un brouillon de nouveau skill dans skills_proposes/<nom>/SKILL.md, pour relecture
    par l'équipe IA. `nom` : identifiant court en kebab-case. `description` : une phrase disant
    ce que fait le skill ET quand l'utiliser. `instructions_markdown` : le corps du skill
    (Rôle, Entrée attendue, Format de sortie, Règles), sans en-tête ---."""
    try:
        path = draft_skill_impl(nom, description, instructions_markdown)
    except ValueError as err:
        return f"Erreur : {err}"
    return f"Brouillon de skill créé : {path.relative_to(ROOT)} (à faire relire avant mise en production)"


TOOLS = [lister_skills, lire_skill, calculer_score, enregistrer_fiche_cadrage, proposer_nouveau_skill]
