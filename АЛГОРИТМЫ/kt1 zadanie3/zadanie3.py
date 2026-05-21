array = [ 0, 1, 2, 2, 3, 3, 4, 5 ]

def thing(massif):
    print()
    massifSIZE = len(massif) 
    print("МАССИВНОСТЬ:", massif, "РАЗМЕРНОСТЬ:", massifSIZE) #проверки1
    print()
    for i in range(0, massifSIZE):
        print("[", i ,"]", "СОДЕРЖАТЕЛЬНОСТЬ:", massif[i]) #проверки2
        
        if massif[i] == massif[i - 1]: #повторение элемента хотябы 2 раза
            print()
            return i - 1 #возвращает предыдущий элемент при успешном выполнении (первый елемент) + учитывает только единичное повторение за весь массив
        
print(thing(array), "*элемент повторяется")