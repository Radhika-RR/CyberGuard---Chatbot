# backend/app/utils/phishing_detector.py
import joblib
import numpy as np

class PhishingDetector:
    def __init__(self, model_path="../../phish_model.joblib", vec_path="../../vectorizer.joblib"):
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vec_path)
        self.feature_names = self.vectorizer.get_feature_names_out()

    def predict(self, text, top_n_features=5):
        X = self.vectorizer.transform([text])
        proba = float(self.model.predict_proba(X)[0][1])  # probability of '1' (phishing)
        label = "phishing" if proba >= 0.5 else "safe"

        # feature contribution
        coef = self.model.coef_[0]  # shape (n_features,)
        xarr = X.toarray()[0]
        contrib = xarr * coef
        # pick top positive contributions (most evidence for phishing)
        idx = np.argsort(-contrib)[:top_n_features]
        top_features = [
            {"feature": self.feature_names[i], "value": float(xarr[i]), "contribution": float(contrib[i])}
            for i in idx if xarr[i] > 0
        ]
        return {"label": label, "probability": proba, "features": top_features}
