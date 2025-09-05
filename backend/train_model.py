import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
from loguru import logger
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    logger.warning("Could not download NLTK data")

class PhishingModelTrainer:
    def __init__(self):
        self.model = None
        self.stop_words = None
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()
    
    def preprocess_text(self, text):
        """Clean and preprocess text for training"""
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs, emails, and special characters
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', text)
        text = re.sub(r'\S+@\S+', ' ', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove stopwords (optional - sometimes helpful for phishing detection)
        try:
            tokens = word_tokenize(text)
            tokens = [word for word in tokens if word not in self.stop_words and len(word) > 2]
            text = ' '.join(tokens)
        except:
            pass
        
        return text
    
    def load_data(self, data_path):
        """Load and preprocess training data"""
        logger.info(f"Loading data from {data_path}")
        
        # Check if file exists
        if not os.path.exists(data_path):
            logger.error(f"Data file not found: {data_path}")
            # Create sample data for demonstration
            logger.info("Creating sample phishing dataset...")
            sample_data = self.create_sample_data()
            sample_data.to_csv(data_path, index=False)
            logger.info(f"Sample data saved to {data_path}")
        
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} samples")
        
        # Validate data format
        required_columns = ['text', 'label']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Data must contain columns: {required_columns}")
            raise ValueError(f"Missing required columns in data")
        
        # Clean data
        df = df.dropna()
        df['text'] = df['text'].apply(self.preprocess_text)
        df = df[df['text'].str.len() > 0]  # Remove empty texts
        
        logger.info(f"After cleaning: {len(df)} samples")
        logger.info(f"Label distribution:\n{df['label'].value_counts()}")
        
        return df
    
    def create_sample_data(self):
        """Create sample phishing dataset for demonstration"""
        phishing_samples = [
            "Urgent! Your account will be suspended. Click here immediately to verify: suspicious-bank.com/verify",
            "Congratulations! You've won $10000. Send your SSN to claim prize now!",
            "Your PayPal account has been limited. Update your information at paypaI-security.com",
            "FINAL NOTICE: Your package is held. Pay $2.99 fee at fake-shipping.net",
            "IRS: You owe taxes. Pay immediately or face legal action at irs-payment.org",
            "Bank Alert: Suspicious activity detected. Confirm identity at bank-secure.net",
            "Your subscription expires today! Renew at discounted-netflix.com",
            "Click to claim your free iPhone! Limited time offer at apple-giveaway.net",
            "Verify your email immediately or lose access: gmail-verification.org",
            "Your credit card has been charged $500. Dispute at credit-dispute.com"
        ]
        
        legitimate_samples = [
            "Thank you for your purchase. Your order #12345 will arrive in 3-5 business days.",
            "Your monthly bank statement is now available in your online banking portal.",
            "Reminder: Your appointment with Dr. Smith is scheduled for tomorrow at 2 PM.",
            "Your subscription to our newsletter has been confirmed. Welcome!",
            "Your password was successfully changed. If this wasn't you, please contact us.",
            "Thank you for attending our webinar. The recording will be available soon.",
            "Your package from Amazon has been delivered to your front door.",
            "Your flight check-in is now available. Check in online to save time.",
            "Your utility bill for this month is $85.50. Pay by the 15th to avoid late fees.",
            "Welcome to our platform! Please verify your email address to get started."
        ]
        
        data = []
        
        # Add phishing samples
        for text in phishing_samples:
            data.append({'text': text, 'label': 1})
        
        # Add legitimate samples
        for text in legitimate_samples:
            data.append({'text': text, 'label': 0})
        
        # Add more varied samples to improve model
        additional_phishing = [
            "Act now! Limited time offer expires soon. Click here for amazing deals!",
            "Your account security is compromised. Update credentials immediately.",
            "Free money waiting for you! No catch, just click and claim.",
            "URGENT: Verify your identity to prevent account closure.",
            "You have been selected for a special promotion. Act fast!"
        ]
        
        additional_legitimate = [
            "Your order has been processed and will ship within 24 hours.",
            "Thank you for your feedback. We appreciate your business.",
            "Your appointment has been confirmed for next Tuesday.",
            "Welcome to our community! Here are some helpful resources.",
            "Your monthly report is ready for download in your dashboard."
        ]
        
        for text in additional_phishing:
            data.append({'text': text, 'label': 1})
        
        for text in additional_legitimate:
            data.append({'text': text, 'label': 0})
        
        return pd.DataFrame(data)
    
    def create_pipeline(self):
        """Create ML pipeline with TF-IDF + Logistic Regression"""
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),  # Use both unigrams and bigrams
                min_df=2,            # Ignore terms that appear in less than 2 documents
                max_df=0.95,         # Ignore terms that appear in more than 95% of documents
                stop_words='english'
            )),
            ('classifier', LogisticRegression(
                random_state=42,
                max_iter=1000,
                class_weight='balanced'  # Handle class imbalance
            ))
        ])
        return pipeline
    
    def train_model(self, data_path, model_save_path):
        """Train the phishing detection model"""
        # Load data
        df = self.load_data(data_path)
        
        X = df['text']
        y = df['label']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Create and train pipeline
        self.model = self.create_pipeline()
        
        logger.info("Training model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        logger.info("Evaluating model...")
        
        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Test Accuracy: {accuracy:.4f}")
        
        # Classification report
        logger.info("Classification Report:")
        logger.info(f"\n{classification_report(y_test, y_pred)}")
        
        # Confusion matrix
        logger.info("Confusion Matrix:")
        logger.info(f"\n{confusion_matrix(y_test, y_pred)}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='accuracy')
        logger.info(f"Cross-validation scores: {cv_scores}")
        logger.info(f"CV Mean accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Save model
        logger.info(f"Saving model to {model_save_path}")
        joblib.dump(self.model, model_save_path)
        
        # Test with sample predictions
        self.test_sample_predictions()
        
        return self.model
    
    def test_sample_predictions(self):
        """Test model with sample inputs"""
        test_samples = [
            "Your account will be suspended unless you verify immediately",
            "Thank you for your order, it will be delivered soon",
            "Click here to claim your free prize now!",
            "Your meeting is scheduled for tomorrow at 3 PM"
        ]
        
        logger.info("\nSample Predictions:")
        for sample in test_samples:
            prediction = self.model.predict([sample])[0]
            probability = self.model.predict_proba([sample])[0]
            
            label = "PHISHING" if prediction == 1 else "LEGITIMATE"
            confidence = max(probability)
            
            logger.info(f"Text: '{sample[:50]}...'")
            logger.info(f"Prediction: {label} (confidence: {confidence:.3f})")
            logger.info("---")

def main():
    """Main training function"""
    logger.info("Starting phishing detection model training...")
    
    # Paths
    data_path = "data/phishing_data.csv"
    model_save_path = "models/phish_model.joblib"
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    
    # Initialize trainer and train model
    trainer = PhishingModelTrainer()
    model = trainer.train_model(data_path, model_save_path)
    
    logger.info("Training completed successfully!")
    logger.info(f"Model saved to: {model_save_path}")

if __name__ == "__main__":
    main()