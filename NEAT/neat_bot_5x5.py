import neat
import random
import pickle
import os

def UpdateDirection(board, net):
    inputs = tuple(board)
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

    # p = neat.Population(config)
    p = neat.Checkpointer.restore_checkpoint("neat_data_5x5/neat-checkpoint-6212")


    p.add_reporter(neat.Checkpointer(generation_interval=10000, filename_prefix="neat_data_5x5/neat-checkpoint-"))

    winner = p.run(Game)
    open("winner_5x5.txt", "w").close()
    with open("winner_5x5.txt", "wb") as f:
        pickle.dump(winner, f)

    print('\nBest genome:\n{!s}'.format(winner))

def IndexToCoordinates(i):
    x = i % 5
    y = (i - i % 5) / 5
    return [int(x), int(y)]

def ChooseApplePosition(snakePos, applePos, obstacles, portals): # Choose a new position for the apple after it is eaten
    pos = [random.randint(0, 4), random.randint(0, 4)]
    while pos in snakePos or pos in applePos or pos in obstacles or pos in portals:
        pos = [random.randint(0, 4), random.randint(0, 4)]
    return pos

def EatApple(fitness, timeSinceEating, headPos, snakePos, applePos, length, obstacles, portals): # Lengthen the snake if the apple is eaten and choose a new position for it
    if headPos in applePos:
        i = applePos.index(headPos)
        length += 1
        applePos[i] = ChooseApplePosition(snakePos, applePos, obstacles, portals)
        fitness += 1
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
    
    isOffScreen = not (-1 < headPos[0] < 5) or not (-1 < headPos[1] < 5)
    if isOffScreen:
        return True
    return False
    
def Mean(lst):
    total = 0
    for x in lst:   
        total += x
    total /= len(lst)
    return total

def UpdateBoard(headPos, applePos, snakePos, board, obstacles, portals): # Update all the fields on the board
    board = []
    for y in range(0, 5):
        for x in range(0, 5):
            pos = [x, y]
            if pos in applePos:    content = 1
            elif pos in obstacles: content = 4
            elif pos in portals:   content = 5
            elif pos == headPos:   content = 2
            elif pos in snakePos:  content = 3
            else:                  content = 0
            board.append(content)
    return board

def Game(genomes, config):
    for g in genomes:
        fitnesses = []
        net = neat.nn.FeedForwardNetwork.create(g[1], config)
        for i in range(5):
            fitness = -1

            numOfApples = 1
            obstacles = []
            portals = []

            board = []
            length = 1
            headPos = [2, 3]
            snakePos = [headPos.copy()]
            applePos = [[3, 3]]
            timeSinceEating = 1
            for i in range(numOfApples-1):
                applePos.append(ChooseApplePosition(snakePos, applePos, obstacles, portals))
            direction = [1, 0]

            while True:
                headPos[0] += direction[0]
                headPos[1] += direction[1]
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
                oldDirection = direction.copy()
                direction = UpdateDirection(board, net)
                if oldDirection == [-1 * direction[0], -1 * direction[1]]:
                    break
                if timeSinceEating > 100:
                    fitness -= 5
                    break
            fitnesses.append(fitness)
            print(fitness)
        g[1].fitness = Mean(fitnesses)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)