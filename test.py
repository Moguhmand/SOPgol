import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import colormaps
import random
from matplotlib.collections import LineCollection
import math

# setup values
COOP = 255
DEFECTOR = 128
DEAD = 0
vals = [COOP, DEFECTOR, DEAD]


hypx = []
hypy = []
hline = []

def randomGrid(N):
    # returnerer et tilfældigt N*N grid
    return np.random.choice(vals, N*N, p=[0.2, 0.2, 0.6]).reshape(N, N)

def update(frameNum, img, imgPay, grid, N, payoffs, hyp, axHyp):

    # kopier grid
    # udregninger sker linje for linje
    newGrid = grid.copy()

    # udregn pGrid
    pGrid = np.zeros((N,N))

    for i in range(N):
        for j in range(N):

            if grid[i,j] == DEAD:
                pGrid[i,j] = 0
                continue

            # evt. implementer en reproduktionsmuligheds rng
            pSum = 0

            # for hver celle: udregn payoff sum -> udregn reproduktion
            naboer = [grid[(i-1)%N,(j-1)%N],grid[(i-1)%N,j],grid[(i-1)%N,(j+1)%N],
                      grid[i,(j-1)%N],grid[i,(j+1)%N],
                      grid[(i+1)%N,(j-1)%N],grid[(i+1)%N,j],grid[(i+1)%N,(j+1)%N]]

            # udregn payoff sum
            if grid[i,j] == COOP:
                for k in naboer:
                    if k == COOP:  # COOP vs COOP: R
                        pSum += 1
                    else:               # COOP vs DEF/DEAD: S
                        pSum += payoffs[1]

            elif grid[i,j] == DEFECTOR:
                for k in naboer:
                    if k == COOP:  # DEF vs COOP: T
                            pSum += payoffs[0]
                        # else (DEF - DEF): pSum += 0 
                        # else (whatever - DEAD): pSum += 0

            # //ellers er cellen død -> ingen payoff: pSum += 0
            # opdater pGrid
            pGrid[i,j] = pSum

            #print(grid[i,j],pSum)

            # grænse payoff (ved død celle, er payoff pr. definition 0)
            # if pSum > 0.1: #Celle har et payoff; får en reproduktionsmulighed.
            #     #Check for ledige pladser

            #     choice = naboer[pNaboer.index(max(pNaboer))]

            #     if grid[i,j] == COOP:
            #         if choice == COOP:  # COOP: R - COOP: R
            #             px, py = 1, 1
            #         else:               # COOP: S - DEF: T
            #             px, py = payoffs[1], payoffs[0]
            #     else:
            #         if choice == COOP:  # DEF: T - COOP: S
            #             px, py = payoffs[0], payoffs[1]
            #         else:               # DEF: P - DEF: P
            #             px, py = 0, 0

            #     # print(f'choices - x:{grid[i,j]}-{px}, y:{choice}-{py}. fitness: {(py - px)}, rng: {reproduceRng}')
            #     if random.random() > (py - px)/2:
            #         newGrid[i,j] = choice

    # opdater grid ud fra pGrid
    for i in range(N):
        for j in range(N):
            
            # nabo grids
            neighbourIndex = [[(i-1)%N,(j-1)%N],[(i-1)%N,j],[(i-1)%N,(j+1)%N],
                              [i,(j-1)%N],[i,(j+1)%N],
                              [(i+1)%N,(j-1)%N],[(i+1)%N,j],[(i+1)%N,(j+1)%N]]

            # find idekser på alle naboer eksl. naboer med nul payoff. 
            pIndexes = [k for k in neighbourIndex if pGrid[k[0],k[1]] != 0]
            # print(pIndexes)

            # hvis ingen naboer med payoff
            if len(pIndexes) == 0:
                newGrid[i,j] = DEAD
            else:
                # udtræk tilfældig nabo
                # choice = pIndexes[random.randint(0, len(pIndexes)-1)]

                choice = random.choices(pIndexes, weights=(float(pGrid[k[0],k[1]]) for k in pIndexes), k=1)[0]

                # hvis random er større end normaliseret payoff (py-px)/2 -> ny celle = udvalgt nabo
                # print('ps',pGrid[choice[0],choice[1]], pGrid[i,j])
                # print('success', (pGrid[choice[0],choice[1]] - pGrid[i,j])/2)

                # success baseret på en logistisk kurve (sigmoid kurve), hvis uafhængige variabel er differencen i fitness (payoff)
                difPay = pGrid[choice[0],choice[1]] - pGrid[i,j]
                sigmoid = 1 / (1 + math.exp(-1))

                if random.random() > sigmoid:
                    newGrid[i,j] = grid[choice[0], choice[1]]

    
    count = np.count_nonzero(newGrid == COOP)/(N*N)
    
    # opdater data
    img.set_data(newGrid)
    grid[:] = newGrid[:]

    imgPay.set_data(pGrid)

    hypx.append(frameNum)
    hypy.append(count)
    plt.xlim([-1, frameNum])
    plt.ylim([0, max(hypy)])

    if axHyp.texts:
        axHyp.texts[0].remove()
    if isinstance(axHyp.get_children()[1], LineCollection):
        axHyp.get_children()[1].remove()
    plt.text(0, count+20, f"count: {count}", fontsize=10)

    hyp.set_data(hypx, hypy)
    axHyp.hlines(y=count, xmin=0, xmax=frameNum)

    return img, imgPay, hyp,


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
    fig, ((axSnow, axPay), (axHyp, empty)) = plt.subplots(2,2)

    cmap = colormaps['viridis']
    for count, entry in enumerate(vals):
        clr = cmap(entry)
        print(clr)
        axSnow.plot(0,0,'-',color=clr, label=['COOP','DEFECTOR','DEAD'][count])    

    img = axSnow.imshow(grid, cmap=cmap, interpolation='nearest')
    startPay = np.zeros((N,N))
    startPay[0,0] = payoffs[0]*8
    imgPay = axPay.imshow(startPay, cmap='coolwarm', interpolation='nearest')

    hyp, = axHyp.plot(0,0)
    plt.title(f'r={args.r}; b={b}, c={c}; T={payoffs[0]}, R=1, S={payoffs[1]}, P=0')
    axSnow.legend(loc='upper right')

    ani = animation.FuncAnimation(fig, update, fargs=(img, imgPay, grid, N, payoffs, hyp, axHyp,), 
                                  interval=updateInterval, 
                                  save_count=500)


    # antal frames?
    # sæt output fil
    if args.movfile:
        ani.save(args.mavfile, fps=30, extra_args=['-vcodec', 'libx264'])
    
    plt.show()

if __name__ == '__main__':
    main()