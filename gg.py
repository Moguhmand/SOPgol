import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection

# setup values
ON = 255
OFF = 0
hypx = []
hypy = []
hline = []
vals = [ON, OFF]

def randomGrid(N):
    # returnerer et tilfældigt N*N grid
    return np.random.choice(vals, N*N, p=[0.2, 0.8]).reshape(N, N)

def update(frameNum, img, grid, N, hyp, axr):

    count = 0
    # kopier grid
    # udregninger sker linje for linje
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):

            # udregn 8-nabo sum vha. toroidal boundary conditions - x og y wrapper om, pacman style.
            # så simuleringen sker på en torodal(=donut) overflade
            total = int((grid[i, (j-1)%N] + grid[i, (j+1)%N] + 
                         grid[(i-1)%N, j] + grid[(i+1)%N, j] + 
                         grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] + 
                         grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N])/255) 
            
            # anvend Conway's regler
            if grid[i, j] == ON:
                if (total < 2) or (total > 3):
                    newGrid[i, j] = OFF
            elif total == 3:
                newGrid[i, j] = ON
                count += 1
    
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
    plt.text(0, count+20, f"count: {count}", fontsize=10)

    hyp.set_data(hypx, hypy)
    axr.hlines(y=count, xmin=0, xmax=frameNum)

    return img, hyp,


# main() funktion
def main():

    # kommandolinje argumenter findes i sys.argv[1], sys.argv[2] osv.
    # sys.argv[0] er script navnet. Denne ignoreres
    # parse argumenter
    parser = argparse.ArgumentParser(description="Runs Conway's Game of Life simulation.")

    # tilføj argumenter
    parser.add_argument('--grid-size', dest='N', required=False) 
    parser.add_argument('--mov-file', dest='movfile', required=False) 
    parser.add_argument('--interval', dest='interval', required=False) 
    args = parser.parse_args() 

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

    img = axl.imshow(grid, interpolation='nearest')
    hyp, = axr.plot(0,0)

    ani = animation.FuncAnimation(fig, update, fargs=(img, grid, N, hyp, axr,), 
                                  interval=updateInterval, 
                                  save_count=500)
    

    # antal frames?
    # sæt output fil
    if args.movfile:
        ani.save(args.mavfile, fps=30, extra_args=['-vcodec', 'libx264'])
    
    plt.show()

if __name__ == '__main__':
    main()