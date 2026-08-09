# Data Quality Report

## orders.csv
- **wrong_date_format_fixed**: 99
- **unparseable_dates**: 0
- **missing_customer_id**: 114

## products.csv
- **product_names_normalized**: 37

## customers.csv
- **invalid_emails**: 9
- **affected customer_ids (first 20)**: ['192', '254', '308', '318', '331', '350', '379', '470', '519']

## order_items.csv
- **orphan_order_items_found**: 6 (order_id not present in orders.csv)
- **orphan_rows_removed**: 6
- **negative_quantity_flagged**: 220
- **invalid_discount_flagged**: 0

_Orphan item_ids removed: [6546, 6547, 6548, 6549, 6550, 6551]_
