time = 3665

hours = time // 3600
print(hours)
minutes = (time - (hours * 3600)) // 60
print(minutes)
seconds = (time - (hours * 3600) - (minutes * 60)) // 1
print(seconds)

print()

print(hours, ':', minutes, ':', seconds)