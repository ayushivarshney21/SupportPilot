"""Combines classification + severity + priority (the slide's process_ticket)."""
import joblib
import config
from preprocess import preprocess_text          # SAME cleaning as used for training
from severity import analyze_severity, analyze_impact, calculate_priority

_vectorizer = None
_model = None


def _load():
    global _vectorizer, _model
    if _model is None:
        if not config.MODEL_PATH.exists():
            raise FileNotFoundError("Model not found. Run: python train_classifier.py")
        _vectorizer = joblib.load(config.VECTORIZER_PATH)
        _model = joblib.load(config.MODEL_PATH)
    return _vectorizer, _model


def process_ticket(ticket: str) -> dict:
    vectorizer, model = _load()
    vec = vectorizer.transform([preprocess_text(ticket)])
    probs = model.predict_proba(vec)[0]
    order = probs.argsort()[::-1]
    top = [{"category": str(model.classes_[i]), "pct": round(float(probs[i]) * 100, 1)} for i in order[:3]]

    sev = analyze_severity(ticket)            # raw text (preprocess.py removes words like "high")
    imp = analyze_impact(ticket)
    return {"category": top[0]["category"], "confidence": top[0]["pct"], "top_categories": top,
            "severity": sev["level"], "severity_score": sev["score"], "indicators": sev["indicators"],
            "business_impact": imp["level"], "impact_indicators": imp["indicators"],
            "priority": calculate_priority(sev["level"], imp["level"])}
