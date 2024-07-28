def yielding_func():
    for i in range(10):
        yield i


outputs = iter(yielding_func())
input(">")

while True:
    try:
        print(next(outputs))
        input(">")
    except StopIteration:
        break

print("Done")
