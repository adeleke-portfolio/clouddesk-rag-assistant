# Lab 4 - Discount logic as a reusable function

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


# Test the function
print(calculate_discount("vip", 500))       # expect 0.2
print(calculate_discount("premium", 250))   # expect 0.15
print(calculate_discount("premium", 120))   # expect 0.1
print(calculate_discount("regular", 150))   # expect 0.05
print(calculate_discount("regular", 50))    # expect 0.0