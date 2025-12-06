# 📊 Guide des quotas Gemini API

## Différences entre les modèles Gemini

### ⚠️ Gemini 2.5 Pro (NOUVEAU - quotas limités)

**Quotas gratuits :**
- ⚠️ **Très limité** pour le tier gratuit
- Recommandé uniquement avec un compte payant

**Quand l'utiliser :**
- Seulement si vous avez activé la facturation
- Pour des tâches complexes nécessitant les dernières améliorations

### ✅ Gemini 1.5 Pro (RECOMMANDÉ pour le tier gratuit)

**Quotas gratuits (généreux) :**
- **15 requêtes par minute**
- **1 500 requêtes par jour**
- **1 million de requêtes par mois**
- Fenêtre contextuelle : **2 millions de tokens**

**Tarifs payants :**
- Input : $1.25/million de tokens
- Output : $5/million de tokens

**Idéal pour :**
- ✅ Documents longs (200-300+ pages)
- ✅ Analyse approfondie avec citations
- ✅ Usage gratuit modéré (1 utilisateur)

### ⚡ Gemini 1.5 Flash (Alternative économique)

**Quotas gratuits :**
- **15 requêtes par minute**
- **1 500 requêtes par jour**
- Fenêtre contextuelle : **1 million de tokens**

**Tarifs payants :**
- Input : $0.075/million de tokens (16x moins cher que Pro)
- Output : $0.30/million de tokens

**Idéal pour :**
- ✅ Réponses rapides
- ✅ Documents courts/moyens (<100 pages)
- ✅ Économiser des coûts en production

## Comprendre l'erreur 429 Quota Exceeded

### Causes possibles

**1. Modèle incompatible avec le tier gratuit**
```
Error: gemini-2.5-pro
Quota exceeded for metric: generate_content_free_tier_input_token_count
```
➡️ **Solution** : Passer à `gemini-1.5-pro` ou `gemini-1.5-flash`

**2. Trop de requêtes par minute**
```
Please retry in 32.748981611s
```
➡️ **Solution** : Attendre 1 minute entre les requêtes

**3. Quota journalier dépassé**
```
Quota exceeded for metric: GenerateRequestsPerDayPerProjectPerModel
```
➡️ **Solution** : Attendre minuit (UTC) ou passer au plan payant

## Changer de modèle dans le code

### Passer à Gemini 1.5 Pro (recommandé)

Dans `pdf_analyzer_backend.py` :
```python
model = genai.GenerativeModel('gemini-1.5-pro')
```

### Passer à Gemini 1.5 Flash (économique)

```python
model = genai.GenerativeModel('gemini-1.5-flash')
```

### Passer à Gemini 2.5 Pro (payant uniquement)

```python
model = genai.GenerativeModel('gemini-2.5-pro')
```

## Surveiller votre utilisation

### Dashboard Google AI Studio

1. Allez sur https://ai.google.dev/usage?tab=rate-limit
2. Consultez vos quotas en temps réel :
   - Requests per minute
   - Requests per day
   - Tokens per day

### Logs Render

Les erreurs de quota apparaissent dans les logs :
```
Dashboard Render → Votre service → Logs
```

## Optimiser l'utilisation des tokens

### 1. Limiter la longueur des documents

Au lieu d'envoyer 300 pages :
```python
# Option 1 : Chunking intelligent
def chunk_document(text, max_tokens=100000):
    # Découper en morceaux de ~100k tokens
    pass

# Option 2 : Extraction ciblée
def extract_relevant_sections(text, query):
    # Identifier les sections pertinentes d'abord
    pass
```

### 2. Réduire max_output_tokens

```python
generation_config={
    'max_output_tokens': 2048,  # Au lieu de 8192
}
```

### 3. Cacher les résultats fréquents

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def analyze_cached(question, doc_hash):
    return model.generate_content(...)
```

### 4. Utiliser Flash pour le prétraitement

```python
# Étape 1 : Flash identifie les sections pertinentes (rapide/économique)
flash_model = genai.GenerativeModel('gemini-1.5-flash')
relevant_sections = flash_model.generate_content(f"Trouve les sections pertinentes: {query}")

# Étape 2 : Pro analyse en profondeur (lent/précis)
pro_model = genai.GenerativeModel('gemini-1.5-pro')
detailed_analysis = pro_model.generate_content(f"Analyse: {relevant_sections}")
```

## Passer au plan payant

### Quand passer au payant ?

- Vous dépassez 1 500 requêtes/jour
- Besoin de plus de 15 requêtes/minute
- Usage en production avec plusieurs utilisateurs
- Besoin de Gemini 2.5 Pro

### Comment activer la facturation

1. Allez sur https://aistudio.google.com/app/apikey
2. Cliquez sur votre projet
3. Activez la facturation Google Cloud
4. Les quotas augmentent automatiquement :
   - **2 000 requêtes par minute** (au lieu de 15)
   - **Illimité par jour** (au lieu de 1 500)

### Coûts estimés

**Scénario : 100 analyses de documents de 300 pages/mois**

Avec Gemini 1.5 Pro :
- Input : 300 pages × 500 tokens/page × 100 = 15M tokens × $1.25/M = **$18.75**
- Output : 2k tokens × 100 = 200k tokens × $5/M = **$1**
- **Total : ~$20/mois**

Avec Gemini 1.5 Flash :
- Input : 15M tokens × $0.075/M = **$1.12**
- Output : 200k tokens × $0.30/M = **$0.06**
- **Total : ~$1.20/mois** (16x moins cher)

## Comparaison des modèles

| Modèle | Quota gratuit/min | Quota gratuit/jour | Tokens contexte | Prix Input | Prix Output | Meilleur pour |
|--------|------------------|-------------------|----------------|-----------|------------|--------------|
| **1.5 Flash** | 15 | 1 500 | 1M | $0.075/M | $0.30/M | Rapide, économique |
| **1.5 Pro** | 15 | 1 500 | 2M | $1.25/M | $5/M | Documents longs, gratuit |
| **2.5 Pro** | 0* | 0* | 2M | $2.50/M | $10/M | Payant seulement |

*Gemini 2.5 Pro n'a pas de tier gratuit utilisable en pratique

## Recommandation finale

**Pour ce projet RAG (documents scientifiques) :**

1. **Développement/Tests** : `gemini-1.5-pro` (gratuit, généreux)
2. **Production légère** : `gemini-1.5-pro` (max 1 500 requêtes/jour)
3. **Production intensive** : `gemini-1.5-flash` avec facturation activée
4. **Analyses complexes** : `gemini-2.5-pro` avec facturation activée

## Ressources

- [Documentation quotas Gemini](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Pricing Gemini API](https://ai.google.dev/pricing)
- [Dashboard usage](https://ai.google.dev/usage?tab=rate-limit)
- [Modèles disponibles](https://ai.google.dev/gemini-api/docs/models)
