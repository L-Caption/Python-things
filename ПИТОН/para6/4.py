import random

def randify():
    return random.randint(1, 7)

while True:
    n = randify()
    guess = input("Угадай число от 1 до 7: ")
    if guess.isdigit() and int(guess) == n:
        print("Правильно! Число было " + str(n))
        break
        