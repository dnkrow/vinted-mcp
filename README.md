# Vinted MCP (non-officiel)

Serveur MCP pour piloter Vinted depuis Claude Desktop ou Cowork. Cible un vendeur qui veut :
- répondre rapidement aux messages des acheteurs (avec assistance IA),
- gérer son catalogue (baisser des prix, fermer des annonces),
- avoir une vue stats rapide.

> ⚠️ **Important — l'API officielle existe.** Si l'utilisateur est éligible **Vinted Pro** ([pro-portal.svc.vinted.com](https://pro-portal.svc.vinted.com/)), la **gestion des annonces (création / modification / suppression / ventes)** doit passer par l'**API officielle Vinted Pro** ([pro-docs.svc.vinted.com](https://pro-docs.svc.vinted.com/)) : Items, Orders, Webhooks. Zéro risque de ban, 500 articles autorisés. **Ce MCP est utile en complément pour la messagerie**, qui n'est pas couverte par l'API Pro.

---

## Plan d'usage recommandé

| Besoin | Outil | Risque |
|---|---|---|
| Lister / modifier / supprimer annonces, stats ventes | **API Vinted Pro (officielle)** | ✅ Aucun |
| Lecture inbox + assistance réponse + auto-réponse questions standards | **Ce MCP** | ⚠️ Faible si rythme raisonnable |

Si pas éligible Vinted Pro, ce MCP fait tout — mais à utiliser avec parcimonie.

---

## Installation (Windows 11)

### 1. Python

```powershell
# Vérifier que Python est installé (3.10+)
py --version

# Sinon: télécharger depuis https://www.python.org/downloads/windows/
# IMPORTANT à l'install: cocher "Add Python to PATH"
```

### 2. Installer le serveur

Récupérer le dossier `vinted-mcp` sur le PC, puis dans PowerShell :

```powershell
cd C:\chemin\vers\vinted-mcp
py -m pip install -e .
```

### 3. Récupérer les cookies Vinted

Vinted bloque le login programmatique (anti-bot Datadome). Donc on réutilise les cookies d'une session navigateur déjà loggée.

1. Dans Chrome / Edge, ouvre **vinted.fr** et connecte-toi normalement.
2. `F12` → onglet **Application** (Chrome) ou **Storage** (Edge) → **Cookies** → `https://www.vinted.fr`.
3. Copier la valeur des cookies suivants (clic droit → "Show requested URL" / "Copy value") :
   - `_vinted_fr_session` (obligatoire)
   - `access_token_web` (recommandé)
   - `anon_id` (recommandé)
4. Copier aussi son **User-Agent** exact : taper `chrome://version` dans la barre d'adresse, ligne "User Agent".

Les cookies expirent après quelques jours/semaines. À rafraîchir périodiquement.

### 4. Brancher dans Claude Desktop

Éditer le fichier de config :

```
%APPDATA%\Claude\claude_desktop_config.json
```

(Le plus simple : `Win+R` → coller `%APPDATA%\Claude` → ouvrir `claude_desktop_config.json` avec Notepad.)

Ajouter le bloc (adapter le chemin et les valeurs) :

```json
{
  "mcpServers": {
    "vinted": {
      "command": "py",
      "args": ["-m", "vinted_mcp.server"],
      "env": {
        "VINTED_DOMAIN": "vinted.fr",
        "VINTED_SESSION_COOKIE": "COLLER_VALEUR_ICI",
        "VINTED_ACCESS_TOKEN_WEB": "COLLER_VALEUR_ICI",
        "VINTED_ANON_ID": "COLLER_VALEUR_ICI",
        "VINTED_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."
      }
    }
  }
}
```

Fermer puis relancer Claude Desktop. Le serveur "vinted" doit apparaître dans la liste des MCPs avec **15 tools**.

### 5. Premier test

Dans Claude, lance simplement :
> *"Vinted whoami"*

Si ça renvoie ton profil → tout est branché. Sinon → cookies à rafraîchir.

---

## Tools exposés

### Lecture publique (pas d'auth)
- `search_items` — recherche dans le catalogue
- `get_item` — détail d'un article

### Compte (auth requise)
- `whoami` — utilisateur connecté (test cookies)
- `my_items`, `list_my_active_items`, `list_my_sold_items` — ses annonces
- `get_seller_stats` — récap (actifs, vendus, vues, favoris)

### Gestion d'annonces (auth requise — préférer Vinted Pro si éligible)
- `update_item_price` — changer le prix d'une annonce
- `close_item` — désactiver (réversible)
- `reactivate_item` — réactiver
- `delete_item` — supprimer (⚠️ irréversible)

### Messagerie (auth requise)
- `list_conversations` — boîte de réception
- `get_conversation` — messages d'un fil
- `send_message` — répondre

### Templates de réponse
- `list_reply_templates` — voir les templates disponibles
- `render_template` — remplir un template avec des variables

### Debug
- `debug_get` — frapper un endpoint `/api/v2/...` arbitraire

---

## Auto-réponse aux questions standards

L'idée : Claude lit régulièrement l'inbox, repère les messages qui correspondent à un template **`safe_auto: true`** (genre "toujours dispo ?"), répond automatiquement. Les autres sont laissés en attente pour validation humaine.

**Setup recommandé via Cowork (tâche planifiée)** :

1. Dans Claude / Cowork, demander :
   > "Crée une tâche planifiée qui tourne toutes les 15 min : appelle `list_conversations` sur Vinted, pour chaque nouveau message non répondu identifie si une réponse template safe_auto s'applique (toujours dispo, délai d'envoi, lot, remerciement après achat). Si oui, envoie la réponse via `send_message`. Sinon, mets-le dans une liste à reviewer et signale-moi."

2. Au début, laisser tourner quelques jours et **vérifier manuellement** les réponses envoyées. Affiner les templates dans `src/vinted_mcp/templates.py` si besoin.

**Volumes raisonnables** : pas plus d'un cycle toutes les 10-15 min. Vinted détecte les patterns trop réguliers.

---

## Personnaliser les templates

Édite `src/vinted_mcp/templates.py`. Chaque template a un id, un texte avec des `{placeholders}`, et un flag `safe_auto` qui indique s'il peut partir sans validation.

Pour ajouter un template, copier la structure d'un existant et redémarrer Claude Desktop.

---

## Limitations connues

- **Datadome.** Si trop de requêtes en rafale → 403. Garder un rythme humain.
- **Cookies expirent.** À rafraîchir périodiquement.
- **Endpoints inbox = best guess.** Les chemins `/inbox/conversations` etc. viennent de l'observation du trafic web. Si Vinted les change, utiliser `debug_get` pour explorer (DevTools → Network → filtre XHR pendant qu'on navigue dans la messagerie).
- **Création d'annonces non implémentée.** Trop complexe en non-officiel (upload photos, catégories, marques, tailles). **Passer par Vinted Pro pour ça.**

---

## Architecture

```
vinted-mcp/
├── pyproject.toml
├── .env.example
├── README.md
└── src/vinted_mcp/
    ├── __init__.py
    ├── client.py      ← VintedClient : HTTP, cookies, endpoints
    ├── server.py      ← FastMCP server : 15 tools
    └── templates.py   ← Réponses standards éditables
```

## Licence

MIT.
