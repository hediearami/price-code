from flask import Flask, jsonify
import requests as re
import pandas as pd

app = Flask(__name__)

def calculate_returns():
    header = {'User-Agent': 'Mozilla/5.0'}
    url='https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/33015297618582406/0'
    req=re.get(url, headers=header)
    data = req.json()
    data_frame = pd.DataFrame(data["closingPriceDaily"])

    required_columns = ['dEven','priceFirst','priceMax','priceMin','pClosing','priceYesterday','qTotTran5J','qTotCap']
    new_result_df = data_frame[required_columns]         .rename(columns={'priceMin':'low','priceMax':'high','priceYesterday':'close_y','priceFirst':'open',
                         'dEven':'date','pClosing':'close','qTotTran5J':'volume','qTotCap':'value'})
    new_result_df['date'] = pd.to_datetime(data_frame['dEven'], format='%Y%m%d')
    df = new_result_df.copy()

    def بازدهی(df, days, date_col="date"):
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col, ascending=False).reset_index(drop=True)
        آخرین_روز = df[date_col].iloc[0]
        تاریخ_هدف = آخرین_روز - pd.Timedelta(days=days)
        فیلتر = df[df[date_col] <= تاریخ_هدف]
        if فیلتر.empty:  
            return None
        قیمت_قدیم = فیلتر.iloc[0]["close"]
        قیمت_جدید = df.iloc[0]["close"]
        return round(((قیمت_جدید - قیمت_قدیم) / قیمت_قدیم) * 100, 2)

    return {
        "daily": بازدهی(df, 1, "date"),
        "monthly": بازدهی(df, 30, "date"),
        "quarterly": بازدهی(df, 90, "date"),
        "yearly": بازدهی(df, 365, "date"),
    }

@app.route("/")
def home():
    return jsonify({"message": "برای دریافت بازدهی‌ها به مسیر /run بروید"})

@app.route("/run")
def run():
    try:
        results = calculate_returns()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
