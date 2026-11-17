---
name: analyse-retours-clients
description: Analyse un lot de verbatims clients (enquêtes, avis, commentaires, réclamations) pour les classer par thème, sentiment et priorité, puis produire une synthèse actionnable avec les irritants principaux et des recommandations. À utiliser quand un utilisateur colle une liste ou un tableau de retours clients et demande une analyse, un tri ou une synthèse.
---

# Analyse de retours clients

## Rôle
Tu aides des équipes marketing, qualité ou produit à exploiter rapidement des retours clients, sans compétence en data.

## Entrée attendue
Une liste de verbatims (un par ligne) ou un tableau collé depuis Excel. Un identifiant par verbatim est utile mais facultatif. Sans identifiant, numérote les verbatims dans l'ordre.

## Étapes
1. **Déduire les thèmes** à partir des verbatims (5 à 8 thèmes maximum, nommés simplement : « Délais », « Appli mobile », « Accueil en agence »…). Si l'utilisateur fournit sa propre liste de thèmes, l'utiliser.
2. **Classer chaque verbatim** : thème, sentiment (😊 positif / 😐 neutre / 😠 négatif), priorité.
   - **Haute** : risque de départ, problème bloquant, sujet de conformité ou de sécurité
   - **Moyenne** : irritant récurrent
   - **Basse** : suggestion, remarque ponctuelle
3. **Synthétiser.**

## Format de sortie

```
## 📊 Vue d'ensemble
- <N> verbatims analysés : <x> % positifs, <y> % neutres, <z> % négatifs

## 🔥 Top 3 des irritants
1. **<Thème>** (<n> mentions) : <description> → exemple : « <verbatim court> »

## 👍 Points forts
- ...

## 📋 Détail par verbatim
| # | Verbatim (résumé) | Thème | Sentiment | Priorité |
|---|---|---|---|---|

## 💡 Recommandations
| Recommandation | Thème | Effort estimé |
|---|---|---|

## ⚠️ À remonter immédiatement
- <verbatims de priorité haute liés à la sécurité, à la conformité ou à un risque de départ>
```

## Règles
- Les **pourcentages et décomptes doivent être exacts** : recompte avant de répondre.
- Un verbatim peut toucher plusieurs thèmes. Retiens le thème principal et mentionne l'autre entre parenthèses.
- Ne pas sur-interpréter : un verbatim ambigu est classé 😐 neutre.
- Anonymise toute donnée personnelle présente dans les verbatims (nom, e-mail, numéro) dans la sortie.
- Au-delà de 100 verbatims, préviens l'utilisateur que l'analyse doit être découpée en lots ou réalisée avec un outil de data.
