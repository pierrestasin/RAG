# 🚀 Guide de déploiement sur Render

## Configuration Render

### 1. Créer le Web Service

1. Allez sur https://render.com
2. Cliquez sur "New +" → "Web Service"
3. Connectez votre dépôt GitHub

### 2. Configuration du service

Utilisez ces paramètres :

```
Name: rag-backend (ou votre choix)
Region: Frankfurt (EU Central)
Branch: main
Root Directory: (laisser vide)
Runtime: Python 3
Build Command: pip install --upgrade pip && pip install -r requirements.txt
Start Command: ./start.sh
```

⚠️ **IMPORTANT** : Le script `start.sh` active automatiquement l'environnement virtuel

### 3. Variables d'environnement

Ajoutez cette variable d'environnement :

```
GEMINI_API_KEY=votre_cle_api_ici
```

⚠️ **Générez votre clé sur** : https://aistudio.google.com/app/apikey

**⚠️ IMPORTANT** : Ne commitez JAMAIS le fichier .env sur Git !

### 4. Plan

- **Free plan** : Gratuit mais s'endort après 15 minutes d'inactivité
- **Starter plan** ($7/mois) : Toujours actif

### 5. Déployer

Cliquez sur "Create Web Service" et attendez 3-5 minutes.

Vous obtiendrez une URL du type :
```
https://rag-lqyi.onrender.com
```

### 6. Mettre à jour le frontend

Dans [index.html](index.html), vérifiez que l'URL de production est correcte (ligne 320) :

```javascript
const API_URL = IS_LOCAL ? 'http://localhost:5001' : 'https://VOTRE-URL.onrender.com';
```

## Déploiement du frontend sur Vercel

1. Créez un compte sur https://vercel.com
2. Cliquez sur "Add New" → "Project"
3. Importez votre dépôt Git
4. Configuration :
   - **Framework Preset** : Other
   - **Build Command** : (laisser vide)
   - **Output Directory** : (laisser vide)
5. Déployez

Votre frontend sera disponible sur :
```
https://votre-projet.vercel.app
```

## Test du déploiement

1. Testez l'API backend :
```bash
curl https://VOTRE-URL.onrender.com/health
```

Devrait retourner :
```json
{"status":"ok","model":"gemini-1.5-pro"}
```

2. Ouvrez votre frontend Vercel
3. Uploadez un PDF de test
4. Posez une question

## Troubleshooting

### Erreur "ModuleNotFoundError: No module named 'waitress'"

✅ **Résolu** avec la nouvelle version de `run_waitress.py`

### Le serveur ne démarre pas

Vérifiez les logs Render :
- La variable `GEMINI_API_KEY` est bien définie
- Le build s'est terminé sans erreur
- Python 3.11.9 est utilisé

### CORS errors

Si vous avez des erreurs CORS, vérifiez que `flask-cors` est bien installé et configuré dans [pdf_analyzer_backend.py](pdf_analyzer_backend.py:12).

### Le plan gratuit s'endort

C'est normal. Solutions :
1. Passer au plan Starter ($7/mois)
2. Utiliser un service de "ping" comme UptimeRobot pour garder l'API active
3. Accepter le délai de 30-60 secondes au premier chargement

## Commandes utiles

### Redéployer manuellement
```bash
git add .
git commit -m "Update"
git push origin main
```

Render redéploiera automatiquement.

### Voir les logs en temps réel
Dans le dashboard Render → Votre service → Onglet "Logs"
