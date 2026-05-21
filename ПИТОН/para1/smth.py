print("КалькуляторIO")

def add(a, b):
    return a + b
def substract(a, b):
    return a - b
def multiply(a, b):
    return a * b
def divide(a, b):
    if b != 0:
        return a / b
    else: print("Error!0 // Cant divide by zero #1")
def square(a, b):
    return a ** b
def root(a, b):
    if b == 0:
        return 1
    else:
        return a ** (1/b)
    
def MAINcheckcall(thatthing):
    # USERinput = str(input())
    # temp1 = USERinput.split(" ")
    temp1 = thatthing.split(" ")
    temp1[0] = float(temp1[0])
    temp1[2] = float(temp1[2])
    result = 0
    print(temp1)
    if temp1[0] and temp1[2]:
        if temp1[1] == '+':
            result = add(temp1[0], temp1[2])
        elif temp1[1] == '-':
            result = substract(temp1[0], temp1[2])
        elif temp1[1] == '*':
            result = multiply(temp1[0], temp1[2])
        elif temp1[1] == '/':
            result = divide(temp1[0], temp1[2])
        elif temp1[1] == '^':
            result = square(temp1[0], temp1[2])
        elif temp1[1] == '#':
            result = root(temp1[0], temp1[2])
        else:
            print("Error!2 // Innaporiate syntaxis #2")
    else:
        print("Error!1 // Innaporiate syntaxis #1")
    print(result)
    print()
        

print()
print("Арсенал:")
print("+ = дать")
print("- = отнять")
print("* = увеличить")
print("/ = умеличить")
print("^ = степенить")
print("# = корнить")
print()
print("Пример выражения:")
print("a + b")
print("(Ответ)")
print()

while True:
    USERinput = str(input())
    if USERinput != None:
        MAINcheckcall(USERinput)
    else: 
        break