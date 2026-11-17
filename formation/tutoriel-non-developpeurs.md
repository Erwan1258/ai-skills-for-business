# 🎓 Utiliser un skill IA en 5 minutes

*Aucune compétence technique n'est nécessaire. Si vous savez copier-coller, vous savez utiliser un skill.*

---

## C'est quoi, un « skill » ?

Un skill, c'est une **fiche d'instructions** déjà rédigée pour l'assistant IA. Elle lui explique précisément comment réaliser une tâche de votre métier : quel format produire, quelles règles respecter, quelles erreurs éviter.

> 💡 **Analogie :** l'assistant IA est un stagiaire très rapide mais qui ne connaît rien à votre métier. Le skill, c'est la fiche de consignes que vous lui donnez pour qu'il fasse bien le travail du premier coup.

Sans skill, vous devez tout réexpliquer à chaque fois. Avec un skill, vous fournissez seulement **votre contenu** (vos notes, le message du client, le document…).

---

## Étape 1 : choisir le bon skill

| Je veux… | Skill à utiliser |
|---|---|
| Transformer mes notes de réunion en compte rendu | 📝 `compte-rendu-reunion` |
| Répondre à un client mécontent | ✉️ `reponse-reclamation` |
| Comprendre ce qu'un texte réglementaire change pour mon équipe | 📚 `synthese-reglementaire` |
| Analyser un lot de commentaires clients | 📊 `analyse-retours-clients` |

## Étape 2 : activer le skill dans votre assistant

Selon l'outil mis à disposition par votre entreprise :

- **Assistant avec skills intégrés** (ex. Claude) : le skill est installé par l'équipe IA. Vous n'avez rien à faire, il s'active tout seul quand vous décrivez la tâche.
- **Assistant personnalisé** (GPT personnalisé, agent Copilot, assistant interne) : ouvrez l'assistant qui porte le nom du skill.
- **Assistant classique** : ouvrez le fichier `SKILL.md`, copiez tout le texte **sous** les trois tirets `---` du début, et collez-le en premier message.

## Étape 3 : donner votre contenu

Collez simplement votre contenu, avec une phrase d'intention :

> « Voici mes notes de la réunion de ce matin, fais-moi le compte rendu : [vos notes] »

✅ **Bon réflexe :** donnez le contexte que vous seul connaissez (ce que vous pouvez proposer au client, l'équipe concernée…).
❌ **À éviter :** coller des noms de clients, des numéros de compte ou des documents confidentiels dans un outil non validé par l'entreprise.

## Étape 4 : relire, ajuster, valider

L'IA vous propose un **brouillon**. C'est vous qui restez responsable de ce qui est envoyé.

Checklist de relecture :
- [ ] Les noms, dates et chiffres sont-ils exacts ?
- [ ] Rien n'a été inventé ?
- [ ] Les champs `[À COMPLÉTER]` sont-ils remplis ?
- [ ] Le ton convient-il à votre destinataire ?

Si le résultat ne vous convient pas, **demandez une correction en langage naturel** :
> « Plus court », « plus formel », « ajoute la date limite du 15 décembre », « reformule le 2ᵉ paragraphe ».

## Étape 5 : donner votre avis 👍👎

Votre retour permet d'améliorer les skills. Après chaque utilisation, notez-la de 1 à 5 dans le formulaire de feedback de la communauté IA, et dites ce qui manquait.

---

## ❓ Et si…

| Situation | Que faire ? |
|---|---|
| Le résultat contient une information fausse | Corrigez-la et signalez-le dans le feedback : c'est précieux |
| Le skill ne correspond pas tout à fait à mon besoin | Proposez une évolution à la communauté IA |
| J'ai une idée de nouveau skill | Remplissez une [fiche de cadrage](../docs/cadrage-cas-usage.md) |
