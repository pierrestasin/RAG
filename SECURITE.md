# 🔒 Guide de sécurité - Gestion des clés API

## ⚠️ IMPORTANT : Ne jamais commiter les clés API

### Problème : Clé API exposée

Si votre clé API Gemini est commitée sur GitHub, elle sera automatiquement détectée et révoquée par Google. Vous verrez l'erreur :

```
403 Your API key was reported as leaked. Please use another API key.
```

### ✅ Solution en 3 étapes

#### 1. Générer une nouvelle clé API

1. Allez sur https://aistudio.google.com/app/apikey
2. **Révoquez l'ancienne clé** (celle qui fuit)
3. Cliquez sur "Create API Key"
4. Copiez la nouvelle clé (format : `AIzaSy...`)

#### 2. Mettre à jour la clé localement

Créez/mettez à jour le fichier `.env` (qui est dans `.gitignore`) :

```bash
# .env
GEMINI_API_KEY=VOTRE_NOUVELLE_CLE_ICI
```

#### 3. Mettre à jour Render

1. Allez sur https://dashboard.render.com
2. Sélectionnez votre service
3. Allez dans **Environment**
4. Modifiez la variable `GEMINI_API_KEY` avec la nouvelle clé
5. Cliquez sur "Save Changes"
6. Le service redémarrera automatiquement

### 🛡️ Bonnes pratiques de sécurité

#### ✅ À FAIRE

1. **Toujours utiliser `.gitignore`** pour exclure `.env`
   ```gitignore
   .env
   *.key
   *.pem
   secrets/
   ```

2. **Utiliser des variables d'environnement** pour les secrets
   ```python
   # ✅ BON
   api_key = os.environ.get('GEMINI_API_KEY')

   # ❌ MAUVAIS
   api_key = "AIzaSy..."
   ```

3. **Créer un `.env.example`** pour documenter
   ```bash
   # .env.example
   GEMINI_API_KEY=your_api_key_here
   DATABASE_URL=your_database_url_here
   ```

4. **Vérifier avant de commiter**
   ```bash
   # Vérifier qu'aucun secret n'est tracké
   git status
   git diff --cached
   ```

#### ❌ À NE JAMAIS FAIRE

1. ❌ Commiter le fichier `.env`
2. ❌ Écrire des clés en dur dans le code
3. ❌ Partager des clés par email/chat
4. ❌ Réutiliser la même clé partout
5. ❌ Commiter des fichiers `config.json` avec secrets

### 🔍 Vérifier si vos secrets sont exposés

#### Rechercher dans l'historique Git

```bash
# Rechercher "AIzaSy" (format des clés Gemini)
git log -p -S "AIzaSy" --all

# Rechercher dans tous les commits
git grep "AIzaSy" $(git rev-list --all)
```

#### Scanner avec TruffleHog (optionnel)

```bash
# Installer truffleHog
pip install truffleHog

# Scanner le repo
truffleHog --regex --entropy=False .
```

### 🧹 Nettoyer l'historique Git (avancé)

Si des secrets sont dans l'historique Git, vous devez les supprimer :

#### Option 1 : Supprimer un fichier de l'historique

```bash
# Supprimer .env de tout l'historique
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Forcer le push (⚠️ ATTENTION : réécrit l'historique)
git push origin --force --all
```

#### Option 2 : Utiliser BFG Repo-Cleaner (recommandé)

```bash
# Installer BFG
brew install bfg  # macOS
# ou télécharger sur : https://rtyley.github.io/bfg-repo-cleaner/

# Supprimer le fichier de l'historique
bfg --delete-files .env

# Nettoyer
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Forcer le push
git push origin --force --all
```

⚠️ **Attention** : Ces commandes réécrivent l'historique Git. Tous les collaborateurs devront re-cloner le repo.

### 🔐 Alternatives sécurisées

#### 1. Utiliser un gestionnaire de secrets

**Pour le développement local :**
- [direnv](https://direnv.net/) - Charge automatiquement `.env`
- [dotenv](https://github.com/motdotla/dotenv) - Librairie Python (déjà utilisée)

**Pour la production :**
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Google Secret Manager](https://cloud.google.com/secret-manager)
- [HashiCorp Vault](https://www.vaultproject.io/)

#### 2. Limiter les permissions de la clé API

Sur Google AI Studio :
1. Créez des clés API différentes par environnement (dev/prod)
2. Définissez des restrictions d'utilisation
3. Surveillez l'utilisation dans le dashboard

### 📊 Monitoring de sécurité

#### GitHub Secret Scanning

GitHub détecte automatiquement les secrets exposés. Si vous recevez une alerte :
1. Révoquez immédiatement la clé
2. Créez une nouvelle clé
3. Nettoyez l'historique Git

#### Configurer les alertes

Dans votre repo GitHub :
1. Settings → Security → Code security and analysis
2. Activez "Secret scanning"
3. Activez "Push protection"

### 🆘 En cas d'exposition

**Actions immédiates :**

1. ✅ Révoquer la clé exposée sur https://aistudio.google.com/app/apikey
2. ✅ Générer une nouvelle clé
3. ✅ Mettre à jour `.env` et Render
4. ✅ Supprimer la clé de Git avec `git rm --cached`
5. ✅ Surveiller l'utilisation de l'API pour détecter un usage frauduleux

**Si la clé a été utilisée frauduleusement :**

1. Contactez Google Cloud Support
2. Vérifiez vos quotas et factures
3. Activez la facturation par alertes

### 📚 Ressources

- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Google AI Studio - Best Practices](https://ai.google.dev/docs)
- [12 Factor App - Config](https://12factor.net/config)

---

**En résumé** : Ne jamais commiter de secrets. Toujours utiliser des variables d'environnement et `.gitignore`.
