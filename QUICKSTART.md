# Wesh Serkam — Vinted MCP, mode d'emploi rapide

OK donc en gros c'est un truc qui te branche **Claude** (l'IA d'Anthropic) directement sur ton compte Vinted. Une fois installé, tu pourras dire à Claude des choses comme :

- *"Liste mes 10 dernières conversations Vinted"*
- *"Réponds à la conversation 12345 : 'oui c'est toujours dispo'"*
- *"Baisse le prix de mon article 99887766 à 12€"*
- *"Donne-moi mes stats du mois"*

Et il fera. Pour de vrai.

> 🚨 **Avant tout — lis ça.** Vinted n'a pas d'API officielle pour la vente perso. Ce truc fait semblant d'être ton navigateur. Tant que tu l'utilises gentiment (rythme humain, pas 1000 actions/heure), c'est OK. Si tu spammes, **risque de ban de ton compte Vinted**. Tu es prévenu. Si tu vends en gros volume, regarde plutôt **Vinted Pro** ([pro-portal.svc.vinted.com](https://pro-portal.svc.vinted.com/)) qui est une API officielle gratuite, zéro risque.

---

## 1. Installe Python

Va sur https://www.python.org/downloads/windows/, prends la dernière version.

🔴 **TRÈS IMPORTANT à l'installation** : coche la case **"Add python.exe to PATH"** sinon rien ne marchera après.

Pour vérifier que c'est OK, ouvre **PowerShell** (touche Windows → tape "powershell" → Entrée) et tape :

```powershell
py --version
```

Si ça affiche un truc genre `Python 3.12.x`, t'es bon.

---

## 2. Récup le projet

Dans PowerShell :

```powershell
cd $env:USERPROFILE\Documents
git clone https://github.com/TON_USERNAME/vinted-mcp.git
cd vinted-mcp
py -m pip install -e .
```

*(Remplace `TON_USERNAME` par le pseudo GitHub de la personne qui t'a partagé le repo.)*

Si t'as pas `git` : télécharge l'installeur ici → https://git-scm.com/download/win, install avec les options par défaut, redémarre PowerShell.

---

## 3. Récup tes cookies Vinted (le bout chiant mais ça prend 2 min)

Vinted te connecte via des cookies dans ton navigateur. On va les copier-coller dans ta config.

1. Ouvre **Chrome** (ou **Edge**) et va sur **vinted.fr**. Connecte-toi si tu l'es pas.
2. Appuie sur **F12** (ça ouvre les outils dev).
3. Tout en haut des outils dev, clique sur l'onglet **Application** (sur Edge c'est **Storage**).
4. Dans la barre de gauche, déplie **Cookies** puis clique sur **https://www.vinted.fr**.
5. Tu vois une liste. Note quelque part (Notepad fait l'affaire) la **Value** des cookies suivants :
   - `_vinted_fr_session` (le plus important, c'est un gros blob)
   - `access_token_web` (si présent)
   - `anon_id` (si présent)
6. Pendant que t'y es, dans la barre d'adresse du navigateur, tape `chrome://version` et copie la ligne **User Agent** — note-la aussi.

⚠️ **Ces cookies = la clé de ton compte Vinted.** Ne les partage avec personne, ne les colle pas dans un Discord public.

---

## 4. Branche Claude Desktop sur le serveur

Télécharge Claude Desktop si t'as pas → https://claude.ai/download

Une fois installé :

1. Ouvre l'**Explorateur Windows**, dans la barre d'adresse tape `%APPDATA%\Claude` et Entrée.
2. Tu vois un fichier `claude_desktop_config.json`. Ouvre-le avec **Notepad** (clic droit → Ouvrir avec → Notepad).
3. Remplace son contenu par ça (en collant TES valeurs aux endroits indiqués) :

```json
{
  "mcpServers": {
    "vinted": {
      "command": "py",
      "args": ["-m", "vinted_mcp.server"],
      "env": {
        "VINTED_DOMAIN": "vinted.fr",
        "VINTED_SESSION_COOKIE": "COLLE_ICI_LA_VALEUR_DE_vinted_fr_session",
        "VINTED_ACCESS_TOKEN_WEB": "COLLE_ICI_LA_VALEUR_DE_access_token_web",
        "VINTED_ANON_ID": "COLLE_ICI_LA_VALEUR_DE_anon_id",
        "VINTED_USER_AGENT": "COLLE_ICI_TON_USER_AGENT"
      }
    }
  }
}
```

4. Enregistre (Ctrl+S) et ferme.
5. **Ferme Claude Desktop complètement** (clic droit sur l'icône en bas à droite → Quit) puis relance-le.

---

## 5. Premier test

Dans Claude Desktop, écris simplement :

> *"Avec Vinted, dis-moi qui je suis"*

S'il te renvoie ton profil (pseudo, photo, etc.), **t'es opérationnel** 🎉. S'il te dit que les cookies sont morts, c'est qu'ils ont expiré → retour à l'étape 3, recopie-les.

---

## 6. Comment t'en servir au quotidien

Quelques exemples de trucs que tu peux demander à Claude :

**Pour la messagerie :**
- *"Liste mes 10 dernières conversations Vinted, classe par non-répondues"*
- *"Lis-moi la conversation 12345"*
- *"Réponds à la 12345 : oui c'est dispo, j'envoie demain"*
- *"Pour les 5 messages où l'acheteur demande si c'est encore dispo, réponds oui dans toutes"*

**Pour le stock :**
- *"Liste mes articles actifs"*
- *"Mes articles vendus ce mois-ci"*
- *"Mes stats Vinted"*
- *"Baisse de 2€ le prix de l'article 99887766"*
- *"Ferme l'annonce 12345 (je veux la retirer temporairement)"*

**Mode auto-réponse questions standards :**
- *"Toutes les 30 min, regarde mes nouveaux messages. Si quelqu'un demande 'toujours dispo ?' réponds-lui avec le template `still_available_yes`. Pour le reste, fais-moi un récap."*

Claude saura quels outils utiliser. C'est lui qui gère.

---

## Personnaliser tes réponses auto

Va dans le fichier `src/vinted_mcp/templates.py`. T'as 9 templates préconfigurés (dispo, taille, état, délai d'envoi, négo de prix, etc.). Modifie le texte pour que ça sonne comme toi. Redémarre Claude après modif.

Tu peux ajouter des templates en copiant la structure d'un existant.

---

## Si ça casse

**"auth_required"** dans une réponse de Claude → tes cookies sont expirés. Refais l'étape 3.

**"403 Forbidden"** systématique → Vinted te bloque. Attends 30 min, et **ralentis le rythme** (pas plus d'une commande toutes les quelques secondes).

**Claude voit pas le serveur "vinted"** → tu as oublié de complètement quitter et relancer Claude Desktop. Ferme via l'icône système tray, pas juste la croix.

**Un truc retourne 404** → Vinted a peut-être changé l'endpoint. Ouvre une issue sur le repo, on verra.

---

## Tips de pro

- **Garde un rythme humain.** Si tu fais 200 actions en 5 min, Vinted va te détecter et te bloquer. La règle : si un humain pourrait pas physiquement le faire, fais-le pas.
- **Refresh tes cookies tous les 15 jours** environ, sinon ça expire et tu galères.
- **Backup ton `claude_desktop_config.json`** une fois qu'il marche, comme ça si tu réinstalles t'as pas à tout refaire.
- **Vinted Pro reste l'option propre** si tu vends sérieusement. C'est officiel, gratuit, et leur Items API te laisse créer/modifier/supprimer des annonces sans risque. Sérieux, regarde ça si tu fais plus de quelques dizaines de ventes par mois.

---

Allez bon courage Serkam, fais-toi des sous 💸
