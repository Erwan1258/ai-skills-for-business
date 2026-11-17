# ✅ Bonnes pratiques de l'IA générative au travail

*Guide vivant, enrichi par les retours d'expérience de la communauté.*

## Pour les utilisateurs

### Bien formuler sa demande
| ❌ Demande vague | ✅ Demande efficace |
|---|---|
| « Fais un mail » | « Rédige une réponse à ce client mécontent. Je peux lui proposer un remboursement de 7,50 € sous 5 jours. Ton : empathique, 150 mots maximum. » |
| « Résume ce document » | « Résume ce document en 5 points pour une équipe de conseillers en agence. Qu'est-ce qui change pour eux ? » |

La recette : **rôle + tâche + contexte + format + contraintes**.

### Les réflexes de sécurité
- 🔒 Utiliser uniquement les outils validés par l'entreprise.
- 🔒 Anonymiser : remplacer les noms par « Client A », supprimer les numéros.
- 👀 Relire systématiquement avant tout envoi à l'extérieur.
- 🧾 Vérifier les chiffres, dates et références à la source.

### Quand ne PAS utiliser l'IA
- Pour une décision qui engage juridiquement l'entreprise sans validation humaine.
- Pour des calculs critiques sans vérification.
- Quand la tâche prend moins de temps à faire soi-même qu'à expliquer.

## Pour les concepteurs de skills

1. **Partir d'un vrai besoin**, cadré avec les utilisateurs ([fiche de cadrage](cadrage-cas-usage.md)).
2. **Un skill = une tâche.** Un skill qui fait tout ne fait rien de bien.
3. **Une description précise** dans l'en-tête : c'est elle qui permet à l'assistant de savoir quand activer le skill.
4. **Imposer un format de sortie** : les utilisateurs s'y retrouvent, et la qualité est plus facile à évaluer.
5. **Écrire les garde-fous noir sur blanc** : « ne jamais inventer », `[À COMPLÉTER]`, alertes d'escalade.
6. **Tester sur au moins 5 cas réels** (anonymisés) avant de diffuser, dont un cas difficile.
7. **Fournir un exemple entrée → sortie** : c'est le meilleur support de formation.
8. **Mesurer puis itérer** : la satisfaction par skill du [dashboard](../dashboard/) indique quoi améliorer en priorité.

## Retours d'expérience capitalisés

| Constat | Ce qu'on a changé |
|---|---|
| Les CR générés contenaient parfois des décisions qui n'en étaient pas | Ajout d'une section « Points ouverts » séparée des « Décisions » |
| Les conseillers recopiaient des promesses non autorisées | Introduction des champs `[À COMPLÉTER]` dans le skill réclamation |
| Les synthèses réglementaires étaient prises pour des avis officiels | Avertissement systématique en fin de synthèse |
| Les pourcentages des analyses de verbatims étaient parfois faux | Règle de recomptage et limite à 100 verbatims par lot |

*Exemples illustratifs : ajoutez les vôtres avec le [modèle de RETEX](modele-retex.md).*
