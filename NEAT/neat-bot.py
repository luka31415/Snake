import neat
import random
import pickle
import os
import matplotlib.pyplot as plt

def UpdateDirection(headPos, applePos, neighbors, direction, net):
    inputs = tuple(neighbors)
    x = applePos[0][0] - headPos[0]
    y = applePos[0][1] - headPos[1]
    inputs += (x, y,)
    if direction == [-1, 0]:
        inputs += (1,)
    elif direction == [1, 0]:
        inputs += (2,)
    elif direction == [0, -1]:
        inputs += (3,)
    elif direction == [0, 1]:
        inputs += (4,)
    output = net.activate(inputs)[0]
    if output < -0.5:
        directionOut = [-1, 0]
    elif output < 0:
        directionOut = [1, 0]
    elif output < 0.5:
        directionOut = [0, 1]
    else:
        directionOut = [0, -1]
    return directionOut

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Create the population, which is the top-level object for a NEAT run.
    # p = neat.Population(config)
    p = neat.Checkpointer.restore_checkpoint("neat_data/neat-checkpoint-1899")

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(filename_prefix="neat_data/neat-checkpoint-"))

    winner = p.run(Game, 3000)
    with open("winner.txt", "wb") as f:
        pickle.dump(winner, f)

    # plt.plot(mean_fitnesses)
    # plt.savefig("mean.png")
    # plt.show()
    # plt.plot(best_fitnesses)
    # plt.savefig("best.png")
    # plt.show()

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

def IndexToCoordinates(i):
    x = i % 16
    y = (i - i % 16) / 16
    return [int(x), int(y)]

def ChooseApplePosition(snakePos, applePos, obstacles, portals): # Choose a new position for the apple after it is eaten
    pos = [random.randint(0, 15), random.randint(0, 15)]
    while pos in snakePos or pos in applePos or pos in obstacles or pos in portals:
        pos = [random.randint(0, 15), random.randint(0, 15)]
    return pos

def EatApple(fitness, timeSinceEating, headPos, snakePos, applePos, length, obstacles, portals): # Lengthen the snake if the apple is eaten and choose a new position for it
    if headPos in applePos:
        i = applePos.index(headPos)
        length += 1
        applePos[i] = ChooseApplePosition(snakePos, applePos, obstacles, portals)
        fitness += 1/timeSinceEating
        timeSinceEating = 1
    else:
        snakePos.remove(snakePos[0])
        timeSinceEating += 1
    return applePos, length, timeSinceEating, fitness

def CheckDeath(headPos, snakePos, obstacles): # Check if the snake is outside of the board or intersecting itself
    bodyPos = snakePos.copy()
    bodyPos.remove(headPos)
    if headPos in bodyPos:
        return True
    if headPos in obstacles:
        return True
    
    isOffScreen = not (-1 < headPos[0] < 16) or not (-1 < headPos[1] < 16)
    if isOffScreen:
        return True
    return False
    
def Mean(lst):
    total = 0
    for x in lst:   
        total += x
    total /= len(lst)
    return total

def GenerateNeighbors(pos, snakePos):
        possibleNeighbors = [[(pos[0] - 1) % 16, pos[1] % 16], [(pos[0] + 1) % 16, pos[1] % 16], [pos[0] % 16, (pos[1] - 1) % 16], [pos[0] % 16, (pos[1] + 1) % 16]]
        neighborList = []
        for neighbor in possibleNeighbors:
            if neighbor in snakePos:
                neighborList.append(1)
            else:
                neighborList.append(0)
        return neighborList

def UpdateBoard(headPos, applePos, snakePos, board, obstacles, portals): # Update all the fields on the board
    board = []
    for y in range(0, 16):
        for x in range(0, 16):
            pos = [x, y]
            if pos in applePos:    content = 1
            elif pos in obstacles: content = 4
            elif pos in portals:   content = 5
            elif pos == headPos:   content = 2
            elif pos in snakePos:  content = 3
            else:                  content = 0
            board.append(content)
    return board

def Game(genomes, config): # Play one game at a time
    for g in genomes:
        fitnesses = []
        net = neat.nn.FeedForwardNetwork.create(g, config)
        for i in range(5):
            fitness = -1

            numOfApples = 1
            obstacles = []
            portals = []

            board = []
            length = 1
            headPos = [8, 8]
            snakePos = [headPos.copy()]
            applePos = [[9, 8]]
            timeSinceEating = 1
            for i in range(numOfApples-1):
                applePos.append(ChooseApplePosition(snakePos, applePos, obstacles, portals))
            direction = [1, 0]

            while True:
                # Update the position of the snake
                headPos[0] += direction[0]
                headPos[1] += direction[1]
                # headPos = [headPos[0] % 16, headPos[1] % 16]
                try:
                    teleported = False
                    if headPos == portals[0]:
                        headPos = portals[1].copy()
                        teleported = True
                    if headPos == portals[1] and not teleported:
                        headPos = portals[0].copy()
                except IndexError:
                    pass
                snakePos.append(headPos.copy())
                applePos, length, timeSinceEating, fitness = EatApple(fitness, timeSinceEating, headPos, snakePos, applePos, length, obstacles, portals) # Update length and apple position

                if CheckDeath(headPos, snakePos, obstacles): # Check for death and end the game if neccessary
                    break
                board = UpdateBoard(headPos, applePos, snakePos, board, obstacles, portals)
                neighbors = GenerateNeighbors(headPos, snakePos)
                oldDirection = direction.copy()
                direction = UpdateDirection(headPos, applePos, neighbors, direction, net)
                if oldDirection == [-1 * direction[0], -1 * direction[1]]:
                    break
                if timeSinceEating > 100: # End the game if no more move is possible
                    fitness -= 5
                    break
            fitnesses.append(fitness)
            if length-2 > 1:
                print(length-2)
        g[1].fitness = Mean(fitnesses)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)