import neat
import random
from time import sleep as wait
import os
import pygame
import pickle

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

def AddRectangle(x, y, r, g, b, screen):
    pygame.draw.rect(screen, (r, g, b),(x+1, y+1, 96, 96))

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Checkpointer.restore_checkpoint("neat_data_5x5/neat-checkpoint-6212")

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(Game, 1)
    with open("winner_5x5.txt", "wb") as f:
        pickle.dump(winner, f)

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

def EatApple(timeSinceEating, headPos, snakePos, applePos, length, obstacles, portals): # Lengthen the snake if the apple is eaten and choose a new position for it
    if headPos in applePos:
        i = applePos.index(headPos)
        length += 1
        applePos[i] = ChooseApplePosition(snakePos, applePos, obstacles, portals)
        timeSinceEating = 0
    else:
        snakePos.remove(snakePos[0])
        timeSinceEating += 1
    return applePos, length, timeSinceEating

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

def PrintBoard(board, screen, darkMode, portalUsed): # Clear the terminal and print the new board
    for i, content in enumerate(board):
        coords = IndexToCoordinates(i)
        coords = [coords[0] * 100, coords[1] * 100]
        if content == 1:
            AddRectangle(coords[0], coords[1], 255, 0, 0, screen)
        elif content == 4:
            AddRectangle(coords[0], coords[1], 50, 50, 50, screen)
        elif content == 2:
            AddRectangle(coords[0], coords[1], 0, 255, 0, screen)
        elif content == 3:
            AddRectangle(coords[0], coords[1], 0, 155, 0, screen)
        elif content == 5:
            if portalUsed:
                if darkMode:
                    AddRectangle(coords[0], coords[1], 155, 155, 55, screen)
                else:
                    AddRectangle(coords[0], coords[1], 100, 155, 200, screen)
            else:
                AddRectangle(coords[0], coords[1], 100, 0, 200, screen)
        else:
            if darkMode:
                AddRectangle(coords[0], coords[1], 0, 0, 0, screen)
            else:
                AddRectangle(coords[0], coords[1], 255, 255, 255, screen)

    pygame.display.update()
    
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
        net = neat.nn.FeedForwardNetwork.create(g[1], config)
        pygame.init()
        screen = pygame.display.set_mode((500, 500))
        pygame.display.set_caption('Snake Game')

        numOfApples = 1
        obstacles = []
        portals = []

        board = []
        length = 1
        headPos = [8, 8]
        snakePos = [headPos.copy()]
        applePos = [[9, 8]]
        timeSinceEating = 0
        for i in range(numOfApples-1):
            applePos.append(ChooseApplePosition(snakePos, applePos, obstacles, portals))
        direction = [1, 0]

        while True:
            darkMode = False
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
            portalUsed = False
            for pos in snakePos:
                if pos in portals:
                    portalUsed = True
            applePos, length, timeSinceEating = EatApple(timeSinceEating, headPos, snakePos, applePos, length, obstacles, portals) # Update length and apple position

            if CheckDeath(headPos, snakePos, obstacles): # Check for death and end the game if neccessary
                break
            board = UpdateBoard(headPos, applePos, snakePos, board, obstacles, portals)
            direction = UpdateDirection(board, net)
            PrintBoard(board, screen, darkMode, portalUsed)
            wait(2)
            if direction == [2, 2] or timeSinceEating > 100: # End the game if no more move is possible
                break
        g[1].fitness = float(length - 2)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)