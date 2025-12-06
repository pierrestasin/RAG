# 🔧 Guide de dépannage - Déploiement Render

## Erreurs courantes et solutions

### ❌ Erreur : `bash: line 1: python: command not found`

**Cause** : La Start Command utilise `python` au lieu de `python3`

**Solution** : Dans les paramètres Render, changez la Start Command :
```bash
# ❌ Incorrect
python run_waitress.py

# ✅ Correct
python3 run_waitress.py
```

---

### ❌ Erreur : `ModuleNotFoundError: No module named 'waitress'`

**Cause** : Les dépendances ne sont pas correctement installées ou accessibles

**Solution 1** : Vérifiez que le Build Command est correct :
```bash
./render_build.sh
```

**Solution 2** : Vérifiez que [render_build.sh](render_build.sh) a les permissions d'exécution :
```bash
chmod +x render_build.sh
git add render_build.sh
git commit -m "Add execute permission to render_build.sh"
git push
```

**Solution 3** : Utilisez un Build Command alternatif :
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

---

### ❌ Erreur : `ModuleNotFoundError: No module named 'pdf_analyzer_backend'`

**Cause** : Le fichier [pdf_analyzer_backend.py](pdf_analyzer_backend.py) n'est pas dans le bon répertoire

**Solution** : Vérifiez la structure :
```
/
├── pdf_analyzer_backend.py  ✅
├── run_waitress.py
├── requirements.txt
└── render_build.sh
```

---

### ❌ Erreur : `google.generativeai.types.generation_types.BlockedPromptException`

**Cause** : Le contenu du PDF est bloqué par les filtres de sécurité Gemini

**Solutions** :
1. Vérifiez que le PDF ne contient pas de contenu sensible
2. Ajustez les safety settings dans [pdf_analyzer_backend.py](pdf_analyzer_backend.py:79) :

```python
response = model.generate_content(
    prompt,
    generation_config={
        'temperature': 0.1,
        'top_p': 0.8,
        'top_k': 40,
        'max_output_tokens': 8192,
    },
    safety_settings={
        'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
        'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
        'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
        'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
    }
)
```

---

### ❌ Erreur : `google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded`

**Cause** : Vous avez dépassé le quota gratuit de l'API Gemini

**Solutions** :
1. **Attendez** : Le quota se réinitialise toutes les minutes
2. **Vérifiez vos quotas** : https://aistudio.google.com/app/apikey
3. **Passez au plan payant** si nécessaire

**Quotas gratuits** :
- 15 requêtes par minute
- 1 500 requêtes par jour
- 1 million de requêtes par mois

---

### ❌ Erreur CORS : `Access to fetch at '...' has been blocked by CORS policy`

**Cause** : Le frontend et le backend ne communiquent pas correctement

**Solution 1** : Vérifiez l'URL de l'API dans [index.html](index.html:320) :
```javascript
const API_URL = IS_LOCAL ? 'http://localhost:5001' : 'https://VOTRE-URL-RENDER.onrender.com';
```

**Solution 2** : Vérifiez que CORS est activé dans [pdf_analyzer_backend.py](pdf_analyzer_backend.py:12) :
```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # ✅ Doit être présent
```

---

### ⚠️ Le service Render s'arrête après 15 minutes

**Cause** : Plan gratuit de Render (comportement normal)

**Solutions** :
1. **Accepter le délai** : Le service redémarre en 30-60 secondes au prochain accès
2. **Passer au plan Starter** : $7/mois, service toujours actif
3. **Utiliser un ping service** : UptimeRobot pour garder le service actif (gratuit)

Configuration UptimeRobot :
- URL à pinger : `https://votre-url.onrender.com/health`
- Intervalle : Toutes les 5 minutes
- Type : HTTP(s)

---

### ❌ Build réussi mais le service ne démarre pas

**Checklist de diagnostic** :

1. **Vérifier les logs Render** :
   - Dashboard Render → Votre service → Onglet "Logs"
   - Cherchez la ligne `Starting Waitress server on port...`

2. **Vérifier les variables d'environnement** :
   - Dashboard Render → Votre service → Environment
   - `GEMINI_API_KEY` doit être définie

3. **Tester l'API Key localement** :
```bash
python3 list_models.py
```

4. **Vérifier le port** :
   - Render définit automatiquement `PORT` (généralement 10000)
   - [run_waitress.py](run_waitress.py:6) lit cette variable

---

### ❌ Erreur : `./render_build.sh: Permission denied`

**Cause** : Le script n'a pas les permissions d'exécution

**Solution** :
```bash
chmod +x render_build.sh
git add render_build.sh
git commit -m "Add execute permission"
git push
```

---

### ❌ Upload de PDF échoue : `413 Request Entity Too Large`

**Cause** : Le PDF est trop volumineux

**Solutions** :
1. **Compresser le PDF** : https://www.ilovepdf.com/compress_pdf
2. **Augmenter la limite** dans [pdf_analyzer_backend.py](pdf_analyzer_backend.py:11) :

```python
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
CORS(app)
```

---

### ❌ Réponses vides ou incohérentes de Gemini

**Cause** : Le prompt ou la température sont mal configurés

**Solutions** :
1. **Vérifiez la température** (doit être basse pour précision) :
```python
'temperature': 0.1,  # ✅ 0.1-0.3 pour documents factuels
```

2. **Améliorez le prompt** avec plus de contraintes :
```python
prompt = f"""CONTEXTE : Tu es un expert en analyse de documents scientifiques.
TÂCHE : Réponds UNIQUEMENT en te basant sur les documents fournis.
CONTRAINTES :
- Cite TOUJOURS la page source
- Si incertain, indique "Confiance: Faible"
- Si absent, réponds "Information non présente dans les documents"

DOCUMENTS :
{documents_text}

QUESTION : {question}

RÉPONSE :"""
```

---

## Commandes utiles pour déboguer

### Tester l'API localement
```bash
# Démarrer le serveur
python3 run_waitress.py

# Dans un autre terminal, tester l'endpoint health
curl http://localhost:10000/health
```

### Voir les logs Render en temps réel
1. Allez sur https://dashboard.render.com
2. Sélectionnez votre service
3. Cliquez sur "Logs" dans le menu de gauche
4. Les logs se mettent à jour en temps réel

### Forcer un redéploiement
```bash
git commit --allow-empty -m "Force redeploy"
git push origin main
```

### Tester les modèles Gemini disponibles
```bash
python3 list_models.py
```

---

## Ressources supplémentaires

- **Documentation Render** : https://render.com/docs
- **Documentation Gemini API** : https://ai.google.dev/docs
- **Limites API Gemini** : https://ai.google.dev/pricing
- **Support Render** : https://render.com/docs/troubleshooting-deploys

---

Si aucune de ces solutions ne fonctionne, vérifiez :
1. Les logs complets de Render
2. La console navigateur (F12) pour les erreurs frontend
3. Testez l'API directement avec `curl` ou Postman
