# ===============================================================
# Project: VAMBEX — Volatility Adjusted Momentum Bands EXtended
# Author: Andre Pinheiro
# Date: 2025.12.17
# Version: v1.0.0
# Description: Fetches Kline data from Binance and returns it in a DataFrame.
# ===============================================================

import logging
from typing import List

import pandas as pd
import requests

logger = logging.getLogger(__name__)

BINANCE_BASE_URL = "http://data-api.binance.vision/api/v3/klines"
ALLOWED_INTERVALS = {
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M",
}
REQUEST_TIMEOUT = (3, 10)  # (connect_timeout, read_timeout) in seconds


class BinanceDataFetcher:
    def __init__(self, symbol: str, interval: str, limit: int = 1000):
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("symbol must be a non-empty string")

        if interval not in ALLOWED_INTERVALS:
            raise ValueError(
                f"interval must be one of: {', '.join(sorted(ALLOWED_INTERVALS))}"
            )

        if not isinstance(limit, int):
            raise ValueError("limit must be an integer between 1 and 1000")

        if limit < 1:
            raise ValueError("limit must be at least 1")

        if limit > 1000:
            logger.warning(
                "Limit is set to %s, but the maximum supported by Binance is 1000. Adjusting to 1000.",
                limit,
            )
            limit = 1000

        self.symbol = symbol.strip().upper()
        self.interval = interval
        self.limit = limit

        logger.info(
            "Initialized BinanceDataFetcher for %s with interval %s and limit %s",
            self.symbol,
            self.interval,
            self.limit,
        )

    def fetch_data(self) -> list:
        params = {"symbol": self.symbol, "interval": self.interval, "limit": self.limit}
        logger.debug(
            "Fetching data for %s with interval %s and limit %s",
            self.symbol,
            self.interval,
            self.limit,
        )

        response = None
        try:
            response = requests.get(
                BINANCE_BASE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            body_preview = (
                response.text[:500] if response is not None else "no response body"
            )
            logger.error(
                "Binance returned HTTP %s for %s (interval=%s, limit=%s). Body preview: %s",
                response.status_code if response is not None else "unknown",
                self.symbol,
                self.interval,
                self.limit,
                body_preview,
            )
            raise
        except requests.exceptions.RequestException as exc:
            logger.error(
                "Request to Binance failed for %s/%s (limit=%s): %s",
                self.symbol,
                self.interval,
                self.limit,
                exc,
            )
            raise

        logger.info(
            "Data fetched successfully for %s with interval %s",
            self.symbol,
            self.interval,
        )
        return response.json()

    def convert_to_dataframe(self, data: list) -> pd.DataFrame:
        if not isinstance(data, list):
            raise ValueError(
                "data must be a list returned by the Binance klines endpoint"
            )

        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "taker_buy_volume",
            "taker_buy_quote_volume",
            "ignore",
        ]

        if not data:
            logger.warning("No data returned for %s/%s", self.symbol, self.interval)
            empty_columns = [
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_volume",
                "trades",
                "taker_buy_volume",
                "taker_buy_quote_volume",
            ]
            return pd.DataFrame(columns=empty_columns)

        df = pd.DataFrame(data, columns=columns)
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", errors="coerce")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", errors="coerce")

        numeric_cols = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_volume",
            "taker_buy_volume",
            "taker_buy_quote_volume",
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["trades"] = pd.to_numeric(df["trades"], errors="coerce").astype("Int64")
        df = df.drop(columns=["ignore"])

        null_mask = df[numeric_cols + ["trades"]].isna()
        if null_mask.any().any():
            bad_counts = {
                col: int(null_mask[col].sum())
                for col in null_mask.columns
                if null_mask[col].any()
            }
            logger.error(
                "Malformed numeric data received for %s/%s: %s",
                self.symbol,
                self.interval,
                bad_counts,
            )
            raise ValueError(f"Malformed numeric data in columns: {bad_counts}")

        df = df.sort_values("open_time").reset_index(drop=True)

        logger.info(
            "Data converted to DataFrame for %s with %s rows",
            self.symbol,
            len(df),
        )
        return df

    def fetch_and_convert(self) -> pd.DataFrame:
        data = self.fetch_data()
        return self.convert_to_dataframe(data)


if __name__ == "__main__":
    from vambex.core.logging_config import setup_logging

    setup_logging(level=logging.DEBUG)
    logger.debug("Starting BinanceDataFetcher example")

    symbol = "BNBUSDT"
    interval = "4h"
    limit = 1000

    fetcher = BinanceDataFetcher(symbol, interval, limit)

    try:
        df = fetcher.fetch_and_convert()
        logger.debug(
            "Data fetched and converted successfully for %s with %s.",
            symbol,
            interval,
        )
        # print the first few rows of the DataFrame to verify content
        print(df.head())

        # Saving CSV, assuming df is your DataFrame with the data
        df.to_csv("candles_data.csv", index=False)
        logger.debug("Data saved to CSV file")

    except Exception as e:  # noqa: BLE001
        logger.error("Failed to fetch or convert data: %s", e)
