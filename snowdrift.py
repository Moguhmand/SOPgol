import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from matplotlib.collections import LineCollection

# setup values
COOP = 255
DEFECTOR = 0
vals = [COOP, DEFECTOR]


hypx = []
hypy = []
hline = []

def randomGrid(N):
    # returnerer et tilfældigt N*N grid
    return np.random.choice(vals, N*N, p=[0.2, 0.8]).reshape(N, N)

def update(frameNum, img, grid, N, payoffs, hyp, axr):

    # kopier grid
    # udregninger sker linje for linje
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):

            # for hver celle: udvælg tilfældig nabo -> sammenlign strat -> udregn payoff -> udregn reproductive succes
            choice = [grid[(i-1)%N,(j-1)%N],grid[(i-1)%N,j],grid[(i-1)%N,(j+1)%N],
                      grid[i,(j-1)%N],grid[i,(j+1)%N],
                      grid[(i+1)%N,(j-1)%N],grid[(i+1)%N,j],grid[(i+1)%N,(j+1)%N]][random.randint(0,7)]

            if grid[i,j] == COOP:
                if choice == COOP:  # COOP: R - COOP: R
                    px, py = 1, 1
                else:               # COOP: S - DEF: T
                    px, py = payoffs[1], payoffs[0]
            else:
                if choice == COOP:  # DEF: T - COOP: S
                    px, py = payoffs[0], payoffs[1]
                else:               # DEF: P - DEF: P
                    px, py = 0, 0
            
            # print(f'choices - x:{grid[i,j]}-{px}, y:{choice}-{py}. fitness: {(py - px)}, rng: {reproduceRng}')
            if random.random() > (py - px)/2:
                newGrid[i,j] = choice
            # else:
            #     newGrid[i,j] = grid[i,j]
            
    count = np.count_nonzero(newGrid == COOP)/(N*N)
    
    # opdater data
    img.set_data(newGrid)
    grid[:] = newGrid[:]


    hypx.append(frameNum)
    hypy.append(count)
    plt.xlim([-1, frameNum])
    plt.ylim([0, max(hypy)])

    if axr.texts:
        axr.texts[0].remove()
    if isinstance(axr.get_children()[1], LineCollection):
        axr.get_children()[1].remove()
    # plt.text(0, count+20, f"count: {count}", fontsize=10)

    hyp.set_data(hypx, hypy)
    axr.hlines(y=count, xmin=0, xmax=frameNum)

    return img, hyp,


# main() funktion
def main():

    # kommandolinje argumenter findes i sys.argv[1], sys.argv[2] osv.
    # sys.argv[0] er script navnet. Denne ignoreres
    # parse argumenter
    parser = argparse.ArgumentParser(description="Enter cost/benefit ratio, r: ")

    # tilføj argumenter
    parser.add_argument('--cost-benefit', dest='r', required=True)
    parser.add_argument('--grid-size', dest='N', required=False) 
    parser.add_argument('--mov-file', dest='movfile', required=False) 
    parser.add_argument('--interval', dest='interval', required=False) 
    args = parser.parse_args() 

    # sæt cost-benefit
    if args.r and float(args.r) > 0 and float(args.r) < 1:
        b,c = float(args.r) + 1, 2 * float(args.r)

        # R=1, T, S, P=0
        payoffs = [b, b-c]
        print(f'r={args.r}; b={b}, c={c}; T={payoffs[0]}, R=1, S={payoffs[1]}, P=0')

    # sæt grid-størrelse
    N = 100
    if args.N and int(args.N) > 8:
        N = int(args.N)

    # sæt animation opdaterings interval
    updateInterval = 50
    if args.interval:
        updateInterval = int(args.interval)
    
    # declare grid
    grid = np.array([])

    # fyld grid tilfældigt (mere OFF end ON)
    grid = randomGrid(N)
    

    # sæt animationen op
    fig, (axl, axr) = plt.subplots(
        nrows=2,
    )

    img = axl.imshow(grid, cmap='cool', interpolation='nearest')
    hyp, = axr.plot(0,0)
    plt.title(f'r={args.r}; b={b}, c={c}; T={payoffs[0]}, R=1, S={payoffs[1]}, P=0')

    ani = animation.FuncAnimation(fig, update, fargs=(img, grid, N, payoffs, hyp, axr,), 
                                  interval=updateInterval, 
                                  save_count=500)


    # antal frames?
    # sæt output fil
    if args.movfile:
        ani.save(args.mavfile, fps=30, extra_args=['-vcodec', 'libx264'])
    
    plt.show()

if __name__ == '__main__':
    main()