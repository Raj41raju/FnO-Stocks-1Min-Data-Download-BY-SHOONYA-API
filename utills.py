import os
import io
import zipfile
import requests
import pandas as pd

def token_download(path: str) -> dict:
    """
    Download Shoonya symbol masters (NSE, BSE, NFO, BFO),
    extract them into `path`, load them as pandas DataFrames,
    normalize columns to a consistent schema, and return them.

    Returns
    -------
    dict[str, pd.DataFrame]
        {
          'NSE': <equities df>,
          'BSE': <equities df>,
          'NFO': <derivatives df>,
          'BFO': <derivatives df>
        }

    Notes
    -----
    - Files are pipe-delimited.
    - Columns are normalized to Shoonya field names:
      ['exch','token','tsym','cname','symname','seg','instname','isin',
       'pp','ls','ti','exd','strprc','optt']
      (equity masters won’t have the derivative-specific fields and vice-versa).
    """
    os.makedirs(path, exist_ok=True)

    root = "https://api.shoonya.com/"
    masters = {
        "NSE_symbols.txt.zip": "NSE",
        "BSE_symbols.txt.zip": "BSE",
        "NFO_symbols.txt.zip": "NFO",
        "BFO_symbols.txt.zip": "BFO",
    }

    # full superset of expected Shoonya fields
    std_cols = [
        "exch","token","tsym","cname","symname","seg","instname","isin",
        "pp","ls","ti","exd","strprc","optt"
    ]
    # dtypes/transformers
    numeric_cols = {"pp": "Int64", "ls": "Int64"}
    float_cols = {"ti": "float64", "strprc": "float64"}
    date_cols = ["exd"]

    out: dict[str, pd.DataFrame] = {}

    def _read_symbols_txt(txt_path: str) -> pd.DataFrame:
        # Try header inference; fallback to no header
        try:
            df_try = pd.read_csv(txt_path, sep="|", dtype=str, low_memory=False)
            # If the first row looks like header repeated in data, re-read without header
            if not {"token", "tsym"}.intersection(set(map(str.lower, df_try.columns))):
                df_try = pd.read_csv(txt_path, sep="|", dtype=str, header=None, low_memory=False)
        except Exception:
            df_try = pd.read_csv(txt_path, sep="|", dtype=str, header=None, low_memory=False)

        # If there’s no header, map by best-known order; otherwise lowercase existing names
        if isinstance(df_try.columns[0], int):
            # Best-effort positional mapping:
            # common order seen across docs: exch, token, tsym, cname, symname, seg, instname,
            # isin, pp, ls, ti, exd, strprc, optt  (extra columns are kept)
            pos_map = {
                0: "exch", 1: "token", 2: "tsym", 3: "cname", 4: "symname",
                5: "seg", 6: "instname", 7: "isin", 8: "pp", 9: "ls",
                10: "ti", 11: "exd", 12: "strprc", 13: "optt"
            }
            df = df_try.rename(columns=pos_map)
        else:
            # normalize header names to lowercase Shoonya keys
            rename = {c: c.strip().lower() for c in df_try.columns}
            df = df_try.rename(columns=rename)

        # Keep known columns + keep any extras separately, then reattach extras at end
        extras = [c for c in df.columns if c not in std_cols]
        for c in std_cols:
            if c not in df.columns:
                df[c] = pd.NA

        # Cast types safely
        for c, dt in numeric_cols.items():
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce").astype(dt)
        for c, dt in float_cols.items():
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        if "exd" in df.columns:
            # Shoonya uses yyyy-mm-dd or dd-MMM-yy in places; try both
            df["exd"] = pd.to_datetime(df["exd"], errors="coerce", infer_datetime_format=True)

        # Token as string, tsym trimmed
        if "token" in df.columns:
            df["token"] = df["token"].astype(str).str.strip()
        if "tsym" in df.columns:
            df["tsym"] = df["tsym"].astype(str).str.strip()

        # Order columns
        df = df[std_cols + extras]

        # Drop empty rows (no token+tsym)
        if {"token","tsym"}.issubset(df.columns):
            df = df[~(df["token"].isna() & df["tsym"].isna())].reset_index(drop=True)

        return df

    for zip_name, key in masters.items():
        url = root + zip_name
        r = requests.get(url, allow_redirects=True, timeout=60)
        r.raise_for_status()

        # extract directly from memory
        with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
            zf.extractall(path)

        # read the extracted txt
        txt_name = zip_name.replace(".zip", "")
        txt_path = os.path.join(path, txt_name)
        if not os.path.exists(txt_path):
            # fallback: locate any .txt inside the zip we just extracted
            candidates = [f for f in os.listdir(path) if f.endswith(".txt") and key in f.upper()]
            if candidates:
                txt_path = os.path.join(path, candidates[0])
            else:
                raise FileNotFoundError(f"Could not locate extracted text for {key}")

        df = _read_symbols_txt(txt_path)

        # Add/confirm exch segment column if missing
        if "exch" in df.columns:
            df["exch"] = df["exch"].fillna(key if key in ("NSE","BSE") else ("NSE" if "NFO" in key else "BSE"))

        out[key] = df

    return out
