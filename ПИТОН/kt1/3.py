words = ["apple", "banana", "cherry", "dragon", "elephant", "fig", "grape", "honey", "iris", "jungle"]
numbers = [-15, -7, 0, 3, 8, 12, -3, 25, 0, 47]

def transform_list(data, func):
    return list(map(func, data))

print(transform_list(["hello", "world"], lambda x: x.upper()))