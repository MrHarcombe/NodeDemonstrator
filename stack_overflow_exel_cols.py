import itertools, string, sys

def excel_cols():
    n = 1
    while True:
        yield from list(''.join(group) for group in itertools.product(string.ascii_uppercase, repeat=n))
        n += 1

##for _ in range(2000):
##    print(excel_cols())

def generate_next_value():
    yield from itertools.chain(*[itertools.product(string.ascii_uppercase, repeat=i) for i in range(1, 1_000)])
