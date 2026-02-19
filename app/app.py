"""
app.py - Flask web server for the bot detector.

Routes:
  GET  /           → Main dashboard page
  POST /api/predict → Analyze an account and return prediction
  GET  /api/meta   → Model metadata (accuracy, features, etc.)
"""

import os
import sys

# Add project root to path so model imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, request, jsonify
from model.predict import predict, get_meta

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main dashboard."""
    meta = get_meta()
    return render_template("index.html", meta=meta)


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Analyze an account and return bot prediction.
    
    Expects JSON with feature values. Computes derived features
    automatically where possible.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Compute derived features from raw inputs
        account_age = max(int(data.get("account_age_days", 1)), 1)
        followers = max(int(data.get("followers_count", 0)), 0)
        following = max(int(data.get("following_count", 0)), 1)
        total_tweets = max(int(data.get("total_tweets", 0)), 0)
        favorites = max(int(data.get("favorites_count", 0)), 0)
        username = data.get("username", "")

        # Auto-compute derived features
        features = {
            "account_age_days": account_age,
            "followers_count": followers,
            "following_count": following,
            "follower_following_ratio": round(followers / following, 4),
            "total_tweets": total_tweets,
            "tweets_per_day": round(total_tweets / account_age, 4),
            "has_profile_image": int(data.get("has_profile_image", 1)),
            "has_bio": int(data.get("has_bio", 1)),
            "bio_length": int(data.get("bio_length", 50)),
            "has_url": int(data.get("has_url", 0)),
            "username_length": len(username) if username else int(data.get("username_length", 10)),
            "username_digit_ratio": _digit_ratio(username) if username else float(data.get("username_digit_ratio", 0.1)),
            "has_default_profile": int(data.get("has_default_profile", 0)),
            "listed_count": int(data.get("listed_count", 0)),
            "favorites_count": favorites,
            "favorites_per_day": round(favorites / account_age, 4),
            "retweet_ratio": float(data.get("retweet_ratio", 0.3)),
            "avg_tweets_per_hour_variance": float(data.get("avg_tweets_per_hour_variance", 5.0)),
            "unique_sources_count": int(data.get("unique_sources_count", 2)),
            "is_verified": int(data.get("is_verified", 0)),
        }

        result = predict(features)
        result["input_features"] = features
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/meta", methods=["GET"])
def api_meta():
    """Return model metadata."""
    return jsonify(get_meta())


def _digit_ratio(username: str) -> float:
    """Calculate the ratio of digits in a username."""
    if not username:
        return 0.0
    digits = sum(1 for c in username if c.isdigit())
    return round(digits / len(username), 4)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
