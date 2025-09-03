# backend/train_model.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

DATA_PATH = os.path.join("data", "phishing_data.csv")
MODEL_OUT = os.path.join("models", "phish_model.joblib")
os.makedirs("models", exist_ok=True)

def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    df = df.dropna(subset=["text", "label"])
    return df

def train():
    df = load_data()
    X = df["text"].astype(str)
    y = df["label"].map(lambda x: 1 if str(x).lower() in ["phish","phishing","1","true","yes"] else 0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,3), max_features=20000)),
        ("clf", LogisticRegression(max_iter=1000))
    ])
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))
    joblib.dump(pipeline, MODEL_OUT)
    print("Saved model to", MODEL_OUT)

if __name__ == "__main__":
    train()
