# Query Results Summary

## Query 1: total revenue per category
- rows returned: 4
- saved to: query_results/01_total_revenue_per_category.csv

| category    |   total_revenue |
|:------------|----------------:|
| Electronics |     8.5929e+07  |
| Books       |     8.39756e+07 |
| Clothing    |     6.91218e+07 |
| Home        |     6.50194e+07 |

## Query 2: top 10 customers by value
- rows returned: 10
- saved to: query_results/02_top_10_customers_by_value.csv

|   customer_id | customer_name   |   total_order_value |
|--------------:|:----------------|--------------------:|
|            87 | Advik Salvi     |         1.47801e+06 |
|           352 | Xalak Dewan     |         1.4633e+06  |
|           451 | Gayathri Mittal |         1.45453e+06 |
|           346 | Warhi Hayre     |         1.43959e+06 |
|           331 | Vaishnavi Madan |         1.39685e+06 |

## Query 3: monthwise order count last 12m
- rows returned: 12
- saved to: query_results/03_monthwise_order_count_last_12m.csv

| year_month   |   order_count |
|:-------------|--------------:|
| 2024-07      |            60 |
| 2024-08      |            59 |
| 2024-09      |            80 |
| 2024-10      |           102 |
| 2024-11      |           100 |

## Query 4: customers never delivered
- rows returned: 63
- saved to: query_results/04_customers_never_delivered.csv

|   customer_id | customer_name       |
|--------------:|:--------------------|
|             4 | Abeer Dutta         |
|             8 | Bimala Buch         |
|            16 | Lekha Raj           |
|            28 | Niharika Gupta      |
|            32 | Chandresh Zachariah |

## Query 5: products more returns than purchases
- rows returned: 0
- saved to: query_results/05_products_more_returns_than_purchases.csv

| product_id   | product_name   | units_purchased   | units_returned   |
|--------------|----------------|-------------------|------------------|

## Query 6: return rate per category
- rows returned: 4
- saved to: query_results/06_return_rate_per_category.csv

| category    |   returned_units |   total_units |   return_rate |
|:------------|-----------------:|--------------:|--------------:|
| Books       |              126 |          5802 |        0.0217 |
| Home        |              104 |          5519 |        0.0188 |
| Clothing    |               99 |          5384 |        0.0184 |
| Electronics |              102 |          5685 |        0.0179 |

## Query 7: running total revenue per region
- rows returned: 1404
- saved to: query_results/07_running_total_revenue_per_region.csv

| region_code   | order_date   |   daily_revenue |   running_total |
|:--------------|:-------------|----------------:|----------------:|
| CENTRAL       | 2023-06-03   |         86567.9 |         86567.9 |
| CENTRAL       | 2023-08-16   |         84355   |        170923   |
| CENTRAL       | 2023-09-03   |         40182.8 |        211106   |
| CENTRAL       | 2023-09-12   |        183501   |        394607   |
| CENTRAL       | 2023-09-13   |         73858.5 |        468466   |

## Query 8: product rank by revenue dense rank
- rows returned: 148
- saved to: query_results/08_product_rank_by_revenue_dense_rank.csv

| category   | product_name               |   total_revenue |   rank_in_category |
|:-----------|:---------------------------|----------------:|-------------------:|
| Books      | Maxime Non-Fiction Boo141  |     5.52947e+06 |                  1 |
| Books      | Enim Non-Fiction Boo115    |     4.78178e+06 |                  2 |
| Books      | Perspiciatis Comics Boo144 |     4.53655e+06 |                  3 |
| Books      | Laborum Fiction Boo148     |     4.53352e+06 |                  4 |
| Books      | Quos Comics Boo143         |     4.19094e+06 |                  5 |

## Query 9: days between orders lag
- rows returned: 2025
- saved to: query_results/09_days_between_orders_lag.csv

|   customer_id | order_date   | previous_order_date   |   days_gap | risk_flag   |
|--------------:|:-------------|:----------------------|-----------:|:------------|
|             1 | 2024-12-04   | nan                   |        nan | At Risk     |
|             1 | 2024-12-09   | 2024-12-04            |          5 | At Risk     |
|             1 | 2025-01-13   | 2024-12-09            |         35 | At Risk     |
|             1 | 2025-01-14   | 2025-01-13            |          1 | At Risk     |
|             1 | 2025-02-03   | 2025-01-14            |         20 | At Risk     |

## Query 10: cte multilevel revenue category counts
- rows returned: 55
- saved to: query_results/10_cte_multilevel_revenue_category_counts.csv

| year_month   | revenue_category   |   customer_count |
|:-------------|:-------------------|-----------------:|
| 2023-07      | High               |                3 |
| 2023-08      | High               |                3 |
| 2023-09      | High               |               16 |
| 2023-10      | High               |               20 |
| 2023-10      | Low                |                1 |

## Query 11: ntile customer quartiles
- rows returned: 586
- saved to: query_results/11_ntile_customer_quartiles.csv

|   customer_id |   total_value |   quartile | quartile_label   |
|--------------:|--------------:|-----------:|:-----------------|
|            87 |   1.47801e+06 |          1 | Platinum         |
|           352 |   1.4633e+06  |          1 | Platinum         |
|           451 |   1.45453e+06 |          1 | Platinum         |
|           346 |   1.43959e+06 |          1 | Platinum         |
|           331 |   1.39685e+06 |          1 | Platinum         |

## Query 12: yoy revenue comparison
- rows returned: 25
- saved to: query_results/12_yoy_revenue_comparison.csv

|   year |   month |          revenue |   prev_year_revenue |   yoy_growth_percent |
|-------:|--------:|-----------------:|--------------------:|---------------------:|
|   2023 |       6 | 848220           |                 nan |                  nan |
|   2023 |       7 | 724978           |                 nan |                  nan |
|   2023 |       8 | 959304           |                 nan |                  nan |
|   2023 |       9 |      3.29375e+06 |                 nan |                  nan |
|   2023 |      10 |      3.51662e+06 |                 nan |                  nan |

## Query 13: first last category shift
- rows returned: 586
- saved to: query_results/13_first_last_category_shift.csv

|   customer_id | first_category   | last_category   | category_shift   |
|--------------:|:-----------------|:----------------|:-----------------|
|             1 | Books            | Home            | Yes              |
|             2 | Books            | Electronics     | Yes              |
|             3 | Books            | Books           | No               |
|             4 | Books            | Clothing        | Yes              |
|             5 | Clothing         | Books           | Yes              |

## Query 14: cumulative revenue distribution
- rows returned: 586
- saved to: query_results/14_cumulative_revenue_distribution.csv

|   customer_id |     revenue |   cumulative_revenue |   cumulative_percent |
|--------------:|------------:|---------------------:|---------------------:|
|            87 | 1.47801e+06 |          1.47801e+06 |                 0.51 |
|           352 | 1.4633e+06  |          2.94131e+06 |                 1.02 |
|           451 | 1.45453e+06 |          4.39584e+06 |                 1.52 |
|           346 | 1.43959e+06 |          5.83543e+06 |                 2.02 |
|           331 | 1.39685e+06 |          7.23229e+06 |                 2.5  |

## Query 15: cohort retention
- rows returned: 90
- saved to: query_results/15_cohort_retention.csv

| cohort_month   |   month_offset |   active_customers |   cohort_customers |   retention_rate_percent |
|:---------------|---------------:|-------------------:|-------------------:|-------------------------:|
| 2023-06        |              1 |                  1 |                 10 |                    10    |
| 2023-06        |              2 |                  2 |                 10 |                    20    |
| 2023-06        |              3 |                  1 |                 10 |                    10    |
| 2023-07        |              0 |                  2 |                 24 |                     8.33 |
| 2023-07        |              1 |                  1 |                 24 |                     4.17 |

## Query 16: products frequently bought together
- rows returned: 25
- saved to: query_results/16_products_frequently_bought_together.csv

| product_a                    | product_b                     |   times_bought_together |
|:-----------------------------|:------------------------------|------------------------:|
| Dignissimos Audio Ele9       | Voluptatem Decor Hom90        |                       7 |
| Dignissimos Audio Ele9       | Dolorum Comics Boo140         |                       6 |
| Doloremque Accessories Ele11 | Dolorum Comics Boo140         |                       6 |
| Totam Non-Fiction Boo123     | Reprehenderit Academic Boo124 |                       6 |
| Dolores Mobiles Ele28        | Maxime Non-Fiction Boo141     |                       5 |
