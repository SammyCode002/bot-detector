"""
predict.py - Load the trained model and make predictions.

Used by the Flask app to classify accounts in real-time.
"""

import os
import json
import pickle
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "bot_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")
META_PATH = os.path.join(BASE_DIR, "model", "model_meta.json")

# Load once at import time
_model = None
_scaler = None
_meta = None


def _load():
    """Lazy-load the model, scaler, and metadata."""
    global _model, _scaler, _meta
    if _model is None:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        with open(SCALER_PATH, "rb") as f:
            _scaler = pickle.load(f)
        with open(META_PATH, "r") as f:
            _meta = json.load(f)


def get_meta() -> dict:
    """Get model metadata (accuracy, feature importance, etc.)."""
    _load()
    return _meta


def predict(features: dict) -> dict:
    """
    Predict whether an account is a bot.
    
    Args:
        features: Dict with feature names as keys
        
    Returns:
        Dict with prediction, confidence, and feature analysis
    """
    _load()

    # Build feature vector in the correct order
    feature_cols = _meta["feature_columns"]
    feature_labels = _meta["feature_labels"]

    X = np.array([[features.get(col, 0) for col in feature_cols]])
    X_scaled = _scaler.transform(X)

    # Predict
    prediction = int(_model.predict(X_scaled)[0])
    probabilities = _model.predict_proba(X_scaled)[0]
    confidence = float(max(probabilities))
    bot_probability = float(probabilities[1])

    # Feature contribution analysis
    # Use the model's feature importances weighted by how extreme each value is
    importances = _meta["feature_importance"]
    contributions = []

    for col in feature_cols:
        imp = importances.get(col, 0)
        val = features.get(col, 0)
        label = feature_labels.get(col, col)

        # Flag features that strongly indicate bot behavior
        flag = None
        if col == "tweets_per_day" and val > 50:
            flag = "Extremely high posting rate"
        elif col == "follower_following_ratio" and val < 0.1:
            flag = "Very few followers relative to following"
        elif col == "account_age_days" and val < 30:
            flag = "Very new account"
        elif col == "username_digit_ratio" and val > 0.4:
            flag = "Many digits in username"
        elif col == "has_profile_image" and val == 0:
            flag = "No profile image"
        elif col == "has_bio" and val == 0:
            flag = "No bio"
        elif col == "retweet_ratio" and val > 0.7:
            flag = "Mostly retweets, little original content"
        elif col == "avg_tweets_per_hour_variance" and val < 2.0:
            flag = "Very uniform posting pattern (likely automated)"
        elif col == "has_default_profile" and val == 1:
            flag = "Default profile (no customization)"
        elif col == "unique_sources_count" and val <= 1:
            flag = "Only one posting source"

        contributions.append({
            "feature": col,
            "label": label,
            "value": val,
            "importance": imp,
            "flag": flag,
        })

    # Sort by importance
    contributions.sort(key=lambda x: x["importance"], reverse=True)

    # Get the top flags (features that actually triggered)
    flags = [c for c in contributions if c["flag"] is not None]

    return {
        "prediction": "bot" if prediction == 1 else "human",
        "is_bot": prediction == 1,
        "confidence": round(confidence * 100, 1),
        "bot_probability": round(bot_probability * 100, 1),
        "human_probability": round((1 - bot_probability) * 100, 1),
        "flags": flags[:5],  # Top 5 red flags
        "top_features": contributions[:8],  # Top 8 features by importance
    }


# Quick test
if __name__ == "__main__":
    # Test with an obvious bot
    bot_result = predict({
        "account_age_days": 15,
        "followers_count": 3,
        "following_count": 2000,
        "follower_following_ratio": 0.0015,
        "total_tweets": 10000,
        "tweets_per_day": 666,
        "has_profile_image": 0,
        "has_bio": 0,
        "bio_length": 0,
        "has_url": 1,
        "username_length": 18,
        "username_digit_ratio": 0.6,
        "has_default_profile": 1,
        "listed_count": 0,
        "favorites_count": 5,
        "favorites_per_day": 0.3,
        "retweet_ratio": 0.9,
        "avg_tweets_per_hour_variance": 0.5,
        "unique_sources_count": 1,
        "is_verified": 0,
    })
    print(f"Bot test: {bot_result['prediction']} ({bot_result['confidence']}% confident)")
    print(f"Flags: {[f['flag'] for f in bot_result['flags']]}")

    # Test with a normal human
    human_result = predict({
        "account_age_days": 2000,
        "followers_count": 500,
        "following_count": 300,
        "follower_following_ratio": 1.67,
        "total_tweets": 3000,
        "tweets_per_day": 1.5,
        "has_profile_image": 1,
        "has_bio": 1,
        "bio_length": 120,
        "has_url": 1,
        "username_length": 10,
        "username_digit_ratio": 0.1,
        "has_default_profile": 0,
        "listed_count": 8,
        "favorites_count": 5000,
        "favorites_per_day": 2.5,
        "retweet_ratio": 0.2,
        "avg_tweets_per_hour_variance": 8.0,
        "unique_sources_count": 3,
        "is_verified": 0,
    })
    print(f"\nHuman test: {human_result['prediction']} ({human_result['confidence']}% confident)")
    print(f"Flags: {[f['flag'] for f in human_result['flags']]}")
