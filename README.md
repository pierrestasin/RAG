# 📚 Analyseur de Documents Scientifiques - Gemini AI

Application web complète pour analyser des documents PDF longs (200-300+ pages) avec l'intelligence artificielle Gemini 1.5 Pro.

## ✨ Fonctionnalités

- ✅ Upload multiple de PDFs (jusqu'à 50 documents)
- ✅ Analyse avec citations de pages automatiques
- ✅ Interface conversationnelle type ChatGPT
- ✅ Fenêtre contextuelle massive (1-2M tokens)
- ✅ **Totalement gratuit** (API Gemini quota gratuit)

## 🚀 Installation rapide (5 minutes)

### Étape 1 : Prérequis

Installez Python 3.8+ sur votre ordinateur :
- **Windows** : https://www.python.org/downloads/
- **Mac** : `brew install python3`
- **Linux** : `sudo apt install python3 python3-pip`

### Étape 2 : Obtenir votre clé API Gemini (GRATUIT)

1. Allez sur : https://aistudio.google.com/app/apikey
2. Connectez-vous avec votre compte Google
3. Cliquez sur "Create API Key"
4. Copiez la clé (format : `AIzaSy...`)

### Étape 3 : Installation de l'application

```bash
# 1. Créer un dossier pour le projet
mkdir pdf-analyzer
cd pdf-analyzer

# 2. Télécharger les fichiers
# Copiez les 3 fichiers fournis :
# - pdf_analyzer_backend.py
# - index.html
# - requirements.txt

# 3. Installer les dépendances Python
pip install -r requirements.txt

# 4. Configurer votre clé API
# Sur Windows :
set GEMINI_API_KEY=VOTRE_CLE_ICI

# Sur Mac/Linux :
export GEMINI_API_KEY=VOTRE_CLE_ICI
```

### Étape 4 : Lancer l'application

```bash
# 1. Démarrer le serveur backend
python pdf_analyzer_backend.py

# 2. Dans un autre terminal, démarrer un serveur web pour le frontend
# Option A - Python 3 :
python -m http.server 8000

# Option B - Python 2 :
python -m SimpleHTTPServer 8000

# 3. Ouvrir votre navigateur
# Allez sur : http://localhost:8000
```

**C'est tout ! L'application est prête 🎉**

---

## 📖 Guide d'utilisation

### 1. Charger vos documents
- Glissez-déposez vos PDFs dans la zone de gauche
- Ou cliquez pour sélectionner des fichiers
- Cliquez sur "Charger les documents"
- ⏱️ Temps de chargement : ~10-30 secondes pour 3-4 documents de 200 pages

### 2. Poser des questions
Exemples de questions efficaces :
```
"Quelles sont les principales conclusions de l'étude ?"

"Compare les méthodologies utilisées dans les 3 documents"

"Extrais tous les chiffres et statistiques mentionnés sur le changement climatique"

"Quelle est la position de l'auteur sur [sujet] ? Cite les pages exactes"

"Y a-t-il des contradictions entre les documents sur [point précis] ?"
```

### 3. Obtenir des réponses fiables
L'IA inclut automatiquement :
- ✅ Citations avec numéros de page
- ✅ Niveau de confiance (Élevé/Moyen/Faible)
- ✅ Indication si l'info n'est pas dans les docs

---

## 💰 Coûts et limites

### Quota GRATUIT de l'API Gemini
- **15 requêtes par minute** (largement suffisant pour 1 utilisateur)
- **1 500 requêtes par jour**
- **1 million de requêtes par mois**
- Fenêtre contextuelle : **1-2 millions de tokens** (~1 500-3 000 pages)

### Si vous dépassez le quota gratuit
Passez à l'API payante (très économique) :
- **Input** : 1,25 $/million de tokens (~0,94 $ par document de 300 pages)
- **Output** : 5 $/million de tokens

**Exemple concret** : 100 analyses de documents de 300 pages = environ **100 $/mois**

---

## 🌐 Déploiement en ligne (pour partager avec d'autres)

### Option 1 : Déploiement gratuit avec Vercel (Frontend) + Render (Backend)

#### Backend sur Render.com (gratuit)
1. Créez un compte sur https://render.com
2. Créez un nouveau "Web Service"
3. Connectez votre dépôt Git (ou uploadez les fichiers)
4. Configuration :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `python pdf_analyzer_backend.py`
   - **Environment Variables** : Ajoutez `GEMINI_API_KEY`
5. Déployez (3-5 minutes)
6. Notez l'URL (ex: `https://votre-app.onrender.com`)

#### Frontend sur Vercel (gratuit)
1. Créez un compte sur https://vercel.com
2. Uploadez juste le fichier `index.html`
3. Dans `index.html`, remplacez :
   ```javascript
   const API_URL = 'http://localhost:5000';
   ```
   par :
   ```javascript
   const API_URL = 'https://votre-app.onrender.com';
   ```
4. Déployez
5. Vous obtenez une URL type : `https://votre-app.vercel.app`

**Total : 0 € de coûts d'hébergement !**

### Option 2 : Déploiement sur votre propre serveur
Si vous avez un VPS ou serveur dédié :
```bash
# Installer avec gunicorn pour la production
pip install gunicorn

# Lancer en production
gunicorn -w 4 -b 0.0.0.0:5000 pdf_analyzer_backend:app
```

---

## 🔧 Personnalisation avancée

### Ajouter une base vectorielle pour + de 3 000 pages

Si vos documents dépassent 3 000 pages, ajoutez Chroma :

```bash
pip install chromadb sentence-transformers
```

Modifiez le backend pour indexer les documents :
```python
import chromadb
from sentence_transformers import SentenceTransformer

# Initialisation
client = chromadb.Client()
collection = client.create_collection("documents")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Indexation par chunks
def chunk_text(text, chunk_size=1000):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) 
            for i in range(0, len(words), chunk_size)]

chunks = chunk_text(documents_text)
embeddings = embedder.encode(chunks)
collection.add(
    embeddings=embeddings.tolist(),
    documents=chunks,
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

# Recherche sémantique
query_embedding = embedder.encode([question])
results = collection.query(
    query_embeddings=query_embedding.tolist(),
    n_results=5
)
relevant_context = results['documents']
```

### Ajouter l'authentification utilisateur

Pour partager avec plusieurs personnes :
```bash
pip install flask-login
```

```python
from flask_login import LoginManager, login_required

# Configuration
login_manager = LoginManager()
login_manager.init_app(app)

# Protéger les routes
@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    # ... votre code
```

---

## ❓ FAQ / Résolution de problèmes

### L'upload prend trop de temps
- **Cause** : PDFs très lourds (scans)
- **Solution** : Compresser les PDFs avec https://www.ilovepdf.com/compress_pdf

### Erreur "CORS policy"
- **Cause** : Frontend et backend sur des ports différents
- **Solution** : Déjà configuré avec `flask-cors`, vérifiez que le backend tourne

### "API key not valid"
- **Cause** : Clé API incorrecte ou non configurée
- **Solution** : 
  ```bash
  # Vérifier la variable d'environnement
  echo $GEMINI_API_KEY
  
  # Si vide, la redéfinir
  export GEMINI_API_KEY=VOTRE_CLE
  ```

### Réponses imprécises
- **Cause** : Question trop vague
- **Solution** : Posez des questions spécifiques avec contexte
  - ❌ Mauvais : "Parle-moi de l'étude"
  - ✅ Bon : "Quels sont les 3 résultats principaux de l'étude sur la page 45-60 ?"

### Quotas dépassés
- **Cause** : + de 15 requêtes/minute ou 1 500/jour
- **Solution** : Passer à l'API payante ou attendre la réinitialisation

---

## 🎯 Optimisations recommandées

### Pour minimiser les hallucinations
Ajoutez ce système de scoring dans le prompt :
```python
prompt = f"""
NIVEAU DE CONFIANCE REQUIS :
- Élevé : Information explicitement mentionnée avec page exacte
- Moyen : Information implicite mais déductible logiquement
- Faible : Inférence basée sur le contexte général

Pour chaque affirmation, indique [CONFIANCE: Élevé/Moyen/Faible]

{votre_prompt_actuel}
"""
```

### Pour accélérer les réponses
Limitez la longueur des réponses :
```python
generation_config={
    'temperature': 0.1,
    'max_output_tokens': 2048,  # Au lieu de 8192
}
```

### Pour économiser les tokens
Envoyez seulement les sections pertinentes au lieu du document entier :
```python
# 1. Première passe : identifier les sections pertinentes
sections_query = f"Quelles sections du document contiennent des infos sur : {question}"

# 2. Seconde passe : analyse approfondie uniquement sur ces sections
```

---

## 📊 Monitoring et Analytics

Ajoutez un compteur d'utilisation :
```python
import json
from datetime import datetime

usage_log = []

@app.route('/analyze', methods=['POST'])
def analyze():
    start_time = datetime.now()
    
    # ... votre code d'analyse
    
    usage_log.append({
        'timestamp': start_time.isoformat(),
        'question': question,
        'response_time': (datetime.now() - start_time).seconds,
        'tokens_used': len(prompt.split())  # Approximation
    })
    
    # Sauvegarder périodiquement
    with open('usage.json', 'w') as f:
        json.dump(usage_log, f)
```

---

## 🆘 Support et Contact

- **Documentation Gemini** : https://ai.google.dev/docs
- **API Limits** : https://ai.google.dev/pricing
- **Issues** : Créez un ticket sur votre dépôt GitHub

---

## 📄 Licence

Ce projet est sous licence MIT - libre d'utilisation, modification et distribution.

---

**Créé avec ❤️ pour faciliter l'analyse de documents scientifiques**
