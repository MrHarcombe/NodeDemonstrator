import itertools
import string

###
#
# experiments from the answers at https://stackoverflow.com/questions/42176498/repeating-letters-like-excel-columns,
#


def excel_cols():
    n = 1
    while True:
        yield from list(
            "".join(group)
            for group in itertools.product(string.ascii_uppercase, repeat=n)
        )
        n += 1


def generate_next_value():
    yield from itertools.chain(
        *[itertools.product(string.ascii_uppercase, repeat=i) for i in range(1, 1_000)]
    )
