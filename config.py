from pathlib import Path

BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "models"
DB_PATH = BASE_DIR / "supportpilot.db"

# Output of clean_data.py (columns: ticket, category, clean_ticket)
CLEAN_DATA_PATH = BASE_DIR / "tickets_clean.csv"

VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.joblib"
MODEL_PATH = MODEL_DIR / "ticket_classifier.joblib"
REPORT_PATH = MODEL_DIR / "classification_report.txt"
CONFUSION_PATH = MODEL_DIR / "confusion_matrix.png"
