from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import PyPDF2
import io
import os
from dotenv import load_dotenv

load_dotenv()  # Charge les variables du fichier .env

app = Flask(__name__)
CORS(app)  # Permet les requêtes depuis le frontend

# Configuration Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
genai.configure(api_key=GEMINI_API_KEY)

# Utilise Gemini 1.5 Pro pour les longs documents (meilleurs quotas gratuits)
model = genai.GenerativeModel('gemini-1.5-pro')

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
    try:
        data = request.json
        question = data.get('question')
        documents_text = data.get('documents_text')
        
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

        # Génération avec Gemini
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.1,  # Faible température pour précision
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 8192,
            }
        )
        
        return jsonify({
            'success': True,
            'answer': response.text
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Vérification santé API"""
    return jsonify({'status': 'ok', 'model': 'gemini-1.5-pro'})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
