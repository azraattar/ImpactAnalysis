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
import unicodedata


# -------------------- Flask Setup --------------------
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


print("\n--- STARTING FLASK SERVER ---")


# -------------------- CSV Path Setup --------------------
is_vercel = 'VERCEL' in os.environ
BASE_DIR = Path.cwd() if is_vercel else Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "bds_boycotts.csv"
print(f"--- Loading CSV from: {CSV_PATH} ---")


# -------------------- Load CSV --------------------
if not CSV_PATH.is_file():
    print("--- FATAL ERROR: CSV file missing. ---")
    df = pd.DataFrame()
else:
    try:
        df = pd.read_csv(CSV_PATH, encoding='latin1').fillna("")
        print(f"--- Loaded {len(df)} rows ---")
    except Exception as e:
        print(f"--- Failed to read CSV: {e} ---")
        df = pd.DataFrame()


# -------------------- Process Data --------------------
if not df.empty:
    df.columns = [c.strip() for c in df.columns]
    month_map = {name: i for i, name in enumerate(calendar.month_name) if name}
    df["Month"] = df["Month"].apply(lambda x: month_map.get(str(x).strip().title()))
    df["Ticker"] = df["Ticker"].apply(lambda t: re.split(r'[\s(,]', str(t).strip())[0] if t else "")
    ROWS = df.to_dict(orient="records")
else:
    ROWS = []
    print("--- INFO: No data loaded ---")


# -------------------- Helper Functions --------------------
def normalize_text(s):
    if not s:
        return ""
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii').strip().lower()


def filter_rows(query):
    if not query:
        return ROWS
    q = normalize_text(query)
    return [r for r in ROWS if q in normalize_text(r.get("Company", ""))]


def find_company_by_name(name_to_find):
    decoded_name = unquote_plus(name_to_find).strip()
    decoded_name_norm = normalize_text(decoded_name)

    # Exact match
    for row in ROWS:
        if normalize_text(row.get("Company", "")) == decoded_name_norm:
            return row

    # Partial match
    for row in ROWS:
        if decoded_name_norm in normalize_text(row.get("Company", "")):
            return row

    # Fuzzy match
    all_names = [r.get("Company", "") for r in ROWS]
    matches = difflib.get_close_matches(decoded_name_norm, [normalize_text(n) for n in all_names], n=1, cutoff=0.7)
    if matches:
        best_match = matches[0]
        return next((r for r in ROWS if normalize_text(r.get("Company", "")) == best_match), None)

    return None


# -------------------- Routes --------------------


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
        month_num = r.get("Month")
        month_name = ""
        if month_num and str(month_num).isdigit() and 1 <= int(month_num) <= 12:
            month_name = calendar.month_name[int(month_num)]

        return {
            "name": r.get("Company", ""),
            "description": r.get("Description", ""),
            "source": r.get("Source", ""),
            "link": r.get("Link", ""),
            "month": month_name,
            "year": r.get("Year", ""),
            "ticker": r.get("Ticker", "")
        }

    return jsonify({
        "results": [map_item(r) for r in items],
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
    })


@app.get("/api/suggestions")
def suggestions():
    q = request.args.get("q", "", type=str).strip().lower()
    all_names = [str(r.get("Company", "")) for r in ROWS if r.get("Company", "")]
    if not q:
        names = list(dict.fromkeys(all_names))[:10]
    else:
        names = list(dict.fromkeys([n for n in all_names if q in n.lower()]))[:10]
    return jsonify(names)


@app.get("/api/company/<path:company_name>")
def get_company_detail(company_name):
    company = find_company_by_name(company_name)
    if not company:
        return jsonify({"error": f"Company '{unquote_plus(company_name)}' not found"}), 404

    month_num = company.get("Month")
    month_name = ""
    if month_num and str(month_num).isdigit() and 1 <= int(month_num) <= 12:
        month_name = calendar.month_name[int(month_num)]

    return jsonify({
        "name": company.get("Company", ""),
        "description": company.get("Description", ""),
        "source": company.get("Source", ""),
        "link": company.get("Link", ""),
        "month": month_name,
        "year": company.get("Year", ""),
        "ticker": company.get("Ticker", "")
    })


# app.py (Only the get_company_finance function is shown)

@app.get("/api/company/<path:company_name>/finance")
def get_company_finance(company_name):
    company = find_company_by_name(company_name)
    if not company:
        return jsonify({"error": "Company not found for finance data"}), 404

    ticker_symbol = company.get("Ticker")
    if not ticker_symbol:
        return jsonify({"error": "Ticker symbol missing"}), 400

    try:
        month = int(company.get("Month"))
        year = int(company.get("Year"))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid or missing date for company event"}), 400

    center_date = datetime.datetime(year, month, 1)
    start_date = center_date - relativedelta(months=6)
    end_date = center_date + relativedelta(months=6)

    try:
        ticker = yf.Ticker(ticker_symbol)
        stock_df = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d")).reset_index()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch data from yfinance for {ticker_symbol}. Error: {e}"}), 500

    if stock_df.empty:
        return jsonify({"error": f"No stock data found for ticker '{ticker_symbol}' in the specified date range."}), 404

    # This part works correctly for stock_df, as history is always tz-aware
    stock_df['Date'] = pd.to_datetime(stock_df['Date']).dt.tz_convert('UTC').dt.tz_localize(None)
    center_date_naive = pd.to_datetime(center_date)

    before_stock = stock_df[stock_df['Date'] < center_date_naive]
    after_stock = stock_df[stock_df['Date'] >= center_date_naive]

    def calculate_trend(df):
        if len(df) < 2: return "N/A"
        return "increase" if df.iloc[-1]["Close"] > df.iloc[0]["Close"] else "decrease"

    response = {
        "before_stock_data": before_stock.to_dict(orient="records"),
        "after_stock_data": after_stock.to_dict(orient="records"),
        "before_trend": calculate_trend(before_stock),
        "after_trend": calculate_trend(after_stock),
        "revenue_data": [],
        "errors": {}
    }

    try:
        fin = ticker.quarterly_financials
        if not fin.empty:
            if "Total Revenue" in fin.index:
                rev_series = fin.loc["Total Revenue"].dropna().sort_index()
                rev_df = rev_series.reset_index()
                rev_df.columns = ["Date", "Revenue"]
                
                # *** THE ONLY CHANGE NEEDED IS HERE ***
                # Make sure the 'Date' column is a datetime object
                rev_df['Date'] = pd.to_datetime(rev_df['Date'])

                # If the dates are timezone-naive, assign UTC timezone to them
                if rev_df['Date'].dt.tz is None:
                    rev_df['Date'] = rev_df['Date'].dt.tz_localize('UTC')

                # Now, safely convert to UTC and remove timezone for comparison
                rev_df['Date'] = rev_df['Date'].dt.tz_convert('UTC').dt.tz_localize(None)
                # *** END OF FIX ***

                start_date_naive = pd.to_datetime(start_date)
                end_date_naive = pd.to_datetime(end_date)
                
                rev_df = rev_df[(rev_df["Date"] >= start_date_naive) & (rev_df["Date"] <= end_date_naive)]
                
                if not rev_df.empty:
                    response["revenue_data"] = rev_df.to_dict(orient="records")
                else:
                    response["errors"]["revenue"] = "No quarterly revenue data available for the period."
            else:
                response["errors"]["revenue"] = "'Total Revenue' data not found in financials."
        else:
            response["errors"]["revenue"] = "Quarterly financials are empty for this ticker."
            
    except Exception as e:
        print(f"--- ERROR: Could not fetch or process revenue data for {ticker_symbol}: {e} ---")
        response["errors"]["revenue"] = "Failed to retrieve quarterly revenue data due to an unexpected error."

    return jsonify(response)





# -------------------- Run Flask --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
