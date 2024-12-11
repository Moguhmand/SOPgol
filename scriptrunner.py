r = [0.001,0.01,0.02,0.05,0.1,0.2,0.5,0.75,1]

rstrings = []

for i in r:
    rstrings.append(f'python test.py --cost-benefit {i} --interval 1000')

longstring = ' & '.join(rstrings)
print(longstring)