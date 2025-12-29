def func(a, b=[]):
    b.append(a)
    return b

print(func(1))
print(func(2))

x = [1, 2, 3]
y = x
y += [4, 5]
print(x, y)

a = {1, 2, 3}
b = {3, 4, 5}
print(a & b)

def f(x):
    return x * x

print(list(map(f, [1,2,3])))

from collections import Counter
print(Counter("banana"))

for i in range(3):
    pass
print(i)


print("a" in ["a", "b", "c"])

x = {1: "a", 2: "b"}
print(x.get(3, "default"))


def outer():
    x = 10
    def inner():
        print(x)
    return inner

fn = outer()
fn()