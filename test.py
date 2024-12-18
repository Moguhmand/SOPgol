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
hypCoopy = []
hypDefy = []
hypDeady=[]

def randomGrid(N):
    # returnerer et tilfældigt N*N grid
    return np.random.choice(vals, N*N, p=[0.02, 0.02, 0.96]).reshape(N, N)

def update(frameNum, img, imgPay, grid, N, payoffs, hypCoop, hypDef, hypDead, axHyp):

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

                # success baseret på en logistisk kurve (sigmoid kurve), hvis uafhængige variabel er differencen i fitness (payoff)
                difPay = pGrid[choice[0],choice[1]] - pGrid[i,j]
                sigmoid = 1 / (1 + math.exp(-(payoffs[0] - 1) * difPay))

                # print('payoff ', pGrid[choice[0],choice[1]], ' || ', pGrid[i,j])
                # print('dif, sig ', difPay, ' || ', sigmoid)

                if sigmoid > random.random():
                    newGrid[i,j] = grid[choice[0], choice[1]]

    
    coopCount = np.count_nonzero(newGrid == COOP)/(N*N)
    defCount = np.count_nonzero(newGrid == DEFECTOR)/(N*N)
    deadCount = 1 - coopCount - defCount
        
    # opdater data
    img.set_data(newGrid)
    grid[:] = newGrid[:]

    imgPay.set_data(pGrid)

    hypx.append(frameNum)
    hypCoopy.append(coopCount)
    hypDefy.append(defCount)
    hypDeady.append(deadCount)
    axHyp.set_xlim([-1, frameNum])

    print(axHyp.texts)
    for t in axHyp.texts:
        t.remove()

    axHyp.text(frameNum*0.8, coopCount+0.05,f'Stabil andel: {sum(hypCoopy[-500:])/500}', fontsize=10)
    axHyp.text(frameNum*0.8, defCount+0.05,f'Stabil andel: {sum(hypDefy[-500:])/500}', fontsize=10)


    # print(axHyp.get_children())
    # if isinstance(axHyp.get_children()[2], LineCollection):
    #     axHyp.get_children()[2].remove()
    # plt.text(0, coopCount+20, f"coopCount: {coopCount}", fontsize=10)

    hypCoop.set_data(hypx, hypCoopy)
    hypDef.set_data(hypx, hypDefy)
    hypDead.set_data(hypx, hypDeady)

    # axHyp.hlines(y=coopCount, xmin=0, xmax=frameNum)

    return img, imgPay, hypCoop, hypDef,


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
    for coopCount, entry in enumerate(vals):
        clr = cmap(entry)
        print(clr)
        axSnow.plot(0,0,'-',color=clr, label=['KOOPERATIV','SVINDLER','DØD'][coopCount])    

    img = axSnow.imshow(grid, cmap=cmap, interpolation='nearest')
    startPay = np.zeros((N,N))
    startPay[0,0] = payoffs[0]*8
    imgPay = axPay.imshow(startPay, cmap='coolwarm', interpolation='nearest')
    cbar = plt.colorbar(imgPay, ax=axPay)
    cbar.set_label('Udbytte')

    hypCoop, = axHyp.plot(0,0, label='KOOPERATIV')
    hypDef, = axHyp.plot(0,0, label='SVINDLER')
    hypDead, = axHyp.plot(0,0, label='DØD')
    axSnow.legend(loc='upper right', bbox_to_anchor=(1.32,1.015))
    # axSnow.legend(bbox_to_anchor=(1.05, 1), loc=2)

    plt.suptitle(f'Rumligt struktureret snowdrift spil simulering\nr={args.r}; b={b}, c={c}; T={payoffs[0]}, R=1, S={payoffs[1]}, P=0')
    axSnow.set_title('Snowdrift gitter')
    axPay.set_title('Udbytte gitter')
    axHyp.set_title('Andel af kooperatører over tid')
    axHyp.legend()
    axHyp.set_ylim(0,1)
    axHyp.yaxis.tick_right()

    axHyp.set_xlabel('Framenumber/Generation')
    axHyp.set_ylabel('Andel af population')

    fig.canvas.manager.full_screen_toggle()

    ani = animation.FuncAnimation(fig, update, fargs=(img, imgPay, grid, N, payoffs, hypCoop, hypDef, hypDead, axHyp,), 
                                  interval=updateInterval, 
                                  save_count=500)


    # antal frames?
    # sæt output fil
    if args.movfile:
        ani.save(args.mavfile, fps=30, extra_args=['-vcodec', 'libx264'])
    
    plt.show()

if __name__ == '__main__':
    main()