print("input weigth (kg)")
weigth2 = input()
print("input heigth (cm)")
heigth2 = input()

weigth = float(weigth2)
heigth = float(heigth2) / 100

index = weigth / (heigth ** 2)
end_index = round(index, 1)
print(end_index)