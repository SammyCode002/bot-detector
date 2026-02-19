"""
generate_dataset.py - Creates a realistic synthetic dataset for bot detection.

Based on statistical patterns from real Twitter/X bot research:
- Bot accounts tend to have: high tweet frequency, low follower ratios,
  newer accounts, less profile info, more uniform posting patterns
- Human accounts tend to have: organic follower growth, varied posting,
  complete profiles, natural username patterns

This generates labeled data for training a classifier.
"""

import csv
import random
import string
import os
from datetime import datetime, timedelta

random.seed(42)  # Reproducible results

NUM_HUMANS = 3000
NUM_BOTS = 2000
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "dataset.csv")

# Feature columns
HEADERS = [
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
    "label",  # 0 = human, 1 = bot
]


def generate_human():
    """Generate a realistic human account profile."""
    age = random.randint(60, 5000)
    followers = max(0, int(random.gauss(500, 800)))
    following = max(1, int(random.gauss(350, 400)))
    ratio = round(followers / max(following, 1), 4)
    total_tweets = max(0, int(random.gauss(2000, 3000)))
    tpd = round(total_tweets / max(age, 1), 4)
    has_pfp = 1 if random.random() < 0.92 else 0
    has_bio = 1 if random.random() < 0.85 else 0
    bio_len = random.randint(20, 160) if has_bio else 0
    has_url = 1 if random.random() < 0.45 else 0
    uname_len = random.randint(4, 15)
    uname_digits = round(random.uniform(0, 0.3), 4)
    default_profile = 1 if random.random() < 0.08 else 0
    listed = max(0, int(random.gauss(5, 15)))
    favorites = max(0, int(random.gauss(3000, 5000)))
    fpd = round(favorites / max(age, 1), 4)
    rt_ratio = round(random.uniform(0.05, 0.5), 4)
    hour_var = round(random.uniform(2.0, 15.0), 4)
    sources = random.randint(1, 5)
    verified = 1 if random.random() < 0.03 else 0

    return [
        age, followers, following, ratio, total_tweets, tpd,
        has_pfp, has_bio, bio_len, has_url, uname_len, uname_digits,
        default_profile, listed, favorites, fpd, rt_ratio, hour_var,
        sources, verified, 0,
    ]


def generate_bot():
    """Generate a realistic bot account profile."""
    # Bots come in different flavors
    bot_type = random.choice(["spam", "follower_farm", "content_bot", "sophisticated"])

    if bot_type == "spam":
        age = random.randint(1, 200)
        followers = random.randint(0, 50)
        following = random.randint(500, 5000)
        total_tweets = random.randint(500, 50000)
        has_pfp = 1 if random.random() < 0.4 else 0
        has_bio = 1 if random.random() < 0.2 else 0
        bio_len = random.randint(0, 30) if has_bio else 0
        has_url = 1 if random.random() < 0.7 else 0
        uname_digits = round(random.uniform(0.3, 0.8), 4)
        default_profile = 1 if random.random() < 0.6 else 0
        rt_ratio = round(random.uniform(0.6, 0.95), 4)
        hour_var = round(random.uniform(0.1, 1.5), 4)
        sources = 1
        favorites = random.randint(0, 100)

    elif bot_type == "follower_farm":
        age = random.randint(30, 1000)
        followers = random.randint(0, 20)
        following = random.randint(1000, 7500)
        total_tweets = random.randint(0, 200)
        has_pfp = 1 if random.random() < 0.5 else 0
        has_bio = 1 if random.random() < 0.3 else 0
        bio_len = random.randint(0, 50) if has_bio else 0
        has_url = 0
        uname_digits = round(random.uniform(0.2, 0.7), 4)
        default_profile = 1 if random.random() < 0.7 else 0
        rt_ratio = round(random.uniform(0.0, 0.3), 4)
        hour_var = round(random.uniform(0.0, 2.0), 4)
        sources = 1
        favorites = random.randint(0, 50)

    elif bot_type == "content_bot":
        age = random.randint(30, 800)
        followers = random.randint(100, 5000)
        following = random.randint(50, 500)
        total_tweets = random.randint(5000, 100000)
        has_pfp = 1 if random.random() < 0.7 else 0
        has_bio = 1 if random.random() < 0.6 else 0
        bio_len = random.randint(10, 80) if has_bio else 0
        has_url = 1 if random.random() < 0.5 else 0
        uname_digits = round(random.uniform(0.1, 0.5), 4)
        default_profile = 1 if random.random() < 0.3 else 0
        rt_ratio = round(random.uniform(0.7, 1.0), 4)
        hour_var = round(random.uniform(0.2, 2.0), 4)
        sources = random.randint(1, 2)
        favorites = random.randint(0, 500)

    else:  # sophisticated
        age = random.randint(100, 2000)
        followers = random.randint(200, 3000)
        following = random.randint(200, 2000)
        total_tweets = random.randint(1000, 20000)
        has_pfp = 1 if random.random() < 0.85 else 0
        has_bio = 1 if random.random() < 0.7 else 0
        bio_len = random.randint(20, 120) if has_bio else 0
        has_url = 1 if random.random() < 0.3 else 0
        uname_digits = round(random.uniform(0.05, 0.4), 4)
        default_profile = 1 if random.random() < 0.15 else 0
        rt_ratio = round(random.uniform(0.3, 0.7), 4)
        hour_var = round(random.uniform(0.5, 4.0), 4)
        sources = random.randint(1, 3)
        favorites = random.randint(100, 3000)

    ratio = round(followers / max(following, 1), 4)
    tpd = round(total_tweets / max(age, 1), 4)
    uname_len = random.randint(5, 20)
    listed = max(0, int(random.gauss(1, 3)))
    fpd = round(favorites / max(age, 1), 4)
    verified = 0

    return [
        age, followers, following, ratio, total_tweets, tpd,
        has_pfp, has_bio, bio_len, has_url, uname_len, uname_digits,
        default_profile, listed, favorites, fpd, rt_ratio, hour_var,
        sources, verified, 1,
    ]


def main():
    rows = []

    print(f"Generating {NUM_HUMANS} human profiles...")
    for _ in range(NUM_HUMANS):
        rows.append(generate_human())

    print(f"Generating {NUM_BOTS} bot profiles...")
    for _ in range(NUM_BOTS):
        rows.append(generate_bot())

    # Shuffle
    random.shuffle(rows)

    # Write CSV
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(rows)

    print(f"Dataset saved to {OUTPUT_PATH}")
    print(f"Total: {len(rows)} rows ({NUM_HUMANS} human, {NUM_BOTS} bot)")

    # Quick stats
    bots = [r for r in rows if r[-1] == 1]
    humans = [r for r in rows if r[-1] == 0]
    print(f"\nSample stats:")
    print(f"  Avg human followers: {sum(r[1] for r in humans) / len(humans):.0f}")
    print(f"  Avg bot followers:   {sum(r[1] for r in bots) / len(bots):.0f}")
    print(f"  Avg human tweets/day: {sum(r[5] for r in humans) / len(humans):.2f}")
    print(f"  Avg bot tweets/day:   {sum(r[5] for r in bots) / len(bots):.2f}")


if __name__ == "__main__":
    main()
