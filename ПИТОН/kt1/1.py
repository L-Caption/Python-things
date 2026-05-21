def format_price(price, discount=0, currency='руб.'):
    if discount not in range(0, 100) or price < 0:
        return 'error?'
    end_price = price - (price * discount / 100)
    return f'{end_price} {currency}'

print(format_price(1000, 25))
print(format_price(2067, 99))
print(format_price(1100, 7, 'USD'))
print(format_price(1500, 0, 'EUR'))
print(format_price(1000, -5))
print(format_price(1000, 105))