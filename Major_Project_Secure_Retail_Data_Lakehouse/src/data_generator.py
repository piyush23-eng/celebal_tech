"""
data_generator.py
------------------
Simulates the RAW extract that would land from an e-commerce platform /
POS network before any governance is applied. This represents the
"Landing Zone" -- exactly what an operational system would dump, PII
and PCI data included in plain text, on purpose, so the rest of the
pipeline has something real to protect.

Run standalone to regenerate data/raw_transactions.csv.
"""

import random
from datetime import date, timedelta

import numpy as np
import os
import pandas as pd
from faker import Faker

fake = Faker("en_IN")
random.seed(42)
np.random.seed(42)

N_CUSTOMERS = 180
N_TRANSACTIONS = 1000


def _random_dob():
    start = date(1958, 1, 1)
    end = date(2006, 1, 1)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def _spend_amount():
    """
    Draw a transaction amount so that, in aggregate, the mix of
    Low / Medium / High spend categories mirrors a realistic retail
    pattern: lots of small basket sizes, a solid chunk of mid-range
    baskets, and a smaller tail of big-ticket purchases.
    """
    bucket = np.random.choice(
        ["low", "medium", "high"], p=[0.33, 0.48, 0.19]
    )
    if bucket == "low":
        return round(np.random.uniform(50, 999), 2)
    elif bucket == "medium":
        return round(np.random.uniform(1000, 4999), 2)
    else:
        return round(np.random.uniform(5001, 22000), 2)


def generate_customers(n):
    customers = []
    for i in range(n):
        customers.append(
            {
                "customer_id": f"CUST{i+1:04d}",
                "customer_name": fake.name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "address": fake.address().replace("\n", ", "),
                "date_of_birth": _random_dob().isoformat(),
            }
        )
    return customers


def generate_transactions(customers, n):
    rows = []
    for i in range(n):
        cust = random.choice(customers)
        card_number = fake.credit_card_number(card_type="mastercard")
        cvv = fake.credit_card_security_code()
        txn_date = fake.date_between(start_date="-180d", end_date="today")
        rows.append(
            {
                "transaction_id": f"TXN{i+1:06d}",
                "customer_id": cust["customer_id"],
                "customer_name": cust["customer_name"],
                "email": cust["email"],
                "phone": cust["phone"],
                "address": cust["address"],
                "date_of_birth": cust["date_of_birth"],
                "card_number": card_number,
                "cvv": cvv,
                "transaction_amount": _spend_amount(),
                "transaction_date": txn_date.isoformat(),
                "store_channel": random.choice(["E-Commerce", "POS-Store"]),
            }
        )
    return rows


def main(n_customers: int = N_CUSTOMERS, n_transactions: int = N_TRANSACTIONS, out_path: str = "data/raw_transactions.csv"):
    if n_customers <= 0 or n_transactions <= 0:
        raise ValueError(f"n_customers and n_transactions must be positive, got {n_customers}, {n_transactions}")
    customers = generate_customers(n_customers)
    transactions = generate_transactions(customers, n_transactions)
    df = pd.DataFrame(transactions)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} raw transactions for {n_customers} customers.")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()
