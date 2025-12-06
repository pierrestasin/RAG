import os
from waitress import serve
from pdf_analyzer_backend import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Waitress server on port {port}...")
    serve(app, host="0.0.0.0", port=port)
