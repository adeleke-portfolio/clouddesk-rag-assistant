# Lab 4 - A function that generates a formatted report

def calculate_discount(customer_type, order_total):
    if customer_type == "vip":
        return 0.20
    elif customer_type == "premium":
        return 0.15 if order_total >= 200 else 0.10
    else:
        return 0.05 if order_total >= 100 else 0.00


def generate_report(orders):
    lines = []
    final_totals = []

    for order in orders:
        rate = calculate_discount(order["type"], order["total"])
        final_total = order["total"] - order["total"] * rate
        final_totals.append(final_total)
        lines.append(f"{order['customer']}: ${order['total']:.2f} -> ${final_total:.2f}")

    lines.append("---")
    lines.append(f"Number of orders: {len(final_totals)}")
    lines.append(f"Total revenue: ${sum(final_totals):.2f}")
    lines.append(f"Average order value: ${sum(final_totals) / len(final_totals):.2f}")

    return "\n".join(lines)


orders = [
    {"customer": "Alice",   "type": "vip",     "total": 500.00},
    {"customer": "Bob",     "type": "regular", "total": 80.00},
    {"customer": "Charlie", "type": "premium", "total": 250.00},
    {"customer": "Diana",   "type": "regular", "total": 150.00},
    {"customer": "Eve",     "type": "premium", "total": 120.00},
]

report = generate_report(orders)
print(report)