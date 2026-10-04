# Lab 4 - Sales report using a function

def calculate_discount(customer_type, order_total):
    if customer_type == "vip":
        return 0.20
    elif customer_type == "premium":
        if order_total >= 200:
            return 0.15
        else:
            return 0.10
    else:
        if order_total >= 100:
            return 0.05
        else:
            return 0.00


orders = [
    {"customer": "Alice",   "type": "vip",     "total": 500.00},
    {"customer": "Bob",     "type": "regular", "total": 80.00},
    {"customer": "Charlie", "type": "premium", "total": 250.00},
    {"customer": "Diana",   "type": "regular", "total": 150.00},
    {"customer": "Eve",     "type": "premium", "total": 120.00},
]

final_totals = []

for order in orders:
    customer_type = order["type"]
    order_total = order["total"]

    discount_rate = calculate_discount(customer_type, order_total)
    discount_amount = order_total * discount_rate
    final_total = order_total - discount_amount

    final_totals.append(final_total)

    print(f"{order['customer']}: {customer_type}, ${order_total:.2f} -> ${final_total:.2f}")

print("---")
print(f"Number of orders: {len(final_totals)}")
print(f"Total revenue: ${sum(final_totals):.2f}")
print(f"Average order value: ${sum(final_totals) / len(final_totals):.2f}")