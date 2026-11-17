# 🧠 AI Skills for Business

> Une boîte à outils pour **déployer l'IA générative auprès de collaborateurs non-développeurs** : un agent IA qui cadre les besoins métier, des skills prêts à l'emploi, des supports de formation et un tableau de bord pour suivre l'adoption.

Ce projet couvre tout le cycle d'adoption de l'IA dans une organisation, et pas seulement l'aspect technique :

```
 Besoin métier  ──►  Skill IA  ──►  Formation  ──►  Adoption  ──►  Retours d'expérience
 (agent cadrage)    (SKILL.md)    (tutos, atelier)   (dashboard)     (bonnes pratiques)
        ▲                                                                   │
        └───────────────────────────── amélioration continue ◄─────────────┘
```

---

## 🚀 Démarrage rapide

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # puis ajoutez une clé gratuite (voir plus bas)
streamlit run dashboard/app.py
```

L'application s'ouvre sur `http://localhost:8501`, avec deux pages : le **tableau de bord d'adoption** et l'**agent de cadrage**.

## 📦 Contenu

| Dossier | Rôle | Pour qui |
|---|---|---|
| [`agent/`](agent/) | **Agent de cadrage** (LangGraph) : interroge un collaborateur sur son besoin, le score, vérifie les skills existants et rédige la fiche de cadrage ou un nouveau skill | Utilisateurs métier, équipe IA |
| [`skills/`](skills/) | 4 skills IA métier au format `SKILL.md`, chacun avec sa **fiche besoin** et des **exemples** entrée/sortie | Utilisateurs métier, équipe IA |
| [`formation/`](formation/) | Tutoriel pas à pas pour non-développeurs, déroulé d'atelier de 45 min, FAQ | Formateurs, utilisateurs |
| [`dashboard/`](dashboard/) | Application **Streamlit** : tableau de bord d'adoption + page de discussion avec l'agent | Équipe IA, management |
| [`tests/`](tests/) | Tests automatisés de l'agent (outils + parcours complet avec un faux LLM) | — |
| [`data/`](data/) | Jeu de données d'usage **fictif** + script de génération | — |
| [`docs/`](docs/) | Guide de bonnes pratiques, démarche de cadrage d'un cas d'usage, modèle de retour d'expérience | Communauté d'utilisateurs |

## 🤖 L'agent de cadrage

Un collaborateur décrit une tâche pénible en langage courant. L'agent mène l'entretien comme un business analyst, puis décide.

```
        ┌──────────┐   appel d'outil ?   ┌─────────┐
START ─►│  agent   │ ──────── oui ─────► │  tools  │
        │  (LLM)   │ ◄────────────────── │         │
        └──────────┘                     └─────────┘
              │ non → réponse à l'utilisateur
              ▼
             END
```

| Outil | Rôle |
|---|---|
| `lister_skills` / `lire_skill` | Vérifie si un skill existant couvre déjà le besoin, avant d'en créer un nouveau |
| `calculer_score` | Score de priorisation sur 20 (volume, gain de temps, faisabilité, risque) |
| `enregistrer_fiche_cadrage` | Écrit la fiche de cadrage dans `cadrages/` |
| `proposer_nouveau_skill` | Rédige un brouillon de `SKILL.md` dans `skills_proposes/`, pour relecture humaine |

**Choix de conception**
- **LangGraph** : graphe explicite agent ⇄ outils, mémoire de conversation par `thread_id` et limite d'étapes contre les boucles.
- **Multi-fournisseur** : un seul client compatible OpenAI. On passe de Groq à Gemini, Mistral ou **Ollama en local** en changeant une ligne du `.env`. En local, les données ne quittent pas la machine.
- **Garde-fous** : l'agent ne peut pas modifier les skills en production. Ses propositions vont dans un dossier séparé, à valider par l'équipe IA. Il lui est aussi interdit d'inventer les réponses de l'utilisateur ou de reprendre des données clients.
- **Testable** : la logique des outils est séparée du LLM. Un faux modèle scripté permet de tester le parcours complet sans clé d'API.

### Configurer un modèle gratuit

```bash
cp .env.example .env
```

Puis, dans `.env`, choisissez **un** fournisseur :

| Fournisseur | `LLM_PROVIDER` | Clé gratuite |
|---|---|---|
| Groq (rapide) | `groq` | [console.groq.com/keys](https://console.groq.com/keys) |
| Google Gemini | `gemini` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| Mistral (hébergé en France) | `mistral` | [console.mistral.ai](https://console.mistral.ai/api-keys) |
| Ollama (100 % local) | `ollama` | Aucune : `ollama pull qwen2.5:7b` |

### Lancer l'agent

```bash
streamlit run dashboard/app.py     # page « 💬 Agent de cadrage » dans le menu de gauche
python data/generate_usage.py      # (facultatif) régénérer les données de démo
python -m agent                    # ou directement dans le terminal
pytest                             # lancer les tests
```

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

## 📈 Le tableau de bord d'adoption

Lancé avec `streamlit run dashboard/app.py` (page d'accueil, sur `http://localhost:8501`) :

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

1. **Identifier le besoin** avec les métiers → l'agent de cadrage, ou la [fiche manuelle](docs/cadrage-cas-usage.md)
2. **Concevoir le skill** et le tester sur des cas réels → `skills/*/SKILL.md`
3. **Former** et accompagner → `formation/`
4. **Mesurer l'adoption** → `dashboard/`
5. **Capitaliser** les retours d'expérience → [`docs/bonnes-pratiques.md`](docs/bonnes-pratiques.md), [`docs/modele-retex.md`](docs/modele-retex.md)

## ⚠️ Données

Toutes les données de ce dépôt (usage, verbatims, exemples) sont **fictives** et générées à des fins de démonstration.

## 👤 Auteur

**Erwan Komguep Jampou**, étudiant en MSc Intelligence Artificielle (Epitech Paris), avec une formation en cybersécurité et réseaux.
[GitHub](https://github.com/Erwan1258)
