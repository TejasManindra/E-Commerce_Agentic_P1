import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv


# Project root
BASE_DIR = Path(__file__).resolve().parents[1]

# Load .env from:
# C:\E-Commerce_Agentic_P1\.env
load_dotenv(BASE_DIR / ".env")


DB_USER = os.getenv("POSTGRES_USER", "ecommerce_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "ecommerce_bi")


DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


engine = create_engine(DATABASE_URL)


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "dataset"
)


tables = [
    "customers",
    "products",
    "orders",
    "order_items",
    "marketing_campaigns",
    "returns",
    "payments",
    "inventory",
    "delivery",
    "targets",
]


def load_table(table_name):
    file_path = os.path.join(
        DATA_DIR,
        f"{table_name}.csv"
    )

    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return

    df = pd.read_csv(file_path)

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False
    )

    print(
        f"[OK] {table_name}: {len(df)} rows loaded"
    )


if __name__ == "__main__":

    print("Starting E-Commerce data loading...\n")

    print("Database configuration:")
    print(f"  Host: {DB_HOST}")
    print(f"  Port: {DB_PORT}")
    print(f"  Database: {DB_NAME}")
    print(f"  User: {DB_USER}")
    print(f"  Password loaded: {bool(DB_PASSWORD)}")
    print()

    for table in tables:
        load_table(table)

    print("\nData loading completed.")