"""Work 4 - AI Ticket Classification
Ticket text -> TF-IDF -> Numerical features -> Logistic Regression -> Category
Input : tickets_clean.csv  (made by clean_data.py; uses 'clean_ticket' + 'category')
Output: models/ticket_classifier.joblib, models/tfidf_vectorizer.joblib, report + confusion matrix
"""
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

import config


def main():
    df = pd.read_csv(config.CLEAN_DATA_PATH).dropna(subset=["clean_ticket", "category"])
    print("Loaded:", df.shape)
    print("\nCategory distribution:\n", df["category"].value_counts())

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_ticket"], df["category"], test_size=0.2, random_state=42, stratify=df["category"])

    # TF-IDF: converts text to numerical features (unigrams + bigrams)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=50000, min_df=2, sublinear_tf=True)
    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=2000, C=5)
    model.fit(Xtr, y_train)

    pred = model.predict(Xte)
    acc = accuracy_score(y_test, pred)
    macro_f1 = f1_score(y_test, pred, average="macro")
    report = classification_report(y_test, pred)
    print(f"\nAccuracy : {acc:.4f}\nMacro F1 : {macro_f1:.4f}\n\n{report}")

    config.MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(vectorizer, config.VECTORIZER_PATH)
    joblib.dump(model, config.MODEL_PATH)
    config.REPORT_PATH.write_text(f"Accuracy: {acc:.4f}\nMacro F1: {macro_f1:.4f}\n\n{report}")

    # Confusion matrix image (for your report / demo)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        labels = sorted(df["category"].unique())
        cm = confusion_matrix(y_test, pred, labels=labels)
        fig, ax = plt.subplots(figsize=(8, 7))
        ax.imshow(cm, cmap="Blues")
        ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
        ax.set_yticks(range(len(labels)), labels)
        for i in range(len(labels)):
            for j in range(len(labels)):
                ax.text(j, i, cm[i, j], ha="center", va="center",
                        color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=8)
        ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.set_title("Confusion Matrix")
        fig.tight_layout(); fig.savefig(config.CONFUSION_PATH, dpi=150)
        print("Saved confusion matrix:", config.CONFUSION_PATH)
    except ImportError:
        print("matplotlib not installed - skipped confusion matrix image")

    print("Saved model + vectorizer to", config.MODEL_DIR)


if __name__ == "__main__":
    main()
