# This file is kept for backward compatibility
# Render now uses Gunicorn directly via the Start Command
from pdf_analyzer_backend import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
