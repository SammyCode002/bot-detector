"""
run.py - Start the Bot Detector web app from the project root.

Usage:
    py run.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.app import app

if __name__ == "__main__":
    print("Bot Detector running at http://localhost:5000")
    app.run(debug=True, port=5000)
