import redis

from tp.market.mrkt_data_updater import make_key, DEBUG_TICKERS


def get_ticker_info(ticker: str) -> dict | None:
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    key = make_key(ticker)
    raw = r.hgetall(key)

    if raw is None:
        return None

    return raw


if __name__ == "__main__":
    for tkr in DEBUG_TICKERS:
        print(get_ticker_info(tkr))
    # print(get_ticker_info("AAPL"))
    # print(get_ticker_info("MSFT"))