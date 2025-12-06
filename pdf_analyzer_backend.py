from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import PyPDF2
import io
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()  # Charge les variables du fichier .env

app = Flask(__name__)
CORS(app)  # Permet les requêtes depuis le frontend

# Configuration Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
genai.configure(api_key=GEMINI_API_KEY)

# Configuration des modèles disponibles avec leurs prix
MODELS_CONFIG = {
    'gemini-1.5-flash': {
        'name': 'Gemini 1.5 Flash',
        'description': 'Rapide et économique - Idéal pour documents courts',
        'context_window': 1000000,
        'free_tier': {'rpm': 15, 'rpd': 1500, 'tpm': 1000000},
        'pricing': {'input': 0.075, 'output': 0.30}  # $ per million tokens
    },
    'gemini-1.5-pro': {
        'name': 'Gemini 1.5 Pro',
        'description': 'Meilleur pour documents longs (200-300 pages)',
        'context_window': 2000000,
        'free_tier': {'rpm': 15, 'rpd': 1500, 'tpm': 2000000},
        'pricing': {'input': 1.25, 'output': 5.00}
    },
    'gemini-2.0-flash-exp': {
        'name': 'Gemini 2.0 Flash (Experimental)',
        'description': 'Dernière génération - Gratuit pendant preview',
        'context_window': 1000000,
        'free_tier': {'rpm': 10, 'rpd': 1500, 'tpm': 1000000},
        'pricing': {'input': 0.00, 'output': 0.00}  # Free during preview
    }
}

# Modèle par défaut
current_model_name = 'gemini-1.5-pro'
model = genai.GenerativeModel(current_model_name)

# Compteur d'utilisation (simple, en mémoire - reset à chaque redémarrage)
usage_stats = {
    'requests_today': 0,
    'tokens_input_today': 0,
    'tokens_output_today': 0,
    'estimated_cost': 0.0,
    'last_reset': datetime.now().date()
}

def reset_daily_stats_if_needed():
    """Reset les stats si on change de jour"""
    today = datetime.now().date()
    if usage_stats['last_reset'] != today:
        usage_stats['requests_today'] = 0
        usage_stats['tokens_input_today'] = 0
        usage_stats['tokens_output_today'] = 0
        usage_stats['estimated_cost'] = 0.0
        usage_stats['last_reset'] = today

def estimate_tokens(text):
    """Estimation rapide du nombre de tokens (≈ 4 caractères par token)"""
    return len(text) // 4

def calculate_cost(input_tokens, output_tokens, model_name):
    """Calcule le coût estimé en dollars"""
    config = MODELS_CONFIG.get(model_name, MODELS_CONFIG['gemini-1.5-pro'])
    pricing = config['pricing']

    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']

    return {
        'input_cost': round(input_cost, 6),
        'output_cost': round(output_cost, 6),
        'total_cost': round(input_cost + output_cost, 6)
    }

@app.route('/models', methods=['GET'])
def get_models():
    """Retourne la liste des modèles disponibles"""
    return jsonify({
        'success': True,
        'current_model': current_model_name,
        'models': MODELS_CONFIG
    })

@app.route('/model', methods=['POST'])
def set_model():
    """Change le modèle actuel"""
    global current_model_name, model

    try:
        data = request.json
        new_model = data.get('model_name')

        if new_model not in MODELS_CONFIG:
            return jsonify({
                'success': False,
                'error': f'Modèle inconnu: {new_model}'
            }), 400

        current_model_name = new_model
        model = genai.GenerativeModel(current_model_name)

        return jsonify({
            'success': True,
            'model': current_model_name
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/usage', methods=['GET'])
def get_usage():
    """Retourne les statistiques d'utilisation"""
    reset_daily_stats_if_needed()

    config = MODELS_CONFIG[current_model_name]
    free_tier = config['free_tier']

    return jsonify({
        'success': True,
        'usage': {
            'requests_today': usage_stats['requests_today'],
            'requests_remaining': max(0, free_tier['rpd'] - usage_stats['requests_today']),
            'tokens_input_today': usage_stats['tokens_input_today'],
            'tokens_output_today': usage_stats['tokens_output_today'],
            'estimated_cost_today': usage_stats['estimated_cost'],
            'free_tier_limits': free_tier,
            'current_model': current_model_name
        }
    })

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Upload et extraction de texte des PDFs"""
    try:
        files = request.files.getlist('files')
        documents = []

        for file in files:
            # Extraction du texte PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ""
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text += f"\n\n--- Page {page_num} ---\n"
                text += page.extract_text()

            documents.append({
                'filename': file.filename,
                'text': text,
                'pages': len(pdf_reader.pages)
            })

        return jsonify({
            'success': True,
            'documents': documents,
            'total_pages': sum(d['pages'] for d in documents)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyse les documents avec Gemini"""
    global usage_stats
    reset_daily_stats_if_needed()

    try:
        data = request.json
        question = data.get('question')
        documents_text = data.get('documents_text')
        selected_model = data.get('model_name', current_model_name)

        # Utiliser le modèle sélectionné
        if selected_model != current_model_name:
            analysis_model = genai.GenerativeModel(selected_model)
        else:
            analysis_model = model

        # Construction du prompt avec citations
        prompt = f"""Tu es un assistant d'analyse de documents scientifiques. Analyse les documents fournis ci-dessous et réponds à la question.

RÈGLES STRICTES :
- Base tes réponses UNIQUEMENT sur le contenu des documents
- Cite TOUJOURS le numéro de page pour chaque affirmation
- Si l'information n'est pas dans les documents, indique "Non trouvé dans les documents"
- Indique ton niveau de confiance (Élevé/Moyen/Faible)
- Utilise un format structuré avec des sections claires

DOCUMENTS :
{documents_text}

QUESTION :
{question}

RÉPONSE (avec citations de pages) :"""

        # Estimation des tokens d'entrée
        input_tokens = estimate_tokens(prompt)

        # Génération avec Gemini
        response = analysis_model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.1,  # Faible température pour précision
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 8192,
            }
        )

        # Estimation des tokens de sortie
        output_tokens = estimate_tokens(response.text)

        # Calcul du coût
        cost_info = calculate_cost(input_tokens, output_tokens, selected_model)

        # Mise à jour des stats
        usage_stats['requests_today'] += 1
        usage_stats['tokens_input_today'] += input_tokens
        usage_stats['tokens_output_today'] += output_tokens
        usage_stats['estimated_cost'] += cost_info['total_cost']

        return jsonify({
            'success': True,
            'answer': response.text,
            'usage': {
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost': cost_info,
                'model_used': selected_model
            }
        })

    except Exception as e:
        error_message = str(e)

        # Détecter les erreurs de quota
        if '429' in error_message or 'quota' in error_message.lower():
            return jsonify({
                'success': False,
                'error': 'Quota dépassé. Veuillez attendre ou changer de modèle.',
                'error_type': 'quota_exceeded',
                'details': error_message
            }), 429

        return jsonify({'success': False, 'error': error_message}), 500


@app.route('/health', methods=['GET'])
def health():
    """Vérification santé API"""
    return jsonify({
        'status': 'ok',
        'model': current_model_name,
        'api_key_set': bool(GEMINI_API_KEY and GEMINI_API_KEY != 'YOUR_API_KEY_HERE')
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)
