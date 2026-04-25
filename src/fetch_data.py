# src/fetch_data.py
import os, json, datetime, requests
import yfinance as yf

FINNHUB_KEY = os.environ["FINNHUB_API_KEY"]

TICKERS = [
    "SPY","QQQ","RSP","QQQE","DIA","IWM",
    "SMH","SOXX","IGV","XBI",
    "XLE","XLF","XLK","XLI","XLV","XLP","XLY","XLU","XLB","XLC","XLRE",
    "ITB","VIX","^VIX","GLD","TLT","HYG","IWM",
]

SECTOR_TICKERS = ["XLE","XLF","XLK","XLI","XLV","XLP","XLY","XLU","XLB","XLC","XLRE"]

def pct(new, old):
    if old and old != 0:
        return round((new - old) / old * 100, 2)
    return 0.0

def fetch_prices():
    """yfinance ile günlük kapanış fiyatlarını çek."""
    raw = [t for t in TICKERS if not t.startswith("^")]
    raw.append("^VIX")
    data = yf.download(raw, period="5d", auto_adjust=True, progress=False)["Close"]

    result = {}
    for t in raw:
        try:
            series = data[t].dropna()
            if len(series) >= 2:
                result[t] = {
                    "price": round(float(series.iloc[-1]), 2),
                    "prev":  round(float(series.iloc[-2]), 2),
                    "chg_pct": pct(float(series.iloc[-1]), float(series.iloc[-2])),
                    "week_ago": round(float(series.iloc[0]), 2),
                    "week_chg_pct": pct(float(series.iloc[-1]), float(series.iloc[0])),
                }
        except Exception:
            pass
    return result

def fetch_news():
    """Finnhub'dan piyasa haberleri çek."""
    url = "https://finnhub.io/api/v1/news"
    params = {"category": "general", "token": FINNHUB_KEY}
    try:
        r = requests.get(url, params=params, timeout=10)
        items = r.json()[:8]
        return [{"headline": i.get("headline",""), "summary": i.get("summary","")[:200]} for i in items]
    except Exception:
        return []

def fetch_earnings_calendar():
    """Önümüzdeki 5 günün önemli bilançoları."""
    today = datetime.date.today()
    end   = today + datetime.timedelta(days=5)
    url   = "https://finnhub.io/api/v1/calendar/earnings"
    params = {
        "from": today.isoformat(),
        "to":   end.isoformat(),
        "token": FINNHUB_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        items = r.json().get("earningsCalendar", [])
        # Sadece büyük isimler
        big = {"AAPL","MSFT","AMZN","META","GOOGL","GOOG","NVDA","TSLA","NFLX","AMD","INTC"}
        return [i for i in items if i.get("symbol") in big][:10]
    except Exception:
        return []

def fetch_economic_calendar():
    """Finnhub ekonomik takvim."""
    today = datetime.date.today()
    end   = today + datetime.timedelta(days=5)
    url   = "https://finnhub.io/api/v1/calendar/economic"
    params = {"from": today.isoformat(), "to": end.isoformat(), "token": FINNHUB_KEY}
    try:
        r = requests.get(url, params=params, timeout=10)
        items = r.json().get("economicCalendar", [])
        # Yüksek etkili olaylar
        hi = [i for i in items if i.get("impact","") in ("high","HIGH","3")]
        return hi[:8]
    except Exception:
        return []

def collect_all():
    today = datetime.date.today().strftime("%d %B %Y")
    prices   = fetch_prices()
    news     = fetch_news()
    earnings = fetch_earnings_calendar()
    econ_cal = fetch_economic_calendar()

    # Sektör RS skorları — SPY'ye göre haftalık rölatif performans
    spy_week = prices.get("SPY", {}).get("week_chg_pct", 0)
    sector_rs = {}
    for t in SECTOR_TICKERS:
        w = prices.get(t, {}).get("week_chg_pct", 0)
        sector_rs[t] = round(w - spy_week, 2)

    return {
        "date": today,
        "prices": prices,
        "sector_rs": sector_rs,
        "news": news,
        "earnings_calendar": earnings,
        "economic_calendar": econ_cal,
    }
