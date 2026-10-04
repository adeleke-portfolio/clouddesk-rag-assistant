# Lab 2 - Order Discount Calculator
customer_name = "Alice"
customer_type = "premium"   # try: "regular", "premium", "vip"
order_total = 50.00

# Determine discount rate
if customer_type == "vip":
    discount_rate = 0.20
elif customer_type == "premium":
    if order_total >= 200:
        discount_rate = 0.15
    else:
        discount_rate = 0.10
else:
    if order_total >= 100:
        discount_rate = 0.05
    else:
        discount_rate = 0.00

discount_amount = order_total * discount_rate
final_total = order_total - discount_amount

print(f"Customer: {customer_name}")
print(f"Customer type: {customer_type}")
print(f"Order total: ${order_total:.2f}")
print(f"Discount rate: {discount_rate * 100:.0f}%")
print(f"Discount amount: ${discount_amount:.2f}")
print(f"Final total: ${final_total:.2f}")