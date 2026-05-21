import random

# Генерация случайных значений
rngA = random.randint(1, 99999)
rngB = random.randint(rngA, 100000)
rngK = random.randint(1, 1000)

print()
print(f"A = {rngA}, B = {rngB}, K = {rngK}")
print("-" * 67)

count = 0
min_num = None
max_num = None

n = rngA
while n <= rngB:
    end = 1
    temp = n
    while temp > 0:
        digit = temp % 10
        if digit != 0:
            end = end * digit
        temp = temp // 10

    if end == rngK:
        print(n)
        count = count + 1
        if min_num is None:
            min_num = n
            max_num = n
        else:
            if n < min_num:
                min_num = n
            if n > max_num:
                max_num = n

    n = n + 1

if count == 0:
    print("?" * random.randint(1, 15))
    print("-" * 67)
    print("Подходящих чисел нет :(")
else:
    print("-" * 67)
    print(f"Количество найденных чисел: {count}")
    print(f"Минимальное: {min_num}")
    print(f"Максимальное: {max_num}")