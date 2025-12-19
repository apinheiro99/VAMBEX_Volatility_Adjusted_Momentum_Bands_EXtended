import json
from pathlib import Path

import numpy as np
import pandas as pd

TXT_COLUMNS = [
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

CSV_COLUMNS = [
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


def load_txt_as_df(path: Path, drop_last: bool = True) -> pd.DataFrame:
    with path.open("r") as file:
        raw = json.load(file)

    df = pd.DataFrame(raw, columns=TXT_COLUMNS)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")

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
        df[col] = pd.to_numeric(df[col])
    df["trades"] = pd.to_numeric(df["trades"]).astype("Int64")

    df = df.drop(columns=["ignore"])
    if drop_last and len(df) > 0:
        df = df.iloc[:-1]

    return df


def load_csv_as_df(path: Path, drop_last: bool = True) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["open_time", "close_time"])
    if drop_last and len(df) > 0:
        df = df.iloc[:-1]

    df = df[CSV_COLUMNS]
    df["trades"] = pd.to_numeric(df["trades"]).astype("Int64")
    return df


def compare_files(
    txt_file_path: str, csv_file_path: str, drop_last: bool = True
) -> None:
    txt_path = Path(txt_file_path)
    csv_path = Path(csv_file_path)

    # Map timestamp -> line number in the original CSV file (including header as line 1)
    csv_raw = pd.read_csv(csv_path, parse_dates=["open_time", "close_time"])
    csv_line_map = {ts: idx + 2 for idx, ts in enumerate(csv_raw["open_time"])}

    txt_df = (
        load_txt_as_df(txt_path, drop_last=drop_last)
        .set_index("open_time")
        .sort_index()
    )
    csv_df = (
        load_csv_as_df(csv_path, drop_last=drop_last)
        .set_index("open_time")
        .sort_index()
    )

    common_index = txt_df.index.intersection(csv_df.index)
    if common_index.empty:
        print("No common timestamps to compare.")
        return

    if len(common_index) != len(txt_df) or len(common_index) != len(csv_df):
        print(
            f"Warning: different sizes (txt={len(txt_df)}, csv={len(csv_df)}). "
            f"Comparing {len(common_index)} common timestamps."
        )

    txt_df = txt_df.loc[common_index]
    csv_df = csv_df.loc[common_index]

    diff = txt_df.compare(csv_df, keep_equal=False)

    if diff.empty:
        print("OK: data matches (ignoring the last line).")
    else:
        index_pos = pd.Series(range(1, len(txt_df) + 1), index=txt_df.index)
        differing_rows = diff.index.unique().tolist()
        print(f"Differences found in {len(differing_rows)} rows.")
        for row in differing_rows:
            pos = index_pos.loc[row]
            # Normalize to a plain int (handles scalar, Series, list, ndarray, Index)
            if hasattr(pos, "iloc"):
                pos = pos.iloc[0]
            elif isinstance(pos, (list, tuple, np.ndarray, pd.Index)):
                pos = pos[0]
            pos = int(pos)
            csv_line = csv_line_map.get(row, "n/a")
            print(f"\nRow {pos} (timestamp {row}, csv line {csv_line}):")
            print(diff.loc[row])


if __name__ == "__main__":
    TXT_PATH = "Z:\\programing\\baixar_binance\\binance_kline_fetcher\\BNBUSDT_4h_kline_binance.txt"
    CSV_PATH = "candles_data.csv"
    compare_files(TXT_PATH, CSV_PATH, drop_last=True)
