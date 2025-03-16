import os
from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

def get_stock_data(symbol: str):
    """Get stock data from Alpha Vantage API"""
    try:
        ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        data, meta_data = ts.get_daily(symbol=symbol, outputsize='compact')
        return {
            "symbol": symbol,
            "data": data.to_dict('records'),
            "meta_data": meta_data
        }
    except Exception as e:
        raise Exception(f"Error fetching stock data: {str(e)}")
