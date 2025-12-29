
def hex2float(ch):
    y = float.fromhex(ch)
    return y

if __name__ == "__main__":
    print(hex2float('A'))
'''
x = 5.0
print('x =', x, ',', 'y =', y)
print('x.as_integer_ratio() =', x.as_integer_ratio())
print('y.hex() =', y.hex())
# Typical comparisons can be made
print('x == y =', x == y)
print('x != y =', x != y)
print('x >= y =', x >= y)
print('x > y =', x > y)
print('x <= y =', x <= y)
print('x < y =', x < y)
# The usual operators can be used:
print('x + y =', x + y)
print('x - y =', x - y)
print('x * y =', x * y)
print('x / y =', x / y)
print('x // y =', x // y)
print('x % y =', x % y)
print('x ** y =', x ** y)
# There are several useful builtin functions:
print('divmod(x, y) =', divmod(x, y))
print('pow(x, y) =', pow(x,y))
print('abs(-x) =', abs(-x))
print('int(x) =', int(x))
print('float(10) =', float(10))
# Inline notation can also be used:
print('x = x + y =', end = ' ')
x += y
print(x)
print('x = x - y =', end = ' ')
x -= y
print(x)
print('x = x * y =', end = ' ')
x *= y
print(x)
print('x = x / y =', end = ' ')
x /= y
print(x)
# Multiple assignments can be done
x, y = 4.0, 2.0
print('x =', x, ',', 'y =', y)
# Bitwise operators cannot be used on the float type
'''
