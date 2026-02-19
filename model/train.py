"""
train.py - Train the bot detection model.

Uses Random Forest classifier on engineered features from social media
account metadata. Outputs a trained model file and feature importance rankings.

Why Random Forest?
- Handles mixed feature types (binary, continuous, ratios) naturally
- Built-in feature importance (great for explaining WHY something was flagged)
- Resistant to overfitting with proper hyperparameters
- Fast inference (important for real-time web app predictions)
- Easy to explain in interviews ("it's an ensemble of decision trees that vote")
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    roc_auc_score,
    f1_score,
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model", "bot_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")
META_PATH = os.path.join(BASE_DIR, "model", "model_meta.json")

# Features to use (excluding the label column)
FEATURE_COLUMNS = [
    "account_age_days",
    "followers_count",
    "following_count",
    "follower_following_ratio",
    "total_tweets",
    "tweets_per_day",
    "has_profile_image",
    "has_bio",
    "bio_length",
    "has_url",
    "username_length",
    "username_digit_ratio",
    "has_default_profile",
    "listed_count",
    "favorites_count",
    "favorites_per_day",
    "retweet_ratio",
    "avg_tweets_per_hour_variance",
    "unique_sources_count",
    "is_verified",
]

# Human-readable feature names for the web app
FEATURE_LABELS = {
    "account_age_days": "Account Age (days)",
    "followers_count": "Followers",
    "following_count": "Following",
    "follower_following_ratio": "Follower/Following Ratio",
    "total_tweets": "Total Tweets",
    "tweets_per_day": "Tweets per Day",
    "has_profile_image": "Has Profile Image",
    "has_bio": "Has Bio",
    "bio_length": "Bio Length",
    "has_url": "Has URL in Profile",
    "username_length": "Username Length",
    "username_digit_ratio": "Digits in Username (%)",
    "has_default_profile": "Default Profile",
    "listed_count": "Listed Count",
    "favorites_count": "Total Favorites",
    "favorites_per_day": "Favorites per Day",
    "retweet_ratio": "Retweet Ratio",
    "avg_tweets_per_hour_variance": "Posting Time Variance",
    "unique_sources_count": "Unique Posting Sources",
    "is_verified": "Verified Account",
}


def load_data():
    """Load and prepare the dataset."""
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"  Rows: {len(df)}")
    print(f"  Humans: {(df['label'] == 0).sum()}")
    print(f"  Bots: {(df['label'] == 1).sum()}")
    print(f"  Bot ratio: {(df['label'] == 1).mean():.1%}")
    return df


def train_model(df: pd.DataFrame):
    """Train the Random Forest model."""
    X = df[FEATURE_COLUMNS].values
    y = df["label"].values

    # Split: 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("\nTraining Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print(f"\n{'=' * 50}")
    print(f"MODEL EVALUATION")
    print(f"{'=' * 50}")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"  AUC-ROC:   {auc:.4f}")

    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Human", "Bot"]))

    print(f"Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  True Humans:  {cm[0][0]} correct, {cm[0][1]} false positive")
    print(f"  True Bots:    {cm[1][1]} correct, {cm[1][0]} false negative")

    # Cross-validation
    print(f"\n5-Fold Cross-Validation:")
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring="f1")
    print(f"  F1 scores: {cv_scores.round(4)}")
    print(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

    # Feature importance
    importances = model.feature_importances_
    feature_ranking = sorted(
        zip(FEATURE_COLUMNS, importances),
        key=lambda x: x[1],
        reverse=True,
    )

    print(f"\nFeature Importance (top 10):")
    for feat, imp in feature_ranking[:10]:
        label = FEATURE_LABELS.get(feat, feat)
        bar = "█" * int(imp * 100)
        print(f"  {label:<28} {imp:.4f}  {bar}")

    return model, scaler, {
        "accuracy": round(accuracy, 4),
        "f1_score": round(f1, 4),
        "auc_roc": round(auc, 4),
        "cv_f1_mean": round(cv_scores.mean(), 4),
        "cv_f1_std": round(cv_scores.std(), 4),
        "feature_importance": {
            feat: round(float(imp), 4) for feat, imp in feature_ranking
        },
        "feature_columns": FEATURE_COLUMNS,
        "feature_labels": FEATURE_LABELS,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
    }


def save_model(model, scaler, meta):
    """Save the trained model, scaler, and metadata."""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"\nModel saved to {MODEL_PATH}")

    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
    print(f"Scaler saved to {SCALER_PATH}")

    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Metadata saved to {META_PATH}")


def main():
    print("=" * 50)
    print("BOT DETECTOR - MODEL TRAINING")
    print("=" * 50)

    df = load_data()
    model, scaler, meta = train_model(df)
    save_model(model, scaler, meta)

    print(f"\n{'=' * 50}")
    print("TRAINING COMPLETE")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
