nums = [-5, 0, 3, 7, -2, 9, 1, -8]
print(nums)
nums_f = list(filter(lambda x: x > 0, nums))
print(nums_f)
nums_f_s = list(map(lambda s: s * s, nums_f))
print(nums_f_s)