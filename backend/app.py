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

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "server error"}), 500

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "bds_boycotts.csv"

try:
    df = pd.read_csv(CSV_PATH, encoding='latin1').fillna("")
except FileNotFoundError:
    print(f"FATAL ERROR: The file 'bds_boycotts.csv' was not found in the 'data' folder.")
    df = pd.DataFrame()

if not df.empty:
    df.columns = [c.strip() for c in df.columns]
    month_map = {name: i for i, name in enumerate(calendar.month_name) if name}
    df["Month"] = df["Month"].apply(lambda x: month_map.get(str(x).strip().title()))
    def clean_ticker(ticker):
        if not ticker or pd.isna(ticker): return ""
        return re.split(r'[\\s(,]', str(ticker).strip())[0]
    df["Ticker"] = df["Ticker"].apply(clean_ticker)
    ROWS = df.to_dict(orient="records")
else:
    ROWS = []

# --- Helper and other routes remain the same ---

def filter_rows(query: str):
    if not query: return ROWS
    q = query.lower()
    return [r for r in ROWS if q in str(r.get("Company", "")).lower() or q in str(r.get("Description", "")).lower()]

@app.get("/api/companies")
def companies():
    query = request.args.get("query", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 5, type=int), 50)
    results = filter_rows(query)
    total = len(results)
    start = (page - 1) * per_page
    items = results[start:start + per_page]
    def map_item(r):
        return { "name": r.get("Company", ""), "description": r.get("Description", ""), "source": r.get("Source", ""), "link": r.get("Link", ""), "month": r.get("Month", ""), "year": r.get("Year", ""), "ticker": r.get("Ticker", "") }
    return jsonify({ "results": [map_item(r) for r in items], "pagination": { "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page } })

@app.get("/api/suggestions")
def suggestions():
    q = request.args.get("q", "", type=str).strip().lower()
    all_names = [str(r.get("Company","")) for r in ROWS if str(r.get("Company","")).strip()]
    if not q:
        names = list(dict.fromkeys(all_names))[:10]
    else:
        names = list(dict.fromkeys([name for name in all_names if q in name.lower()]))[:10]
    return jsonify(names)

# --- NEW: Robust matching function ---
def find_company_by_name(name_to_find):
    """Finds a company using exact, partial, and then fuzzy matching."""
    decoded_name = unquote_plus(name_to_find).strip().lower()
    
    # 1. Try exact match first
    for row in ROWS:
        if str(row.get("Company", "")).strip().lower() == decoded_name:
            return row

    # 2. Try partial (substring) match
    for row in ROWS:
        if decoded_name in str(row.get("Company", "")).strip().lower():
            return row
            
    # 3. Fallback to fuzzy match
    all_company_names = [str(r.get("Company", "")).strip() for r in ROWS]
    matches = difflib.get_close_matches(decoded_name, all_company_names, n=1, cutoff=0.7)
    if matches:
        best_match_name = matches[0]
        return next((c for c in ROWS if str(c.get("Company", "")).strip() == best_match_name), None)

    return None

# --- UPDATED COMPANY DETAIL ROUTE ---
@app.get("/api/company/<path:company_name>")
def get_company_detail(company_name):
    company_data = find_company_by_name(company_name)

    if not company_data:
        return jsonify({"error": f"Company '{unquote_plus(company_name)}' not found"}), 404
    
    month_num = company_data.get("Month")
    month_name = calendar.month_name[int(month_num)] if month_num and str(month_num).isdigit() else ""

    return jsonify({
        "name": company_data.get("Company", ""),
        "description": company_data.get("Description", ""),
        "source": company_data.get("Source", ""),
        "link": company_data.get("Link", ""),
        "month": month_name,
        "year": company_data.get("Year", ""),
        "ticker": company_data.get("Ticker", "")
    })

# --- UPDATED FINANCE ROUTE ---
@app.get("/api/company/<path:company_name>/finance")
def get_company_finance(company_name):
    company = find_company_by_name(company_name)
    
    if not company: return jsonify({"error": "Company not found for finance data"}), 404

    ticker_symbol = company.get("Ticker")
    if not ticker_symbol or pd.isna(ticker_symbol): return jsonify({"error": "Ticker symbol missing"}), 400
    try:
        month = int(company.get("Month"))
        year = int(company.get("Year"))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date"}), 400

    center_date = datetime.datetime(year, month, 1)
    start_date, end_date = center_date - relativedelta(months=6), center_date + relativedelta(months=6)
    
    ticker = yf.Ticker(ticker_symbol)
    stock_df = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d")).reset_index()

    if stock_df.empty:
        return jsonify({"error": f"No stock data found for ticker {ticker_symbol}"}), 404

    center_date_aware = pd.to_datetime(center_date).tz_localize(stock_df['Date'].dt.tz)

    before_stock = stock_df[stock_df['Date'] < center_date_aware]
    after_stock = stock_df[stock_df['Date'] >= center_date_aware]

    def calculate_trend(df):
        if len(df) < 2: return "N/A"
        return "increase" if df.iloc[-1]["Close"] > df.iloc[0]["Close"] else "decrease"

    revenue_data = []
    try:
        financials = ticker.quarterly_financials
        if not financials.empty and "Total Revenue" in financials.index:
            revenue_series = financials.loc["Total Revenue"].dropna().sort_index()
            revenue_df = revenue_series.reset_index()
            revenue_df.columns = ["Date", "Revenue"]
            revenue_df["Date"] = pd.to_datetime(revenue_df["Date"])
            revenue_df = revenue_df[(revenue_df["Date"] >= start_date) & (revenue_df["Date"] <= end_date)]
            revenue_data = revenue_df.to_dict(orient="records")
    except Exception as e:
        print(f"Could not fetch revenue for {ticker_symbol}: {e}")

    return jsonify({
        "before_stock_data": before_stock.to_dict(orient="records"),
        "after_stock_data": after_stock.to_dict(orient="records"),
        "before_trend": calculate_trend(before_stock),
        "after_trend": calculate_trend(after_stock),
        "revenue_data": revenue_data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
