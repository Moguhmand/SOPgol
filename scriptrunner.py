r = [i/10 for i in range(1, 10, 1)]

rstrings = []

for i in r:
    rstrings.append(f'python test.py --cost-benefit {i} --grid-size 256')
    rstrings.append(f'python test.py --cost-benefit {i} --grid-size 64')

longstring = ' & '.join(rstrings)
print(longstring)