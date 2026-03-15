# 🛡 Bot Detector — AI-Powered Social Media Account Analysis

A machine learning web app that analyzes social media account features to determine whether an account is a bot or a real human. Uses a Random Forest classifier trained on 20 behavioral features.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)
![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3+-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **Random Forest classifier** trained on 5,000 labeled accounts (99.8% accuracy)
- **20 behavioral features** including posting patterns, follower ratios, and profile completeness
- **Real-time analysis** via a Flask web interface
- **Confidence gauge** showing bot vs human probability
- **Red flag detection** highlighting suspicious patterns
- **Feature importance breakdown** showing what the model cares about most
- **Preset profiles** to test known bot patterns (spam, follower farm)
- **Simple/Advanced mode** toggle for different detail levels

## Quick Start

```bash
# Clone the repo
git clone https://github.com/SammyCode002/bot-detector.git
cd bot-detector

# Install dependencies
pip install -r requirements.txt

# Generate training data & train the model
py data/generate_dataset.py
py model/train.py

# Run the web app
py run.py
```

Open **http://localhost:5000** in your browser.

## How It Works

### The Model

The classifier analyzes 20 features that distinguish bot behavior from human behavior:

| Feature | Why It Matters |
|---------|---------------|
| Posting Time Variance | Bots post at uniform intervals; humans are irregular |
| Retweet Ratio | Bots often retweet heavily with little original content |
| Username Digit Ratio | Bot usernames often have many random digits |
| Follower/Following Ratio | Bots follow many but have few followers |
| Account Age | Many bots are recently created |
| Tweets Per Day | Some bots post hundreds of times daily |
| Profile Completeness | Bots often skip profile images, bios, URLs |
| Unique Posting Sources | Bots typically use one automated source |

### Bot Types Detected

The training data includes four distinct bot archetypes:

- **Spam bots** — New accounts, extreme posting rates, high retweet ratios
- **Follower farms** — Follow thousands, produce almost no content
- **Content bots** — Automated reposting at inhuman volume
- **Sophisticated bots** — Mimic human patterns but slip on posting regularity

### Training Pipeline

```
Raw Data (5,000 accounts)
    │
    ▼
Feature Engineering (20 features)
    │
    ▼
Train/Test Split (80/20, stratified)
    │
    ▼
StandardScaler (normalize features)
    │
    ▼
Random Forest (200 trees, max_depth=15)
    │
    ▼
Evaluation: 99.8% accuracy, 0.997 F1, 1.0 AUC-ROC
```

## Project Structure

```
bot-detector/
├── app/
│   ├── app.py               # Flask routes
│   ├── templates/
│   │   └── index.html        # Dashboard UI
│   └── static/
│       ├── css/style.css     # Styles
│       └── js/app.js         # Frontend logic
├── model/
│   ├── train.py              # Model training
│   ├── predict.py            # Inference module
│   ├── bot_model.pkl         # Trained model
│   ├── scaler.pkl            # Feature scaler
│   └── model_meta.json       # Metadata & metrics
├── data/
│   ├── generate_dataset.py   # Synthetic data generator
│   └── dataset.csv           # Training data
├── requirements.txt
└── README.md
```

## Model Performance

| Metric | Score |
|--------|-------|
| Accuracy | 99.8% |
| F1 Score | 99.7% |
| AUC-ROC | 1.000 |
| Cross-Val F1 (5-fold) | 99.7% ± 0.8% |

### Top Feature Importances

1. Posting Time Variance (30.0%)
2. Retweet Ratio (14.0%)
3. Username Digit Ratio (13.4%)
4. Total Tweets (8.9%)
5. Following Count (7.8%)

## Honest Limitations

- **Synthetic training data** — Based on statistical patterns from real research, but not actual Twitter data. Production systems use real labeled datasets.
- **No API integration** — You manually enter account features. A production tool would pull data from Twitter's API.
- **Binary classification** — Outputs "bot" or "human." Real-world detection benefits from probability thresholds and multi-class labels.
- **No adversarial resistance** — Sophisticated bots designed to evade detection could fool this model.

These are intentional scope boundaries for a portfolio project.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| ML Model | scikit-learn (Random Forest) |
| Web Framework | Flask |
| Frontend | Vanilla HTML/CSS/JS |
| Data Processing | pandas, NumPy |
| Language | Python 3.10+ |

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*Built as a Computer Science / Cybersecurity portfolio project.*
