"""
Background data generator for the Live Sales Query Explorer.

Seeds the `orders` table with a batch of realistic historical records on
first run, then inserts one new random order every few seconds to simulate
a live sales feed.
"""

import random
import time
from datetime import datetime, timedelta

import mysql.connector
from faker import Faker

from config import AMOUNT_MAX, AMOUNT_MIN, CATEGORIES, COUNTRIES, DB_CONFIG

fake = Faker()

SEED_MIN_ROWS = 500
SEED_MAX_ROWS = 1000
SEED_HISTORY_DAYS = 60
INSERT_MIN_INTERVAL = 3
INSERT_MAX_INTERVAL = 5


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def random_order(order_date=None):
    category = random.choice(list(CATEGORIES.keys()))
    product = random.choice(CATEGORIES[category])
    return {
        "customer_name": fake.name(),
        "country": random.choice(COUNTRIES),
        "category": category,
        "product": product,
        "amount": round(random.uniform(AMOUNT_MIN, AMOUNT_MAX), 2),
        "order_date": order_date or datetime.now(),
    }


def insert_order(conn, order):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO orders (customer_name, country, category, product, amount, order_date)
        VALUES (%(customer_name)s, %(country)s, %(category)s, %(product)s, %(amount)s, %(order_date)s)
        """,
        order,
    )
    conn.commit()
    cursor.close()


def seed_if_empty(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    (count,) = cursor.fetchone()
    cursor.close()

    if count > 0:
        print(f"[generator] orders table already has {count} rows, skipping seed.")
        return

    n_rows = random.randint(SEED_MIN_ROWS, SEED_MAX_ROWS)
    print(f"[generator] seeding {n_rows} historical orders...")

    now = datetime.now()
    orders = []
    for _ in range(n_rows):
        random_offset = timedelta(
            days=random.randint(0, SEED_HISTORY_DAYS),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        orders.append(random_order(order_date=now - random_offset))

    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO orders (customer_name, country, category, product, amount, order_date)
        VALUES (%(customer_name)s, %(country)s, %(category)s, %(product)s, %(amount)s, %(order_date)s)
        """,
        orders,
    )
    conn.commit()
    cursor.close()
    print(f"[generator] seed complete: {n_rows} rows inserted.")


def run():
    conn = get_connection()
    seed_if_empty(conn)

    print("[generator] entering live insert loop (Ctrl+C to stop)...")
    while True:
        order = random_order()
        insert_order(conn, order)
        print(
            f"[generator] inserted order: {order['customer_name']} | "
            f"{order['category']} / {order['product']} | "
            f"{order['country']} | €{order['amount']}"
        )
        time.sleep(random.uniform(INSERT_MIN_INTERVAL, INSERT_MAX_INTERVAL))


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n[generator] stopped.")
