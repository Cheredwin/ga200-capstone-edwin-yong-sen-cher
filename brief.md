# Lunchbox quotation brief

Heicoders Catering prices every weekday lunchbox order from `rates-lunchbox.json`. The rules are:

- The minimum order is 20 boxes. A smaller order cannot be quoted.
- The price per box depends on the total number of boxes in the order, and that one price applies to every box in the order.
- A delivery fee is charged once per order, by delivery area.
- GST of 9% is charged on the boxes plus the delivery fee, rounded to the nearest cent.

| Boxes in the order | Price per box |
| --- | --- |
| 20 to 49 | S$12.50 |
| 50 to 99 | S$11.80 |
| 100 or more | S$11.00 |

| Delivery area | Delivery fee per order |
| --- | --- |
| Central and CBD | S$30 |
| Other mainland Singapore | S$45 |
| Sentosa and Jurong Island | S$80 |

## Reference cases

Your calculator must match all three to the cent.

| Case | Order | Boxes | Delivery area | Boxes total | Delivery | GST (9%) | Total payable |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | LL-0413 | 30 | Central and CBD | 30 x S$12.50 = S$375.00 | S$30.00 | S$36.45 | **S$441.45** |
| 2 | LL-0412 | 60 | Sentosa and Jurong Island | 60 x S$11.80 = S$708.00 | S$80.00 | S$70.92 | **S$858.92** |
| 3 | LL-0414 | 120 | Other mainland Singapore | 120 x S$11.00 = S$1,320.00 | S$45.00 | S$122.85 | **S$1,487.85** |
