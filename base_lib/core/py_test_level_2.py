def make():
    funcs = []
    for i in range(3):
        funcs.append(lambda: i)
    return funcs

f1, f2, f3 = make()
print(f1(), f2(), f3())