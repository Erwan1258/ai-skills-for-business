# 🧠 AI Skills for Business

> Une boîte à outils pour **déployer l'IA générative auprès de collaborateurs non-développeurs** : des skills prêts à l'emploi, les fiches besoin qui les justifient, des supports de formation et un tableau de bord pour suivre l'adoption.

Ce projet couvre tout le cycle d'adoption de l'IA dans une organisation, et pas seulement l'aspect technique :

```
 Besoin métier  ──►  Skill IA  ──►  Formation  ──►  Adoption  ──►  Retours d'expérience
  (fiche besoin)    (SKILL.md)    (tutos, atelier)   (dashboard)     (bonnes pratiques)
        ▲                                                                   │
        └───────────────────────────── amélioration continue ◄─────────────┘
```

---

## 📦 Contenu

| Dossier | Rôle | Pour qui |
|---|---|---|
| [`skills/`](skills/) | 4 skills IA métier au format `SKILL.md`, chacun avec sa **fiche besoin** et des **exemples** entrée/sortie | Utilisateurs métier, équipe IA |
| [`formation/`](formation/) | Tutoriel pas à pas pour non-développeurs, déroulé d'atelier de 45 min, FAQ | Formateurs, utilisateurs |
| [`dashboard/`](dashboard/) | Tableau de bord **Streamlit** de suivi de l'adoption (utilisateurs actifs, usage par skill, satisfaction, temps gagné) | Équipe IA, management |
| [`data/`](data/) | Jeu de données d'usage **fictif** + script de génération | — |
| [`docs/`](docs/) | Guide de bonnes pratiques, démarche de cadrage d'un cas d'usage, modèle de retour d'expérience | Communauté d'utilisateurs |

## 🛠️ Les skills

| Skill | Problème métier | Gain estimé |
|---|---|---|
| [📝 Compte rendu de réunion](skills/compte-rendu-reunion/) | Des notes brutes en vrac → un CR structuré avec décisions et actions | ~20 min / réunion |
| [✉️ Réponse à une réclamation](skills/reponse-reclamation/) | Rédiger une réponse client empathique, conforme et cohérente | ~15 min / réclamation |
| [📚 Synthèse réglementaire](skills/synthese-reglementaire/) | Résumer un texte réglementaire long en impacts concrets pour une équipe | ~1 h / document |
| [📊 Analyse de retours clients](skills/analyse-retours-clients/) | Classer des dizaines de verbatims par thème, sentiment et priorité | ~2 h / lot |

Chaque skill suit la même structure :

```
skills/<nom-du-skill>/
├── SKILL.md      # Les instructions données à l'assistant IA (le "skill" lui-même)
├── BESOIN.md     # Fiche besoin : utilisateur cible, irritant, gain, risques, indicateurs
└── exemples/     # Une entrée réelle (anonymisée) et la sortie attendue
```

> **Pourquoi le format `SKILL.md` ?** C'est un format ouvert (un fichier Markdown avec un en-tête `name` / `description`) utilisé par les assistants IA à base d'agents comme Claude. Le même contenu peut aussi être collé tel quel comme « instructions » dans un GPT personnalisé, un Copilot agent ou un assistant interne. **Le skill est indépendant de l'outil.**

## 🚀 Lancer le tableau de bord d'adoption

```bash
# 1. Créer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. (Optionnel) Régénérer les données fictives
python data/generate_usage.py

# 4. Lancer le dashboard
streamlit run dashboard/app.py
```

Le dashboard s'ouvre sur `http://localhost:8501` :

- **KPI** : utilisateurs actifs, nombre d'utilisations, satisfaction moyenne, heures gagnées
- **Courbe d'adoption** hebdomadaire
- **Usage par skill** et **par direction métier**
- **Satisfaction** par skill, pour repérer ceux qui doivent être retravaillés
- **Retours qualitatifs** des utilisateurs
- Filtres par période, direction et skill

### 📥 Alimenter le tableau de bord

| Méthode | Comment |
|---|---|
| **Données de démo** | Sélectionnées par défaut. 26 semaines d'usage fictif jusqu'à aujourd'hui |
| **Importer ses CSV** | Panneau de gauche → « Importer mes fichiers CSV ». Un modèle est téléchargeable ([`data/modele_usage.csv`](data/modele_usage.csv)). La liste des collaborateurs ciblés est facultative et sert au taux d'adoption |
| **Formulaire de feedback** | Panneau de gauche → « ➕ Donner un feedback ». Chaque réponse est enregistrée dans `data/feedback.csv` et les graphiques se mettent à jour immédiatement |

Format attendu d'un fichier d'usage :

```csv
date,user_id,direction,skill,satisfaction,minutes_gagnees,commentaire
2026-11-03,U0001,RH,compte-rendu-reunion,5,20,Gain de temps énorme sur mes CR
```

En entreprise, ces données proviennent de l'**export d'usage de l'outil IA** (console d'administration ou API d'analytics) et d'un **questionnaire de satisfaction** (Forms), fusionnés dans ce format.

## 🎓 Former les utilisateurs

- [Tutoriel : utiliser un skill en 5 minutes](formation/tutoriel-non-developpeurs.md) : aucune compétence technique requise
- [Déroulé d'un atelier de 45 minutes](formation/atelier-45min.md) : pour animer une session de prise en main
- [FAQ des nouveaux utilisateurs](formation/faq.md)

## 🧭 Méthode

1. **Identifier le besoin** avec les métiers → [`docs/cadrage-cas-usage.md`](docs/cadrage-cas-usage.md)
2. **Concevoir le skill** et le tester sur des cas réels → `skills/*/SKILL.md`
3. **Former** et accompagner → `formation/`
4. **Mesurer l'adoption** → `dashboard/`
5. **Capitaliser** les retours d'expérience → [`docs/bonnes-pratiques.md`](docs/bonnes-pratiques.md), [`docs/modele-retex.md`](docs/modele-retex.md)

## ⚠️ Données

Toutes les données de ce dépôt (usage, verbatims, exemples) sont **fictives** et générées à des fins de démonstration.

## 👤 Auteur

**Erwan Komguep Jampou**, étudiant en MSc Intelligence Artificielle (Epitech Paris), avec une formation en cybersécurité et réseaux.
[GitHub](https://github.com/Erwan1258)
