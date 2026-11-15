import pandas as pd
import yfinance as yf
from modules.universe import to_yahoo_symbol

def _latest(frame, labels):
    if frame is None or frame.empty:
        return None
    for label in labels:
        if label in frame.index:
            values = frame.loc[label].dropna()
            if len(values):
                try:
                    return float(values.iloc[0])
                except Exception:
                    return None
    return None

def get_snapshot(symbol: str):
    yf_symbol = to_yahoo_symbol(symbol)
    ticker = yf.Ticker(yf_symbol)
    info = ticker.get_info() or {}
    hist = ticker.history(period="1y", auto_adjust=True)
    financials = ticker.financials
    balance = ticker.balance_sheet
    cashflow = ticker.cashflow
    price = float(hist["Close"].dropna().iloc[-1]) if not hist.empty else info.get("currentPrice")
    prev = float(hist["Close"].dropna().iloc[-2]) if len(hist) > 1 else None
    change = ((price / prev) - 1) * 100 if price and prev else None
    market_cap = info.get("marketCap")
    return {
        "symbol": symbol.upper(), "yahoo_symbol": yf_symbol,
        "company": info.get("longName") or info.get("shortName") or symbol.upper(),
        "sector": info.get("sector") or "Not available",
        "industry": info.get("industry") or "",
        "market_cap_inr": market_cap,
        "market_cap_crore": market_cap / 1e7 if market_cap else None,
        "price": price, "day_change_pct": change,
        "trailing_pe": info.get("trailingPE"), "forward_pe": info.get("forwardPE"),
        "price_to_book": info.get("priceToBook"),
        "roe": info.get("returnOnEquity"),
        "profit_margin": info.get("profitMargins"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "debt_to_equity": info.get("debtToEquity"),
        "total_revenue_latest_fy": _latest(financials, ["Total Revenue"]),
        "net_income_latest_fy": _latest(financials, ["Net Income"]),
        "operating_cash_flow_latest_fy": _latest(cashflow, ["Operating Cash Flow"]),
        "free_cash_flow_latest_fy": _latest(cashflow, ["Free Cash Flow"]),
        "total_debt_latest_fy": _latest(balance, ["Total Debt"]),
        "data_source": "Yahoo Finance via yfinance; verify against exchange filings",
    }

def run_screen(symbols, min_cap_crore=0, min_revenue_growth=-1, min_roe=-1):
    rows, errors = [], []
    for symbol in symbols:
        try:
            d = get_snapshot(symbol)
            if d["market_cap_crore"] is not None and d["market_cap_crore"] < min_cap_crore:
                continue
            if d["revenue_growth"] is not None and d["revenue_growth"] < min_revenue_growth:
                continue
            if d["roe"] is not None and d["roe"] < min_roe:
                continue
            rows.append({
                "Symbol": d["symbol"], "Company": d["company"], "Sector": d["sector"],
                "Market Cap ₹ Cr": round(d["market_cap_crore"], 1) if d["market_cap_crore"] is not None else None,
                "Revenue growth %": round(d["revenue_growth"] * 100, 1) if d["revenue_growth"] is not None else None,
                "Earnings growth %": round(d["earnings_growth"] * 100, 1) if d["earnings_growth"] is not None else None,
                "ROE %": round(d["roe"] * 100, 1) if d["roe"] is not None else None,
                "PE": round(d["trailing_pe"], 1) if d["trailing_pe"] is not None else None,
                "Price ₹": round(d["price"], 2) if d["price"] is not None else None,
            })
        except Exception as exc:
            errors.append(f"{symbol}: {exc}")
    return pd.DataFrame(rows), errors
