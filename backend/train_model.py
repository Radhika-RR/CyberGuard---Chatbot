# backend/train_model.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

df = pd.read_csv("phishing_data.csv")  # ensure columns: text,label
df = df.dropna(subset=["text", "label"])
X = df["text"].astype(str).values
y = df["label"].astype(int).values  # 1 phishing, 0 safe (adapt to your labels)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
X_train_tf = vectorizer.fit_transform(X_train)
X_test_tf = vectorizer.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_tf, y_train)

preds = model.predict(X_test_tf)
print(classification_report(y_test, preds))

joblib.dump(model, "phish_model.joblib")
joblib.dump(vectorizer, "vectorizer.joblib")
print("Saved phish_model.joblib and vectorizer.joblib")
