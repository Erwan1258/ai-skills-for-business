"""Génère un jeu de données d'usage FICTIF pour le tableau de bord d'adoption.

Simule ~6 mois de déploiement de skills IA auprès de collaborateurs non-développeurs :
- adoption progressive (courbe en S) après des ateliers de formation ;
- usage différent selon les directions métier ;
- satisfaction propre à chaque skill, qui s'améliore après une nouvelle version.

Usage : python data/generate_usage.py
"""

from __future__ import annotations

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
WEEKS = 26
# Les données couvrent les 26 dernières semaines, jusqu'à la semaine en cours
_today = date.today()
START = _today - timedelta(days=_today.weekday()) - timedelta(weeks=WEEKS - 1)  # un lundi
N_USERS = 450  # population cible (tous ne deviendront pas utilisateurs)

SKILLS = {
    # nom : (popularité relative, satisfaction moyenne v1, minutes gagnées par usage, semaine de la v2)
    "compte-rendu-reunion": (1.0, 4.3, 20, None),
    "reponse-reclamation": (0.8, 3.6, 15, 12),
    "synthese-reglementaire": (0.45, 4.0, 60, None),
    "analyse-retours-clients": (0.3, 3.9, 120, None),
}

DIRECTIONS = {
    # direction : (part des utilisateurs, appétence pour l'IA, skills préférés)
    "Banque de détail": (0.35, 0.9, {"reponse-reclamation": 2.5}),
    "Conformité": (0.12, 0.8, {"synthese-reglementaire": 3.0}),
    "Marketing": (0.13, 1.3, {"analyse-retours-clients": 3.0}),
    "RH": (0.12, 1.0, {"compte-rendu-reunion": 1.5}),
    "Finance": (0.14, 0.7, {}),
    "Opérations": (0.14, 1.0, {"compte-rendu-reunion": 1.3}),
}

# Semaines où ont lieu des ateliers de formation (pics d'activation)
TRAINING_WEEKS = [1, 4, 8, 13, 18]

FEEDBACK = {
    "compte-rendu-reunion": {
        "pos": ["Gain de temps énorme sur mes CR", "Format clair, mon équipe adore", "Les actions sont enfin bien suivies"],
        "neg": ["Il manque parfois des noms de participants", "Un peu long pour des réunions courtes"],
    },
    "reponse-reclamation": {
        "pos": ["Le ton est juste, même face aux clients énervés", "Les champs À COMPLÉTER évitent les erreurs"],
        "neg": ["Trop formel au début", "Réponses trop longues", "Je dois souvent réécrire l'intro"],
    },
    "synthese-reglementaire": {
        "pos": ["Les références aux articles sont très utiles", "Enfin je comprends ce qui me concerne"],
        "neg": ["Synthèse parfois trop générale"],
    },
    "analyse-retours-clients": {
        "pos": ["2 h de travail en 5 minutes", "Les recommandations sont actionnables"],
        "neg": ["Limite de 100 verbatims contraignante", "Thèmes parfois trop larges"],
    },
}


def logistic(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def main() -> None:
    rng = random.Random(SEED)
    out_dir = Path(__file__).resolve().parent

    # --- Utilisateurs ---
    dir_names = list(DIRECTIONS)
    dir_weights = [DIRECTIONS[d][0] for d in dir_names]
    users = []
    for i in range(1, N_USERS + 1):
        direction = rng.choices(dir_names, dir_weights)[0]
        # Semaine d'activation : liée à un atelier, plus tôt pour les directions les plus appétentes
        appetence = DIRECTIONS[direction][1]
        candidates = [w for w in TRAINING_WEEKS if rng.random() < 0.35 * appetence] or [rng.choice(TRAINING_WEEKS)]
        activation = min(candidates) + rng.randint(0, 2)
        # Intensité d'usage individuelle (quelques power users, beaucoup d'usagers occasionnels)
        intensity = rng.lognormvariate(0, 0.7) * appetence
        if rng.random() < 0.3 / appetence:
            activation = None  # n'a jamais adopté les skills
        churn_week = activation + rng.randint(3, 30) if activation is not None and rng.random() < 0.25 else None
        users.append(
            {
                "user_id": f"U{i:04d}",
                "direction": direction,
                "activation_week": activation,
                "intensity": intensity,
                "churn_week": churn_week,
            }
        )

    with open(out_dir / "users.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "direction", "date_activation"])
        for u in users:
            activation = u["activation_week"]
            date_activation = START + timedelta(weeks=activation) if activation is not None else ""
            writer.writerow([u["user_id"], u["direction"], date_activation])

    # --- Événements d'usage ---
    rows = []
    for week in range(WEEKS):
        week_start = START + timedelta(weeks=week)
        maturity = logistic((week - 8) / 3)  # l'usage s'installe avec le temps
        for u in users:
            if u["activation_week"] is None or week < u["activation_week"]:
                continue
            if u["churn_week"] is not None and week >= u["churn_week"]:
                continue
            fav = DIRECTIONS[u["direction"]][2]
            weights = {s: SKILLS[s][0] * fav.get(s, 1.0) for s in SKILLS}
            lam = u["intensity"] * (0.6 + 1.6 * maturity)
            n_uses = min(_poisson(rng, lam), 12)
            for _ in range(n_uses):
                skill = rng.choices(list(weights), list(weights.values()))[0]
                _, sat_v1, minutes, v2_week = SKILLS[skill]
                sat_mean = sat_v1 + (0.6 if v2_week is not None and week >= v2_week else 0)
                rating = round(min(5, max(1, rng.gauss(sat_mean, 0.8))))
                day = min(week_start + timedelta(days=rng.randint(0, 4)), _today)
                comment = ""
                if rng.random() < 0.06:
                    pool = FEEDBACK[skill]["pos"] if rating >= 4 else FEEDBACK[skill]["neg"]
                    comment = rng.choice(pool)
                rows.append(
                    [
                        day.isoformat(),
                        u["user_id"],
                        u["direction"],
                        skill,
                        rating,
                        round(minutes * rng.uniform(0.5, 1.2)),
                        comment,
                    ]
                )

    rows.sort(key=lambda r: r[0])
    with open(out_dir / "usage.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "user_id", "direction", "skill", "satisfaction", "minutes_gagnees", "commentaire"])
        writer.writerows(rows)

    print(f"✅ {len(users)} collaborateurs et {len(rows)} utilisations générés dans {out_dir}")


def _poisson(rng: random.Random, lam: float) -> int:
    """Tirage de Poisson (algorithme de Knuth), sans dépendance à numpy."""
    if lam <= 0:
        return 0
    threshold, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= threshold:
            return k
        k += 1


if __name__ == "__main__":
    main()
