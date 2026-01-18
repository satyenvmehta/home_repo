import pandas as pd
import yfinance as yf
from datetime import datetime

# from TradeUtil import prep_ticker_list
from tp.market.get_price import getTickerObj, getTickerInfo
# from position import Positions
#
# positions = Positions()


def fetch_fundamentals_realtime(tickers, weekly_file='fundamentals_weekly.csv', save_file='screen_results.xlsx', pe_multiplier=1.0, peg_threshold=1.0):
    # Load weekly fundamentals
    weekly_df = pd.read_csv(weekly_file)
    # Fetch realtime
    records = []
    print("downloading Realtime data")
    for t in tickers:
        print(".", end="", flush=True)
        # info = yf.Ticker(t).info
        info = getTickerInfo(t)
        if info is None:
            continue

        pe = info.get('trailingPE') or info.get('forwardPE')
        # Get weekly data
        w = weekly_df[weekly_df['Ticker']==t]
        if w.empty or pe is None:
            continue
        bvps = w.iloc[0]['BVPS']
        growth = w.iloc[0]['Growth']
        sector = w.iloc[0]['Sector']
        # Compute PEG if growth positive
        peg = None
        if growth is not None and growth>0:
            peg = pe / (growth * 100)
        # You can also compute P/B: price might be needed
        price = info.get('regularMarketPrice')
        if price is None:
            price = info.get('currentPrice')
        price = round(price, 2)
        pe = round(pe, 2)
        peg = round(peg, 2)
        pb_ratio = None
        if price is not None and bvps is not None and bvps>0:
            pb_ratio = price / bvps
            pb_ratio = round(pb_ratio, 2)
        records.append({
            'Ticker': t,
            'Sector': sector,
            'PE': pe,
            'PEG': peg,
            'P/B': pb_ratio
        })
    df = pd.DataFrame(records)
    # Compute sector averages
    sector_avgs = df.groupby('Sector').agg({'PE':'mean','PEG':'mean'}).rename(columns={'PE':'Sector_Avg_PE','PEG':'Sector_Avg_PEG'})
    df = df.merge(sector_avgs, on='Sector', how='left')
    df['Ratio_vs_Sector_PE'] = round(df['PE'] / df['Sector_Avg_PE'], 2)
    df['Ratio_vs_Sector_PE_%'] = (df['Ratio_vs_Sector_PE'] * 100).round(1)

    # Filter
    filtered = df[(df['Ratio_vs_Sector_PE'] <= pe_multiplier) & (df['PEG'].notna()) & (df['PEG'] <= peg_threshold)]
    # Export
    sheet_name = C.datetime.now().strftime('%b_%d')
    with pd.ExcelWriter(save_file) as writer:
        filtered.to_excel(writer, sheet_name=sheet_name, index=False)
    return filtered

# Example usage
tickers = ["AAPL","MSFT","AMD","NVDA"]
# tickers = prep_ticker_list()
# fetch_weekly_fundamentals(tickers)
results = fetch_fundamentals_realtime(tickers, pe_multiplier=1.0, peg_threshold=1.0)
print(results)
