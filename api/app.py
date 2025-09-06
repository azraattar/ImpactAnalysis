# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from pathlib import Path
import yfinance as yf
from dateutil.relativedelta import relativedelta
import datetime
import calendar
import re
import difflib
from urllib.parse import unquote_plus
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# --- Start of New Debugging Code ---

print("--- STARTING FLASK SERVER ---")

# Determine the environment
is_vercel = 'VERCEL' in os.environ
print(f"--- Is this a Vercel environment? {is_vercel} ---")

if is_vercel:
    # Path for Vercel deployment
    BASE_DIR = Path.cwd()
    CSV_PATH = BASE_DIR / "api" / "data" / "bds_boycotts.csv"
else:
    # Path for local development
    BASE_DIR = Path(__file__).resolve().parent
    CSV_PATH = BASE_DIR / "data" / "bds_boycotts.csv"

# Print the exact path being used
print(f"--- Attempting to load data from: {CSV_PATH} ---")

# Check if the file actually exists at that path
if not CSV_PATH.is_file():
    print("--- FATAL ERROR: FILE DOES NOT EXIST AT THIS PATH ---")
    print("--- Please check your folder structure. The 'data' folder and its contents should be inside the 'api' folder. ---")
    df = pd.DataFrame() # Create empty DataFrame to prevent crash
else:
    try:
        df = pd.read_csv(CSV_PATH, encoding='latin1').fillna("")
        print(f"--- SUCCESS: Loaded {len(df)} rows from CSV file. ---")
    except Exception as e:
        print(f"--- FATAL ERROR: File exists, but failed to read. Error: {e} ---")
        df = pd.DataFrame()

# Process the DataFrame
if not df.empty:
    df.columns = [c.strip() for c in df.columns]
    month_map = {name: i for i, name in enumerate(calendar.month_name) if name}
    df["Month"] = df["Month"].apply(lambda x: month_map.get(str(x).strip().title()))
    def clean_ticker(ticker):
        if not ticker or pd.isna(ticker): return ""
        # Use a raw string r'' to avoid issues with backslashes
        return re.split(r'[\s(,]', str(ticker).strip())[0]
    df["Ticker"] = df["Ticker"].apply(clean_ticker)
    ROWS = df.to_dict(orient="records")
else:
    ROWS = []
    print("--- INFO: The 'ROWS' list is empty because no data was loaded. ---")

# --- End of New Debugging Code ---

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not found"}), 404

# ... (The rest of your routes and functions remain the same) ...
