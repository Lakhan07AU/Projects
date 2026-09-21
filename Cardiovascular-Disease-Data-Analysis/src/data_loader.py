"""
Data Loader Module for Cardiovascular Disease Data Analysis
"""

import os
import sqlite3
import pandas as pd


def load_raw_data(file_path: str = "data/raw/cardio_train.csv") -> pd.DataFrame:
    """
    Load the raw Kaggle cardiovascular disease dataset.
    Detects delimiter automatically (';' or ',').
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw dataset file not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        first_line = f.readline()

    delimiter = ";" if ";" in first_line else ","
    df = pd.read_csv(file_path, sep=delimiter)
    return df


def load_cleaned_data(file_path: str = "data/processed/cardio_cleaned.csv") -> pd.DataFrame:
    """
    Load processed clean dataset.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Cleaned dataset file not found at: {file_path}")
    return pd.read_csv(file_path)


def save_to_sqlite(df: pd.DataFrame, db_path: str = "data/processed/cardio_db.sqlite", table_name: str = "cardio_cleaned") -> None:
    """
    Export DataFrame into an SQLite database for SQL query execution.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"Data saved to SQLite database: {db_path} (Table: {table_name})")


def run_sql_query(query: str, db_path: str = "data/processed/cardio_db.sqlite") -> pd.DataFrame:
    """
    Execute a SQL query against the SQLite database and return a Pandas DataFrame.
    """
    conn = sqlite3.connect(db_path)
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result
