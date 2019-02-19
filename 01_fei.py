def fib(num):
    a, b = 0, 1
    for i in xrange(num):
        yield b
        a, b = b, a + b

print(fib(3))