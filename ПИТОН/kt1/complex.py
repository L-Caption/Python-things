products = [
    {"name": "Laptop", "price": 950, "rating": 4.5, "in_stock": True},
    {"name": "Mouse", "price": -10, "rating": 4.8, "in_stock": True},
    {"name": "Keyboard", "price": 120, "rating": 3.9, "in_stock": False},
    {"name": "Monitor", "price": 300, "rating": 4.2, "in_stock": True},
    {"name": "Headphones", "price": 80, "rating": 4.6, "in_stock": True}
]

print()
print()
print()

def is_valid(product):
    if product["price"] > 0 and product["rating"] >= 4 and product["in_stock"] == True:
        return True
    else: return False

# new_products = []
# for product in products:
#     if is_valid(product):
#         new_products.append(product)

# print(new_products)

new_products = list(filter(is_valid, products))
print(new_products)
print()

def add_final_price(product):
    product["final_price"] = product["price"] * 0.85
    return product

new_products = list(map(add_final_price, new_products))
print(new_products)
print()

sorted_products = sorted(new_products, key=lambda x: x["price"])
print(sorted_products)
print()

def print_products(products):
    for item in products:
        print(item["name"], "| Цена:", item["price"], "| Итог:", item["final_price"])

print_products(sorted_products)