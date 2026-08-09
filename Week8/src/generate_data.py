"""
Part 1: Data Generation
------------------------
Generates 4 raw CSV files that simulate messy, real-world e-commerce data:
    data/raw/customers.csv
    data/raw/products.csv
    data/raw/orders.csv
    data/raw/order_items.csv

Design notes (the "think about" question):
    order_items.order_id must reference a real order most of the time, so
    order_items are generated AFTER orders, by sampling order_ids that
    already exist. To make check_referential_integrity() in clean_data.py
    actually have something to catch (and prove it works), a tiny, fixed
    number of "orphan" order_items rows are injected on purpose at the end
    (see BROKEN_REF_COUNT). Everything else stays consistent by construction.
"""

import csv
import os
import random
from datetime import datetime, timedelta

from faker import Faker

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# ---------------------------------------------------------------- settings
N_CUSTOMERS = 600
N_PRODUCTS = 150
N_ORDERS = 2200
BROKEN_REF_COUNT = 6          # intentional orphan order_items (edge case bait)

STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
STATUS_WEIGHTS = [0.10, 0.15, 0.55, 0.10, 0.10]
CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]
CUSTOMER_TYPE_WEIGHTS = [0.65, 0.25, 0.10]
REGIONS = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]

CATEGORY_MAP = {
    "Electronics": ["Mobiles", "Laptops", "Accessories", "Audio"],
    "Clothing": ["Men", "Women", "Kids", "Footwear"],
    "Home": ["Kitchen", "Furniture", "Decor", "Cleaning"],
    "Books": ["Fiction", "Non-Fiction", "Academic", "Comics"],
}

START_DATE = datetime(2023, 6, 1)
END_DATE = datetime(2025, 6, 30)   # ~2 years of history


def random_datetime(start, end):
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)


def messy_name_variant(name):
    """Randomly injects the extra-space / mixed-case issue the assignment asks for."""
    r = random.random()
    if r < 0.10:
        return f"  {name}  "
    if r < 0.20:
        return name.upper()
    if r < 0.30:
        return name.lower()
    return name


def messy_email(email):
    """~2% invalid emails: missing '@' or missing domain."""
    if random.random() < 0.02:
        if random.random() < 0.5:
            return email.replace("@", "")          # missing @
        return email.split("@")[0] + "@"            # missing domain
    return email


def wrong_date_format(dt):
    """A slice of orders get DD-MM-YYYY (string) instead of the standard format."""
    return dt.strftime("%d-%m-%Y %H:%M:%S")


def standard_date_format(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------- customers
def generate_customers():
    rows = []
    for cid in range(1, N_CUSTOMERS + 1):
        name = fake.name()
        base_email = fake.email()
        reg_date = random_datetime(START_DATE, END_DATE - timedelta(days=1))
        rows.append({
            "customer_id": cid,
            "customer_name": name,
            "email": messy_email(base_email),
            "registration_date": reg_date.strftime("%Y-%m-%d"),
            "customer_type": random.choices(CUSTOMER_TYPES, CUSTOMER_TYPE_WEIGHTS)[0],
        })
    path = os.path.join(RAW_DIR, "customers.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return rows


# ---------------------------------------------------------------- products
def generate_products():
    rows = []
    pid = 1
    for category, subcats in CATEGORY_MAP.items():
        per_cat = N_PRODUCTS // len(CATEGORY_MAP)
        for _ in range(per_cat):
            subcat = random.choice(subcats)
            raw_name = f"{fake.word().capitalize()} {subcat} {category[:3]}{pid}"
            rows.append({
                "product_id": pid,
                "product_name": messy_name_variant(raw_name),
                "category": category,
                "subcategory": subcat,
                "cost_price": round(random.uniform(50, 25000), 2),
            })
            pid += 1
    path = os.path.join(RAW_DIR, "products.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return rows


# ---------------------------------------------------------------- orders
def generate_orders(customers):
    rows = []
    customer_ids = [c["customer_id"] for c in customers]
    customer_reg = {c["customer_id"]: datetime.strptime(c["registration_date"], "%Y-%m-%d")
                    for c in customers}

    for oid in range(1, N_ORDERS + 1):
        has_customer = random.random() > 0.05          # 5% NULL customer_id
        cid = random.choice(customer_ids) if has_customer else ""

        # orders must happen on/after the customer registered
        earliest = customer_reg[cid] if has_customer else START_DATE
        order_dt = random_datetime(max(earliest, START_DATE), END_DATE)

        wrong_format = random.random() < 0.05            # 5% wrong date format
        date_str = wrong_date_format(order_dt) if wrong_format else standard_date_format(order_dt)

        rows.append({
            "order_id": oid,
            "customer_id": cid,
            "order_date": date_str,
            "status": random.choices(STATUSES, STATUS_WEIGHTS)[0],
            "region_code": random.choice(REGIONS),
        })
    path = os.path.join(RAW_DIR, "orders.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return rows


# ---------------------------------------------------------------- order_items
def generate_order_items(orders, products):
    rows = []
    item_id = 1
    product_ids = [p["product_id"] for p in products]
    product_price = {p["product_id"]: p["cost_price"] for p in products}
    order_ids = [o["order_id"] for o in orders]

    for order in orders:
        n_items = random.randint(1, 5)
        chosen_products = random.sample(product_ids, k=min(n_items, len(product_ids)))
        for pid in chosen_products:
            is_return = random.random() < 0.03           # 3% negative quantity
            qty = -random.randint(1, 3) if is_return else random.randint(1, 6)
            unit_price = round(product_price[pid] * random.uniform(1.15, 1.6), 2)  # markup over cost
            rows.append({
                "item_id": item_id,
                "order_id": order["order_id"],
                "product_id": pid,
                "quantity": qty,
                "unit_price": unit_price,
                "discount_percent": round(random.choice([0, 0, 0, 5, 10, 15, 20, 25, 30, 40]), 2),
            })
            item_id += 1

    # ---- intentionally inject a handful of orphan rows (bad order_id) ----
    max_real_order_id = max(order_ids)
    for _ in range(BROKEN_REF_COUNT):
        fake_order_id = max_real_order_id + random.randint(1000, 9999)
        pid = random.choice(product_ids)
        rows.append({
            "item_id": item_id,
            "order_id": fake_order_id,
            "product_id": pid,
            "quantity": random.randint(1, 3),
            "unit_price": round(product_price[pid] * 1.3, 2),
            "discount_percent": 0,
        })
        item_id += 1

    random.shuffle(rows)
    path = os.path.join(RAW_DIR, "order_items.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return rows


def main():
    print("Generating raw, intentionally-messy CSVs ...")
    customers = generate_customers()
    products = generate_products()
    orders = generate_orders(customers)
    order_items = generate_order_items(orders, products)

    print(f"  customers.csv    -> {len(customers)} rows")
    print(f"  products.csv     -> {len(products)} rows")
    print(f"  orders.csv       -> {len(orders)} rows")
    print(f"  order_items.csv  -> {len(order_items)} rows "
          f"(includes {BROKEN_REF_COUNT} intentional orphan rows)")
    print(f"Saved to: {os.path.abspath(RAW_DIR)}")


if __name__ == "__main__":
    main()
