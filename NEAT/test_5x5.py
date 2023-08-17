# Import packages
import random
from time import sleep as wait
import pygame
import neat
import pandas

config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, "config-feedforward")

# with open("winner.txt", "rb") as f:
    # genome = pickle.load(f)
genome = pandas.read_pickle(r"winner_5x5.txt")
genomes = [(1, genome)]

def GenerateInput(net, board, direction):
    inputs = tuple(board)
    output = net.activate(inputs)[0]
    print(output)
    if output < -0.5:
        directionOut = [-1, 0]
    elif output < 0:
        directionOut = [1, 0]
    elif output < 0.5:
        directionOut = [0, 1]
    else:
        directionOut = [0, -1]
    return directionOut

def ChooseApplePosition(snakePos, applePos, obstacles, portals): # Choose a new position for the apple after it is eaten
    pos = [random.randint(0, 4), random.randint(0, 4)]
    while pos in snakePos or pos in applePos or pos in obstacles or pos in portals:
        pos = [random.randint(0, 4), random.randint(0, 4)]
    return pos

def EatApple(timeSinceEating, headPos, snakePos, applePos, length, obstacles, portals): # Lengthen the snake if the apple is eaten and choose a new position for it
    if headPos in applePos:
        i = applePos.index(headPos)
        length += 1
        applePos[i] = ChooseApplePosition(snakePos, applePos, obstacles, portals)
        print(f"Score: {length - 2}")
        timeSinceEating = 0
    else:
        snakePos.remove(snakePos[0])
        timeSinceEating += 1
    return applePos, length, timeSinceEating

def UpdateBoard(headPos, applePos, snakePos, board, obstacles, portals): # Update all the fields on the board
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

def IndexToCoordinates(i):
    x = i % 5
    y = (i - i % 5) / 5
    return [int(x), int(y)]

def PrintBoard(board, screen, darkMode, portalUsed): # Clear the terminal and print the new board
    for i, content in enumerate(board):
        col = []
        coords = IndexToCoordinates(i)
        coords = [coords[0] * 100, coords[1] * 100]
        if content == 1:
            col = [255, 0, 0]
        elif content == 4:
            col = [50, 50, 50]
        elif content == 2:
            col = [0, 255, 0]
        elif content == 3:
            col = [0, 155, 0]
        elif content == 5:
            if portalUsed:
                if darkMode:
                    col = [45, 45, 55]
                else:
                    col = [100, 45, 200]
            else:
                col = [100, 0, 200]
        else:
            if darkMode:
                col = [0, 0, 0]
            else:
                col = [255, 255, 255]
        AddRectangle(coords[0], coords[1], col[0], col[1], col[2], screen)

    pygame.display.update()

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

def AddRectangle(x, y, r, g, b, screen):
    pygame.draw.rect(screen, (r, g, b),(x+1, y+1, 96, 96))

def Main(numOfApples, obstacles, portals, darkMode):
    net = neat.nn.FeedForwardNetwork.create(genomes[0][1], config)
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    pygame.display.set_caption('Snake Game')

    length = 1
    headPos = [2, 3]
    snakePos = [headPos.copy()]
    applePos = [[3, 3]]
    for i in range(numOfApples-1):
        applePos.append(ChooseApplePosition(snakePos, applePos, obstacles, portals))
    direction = [1, 0]
    timeSinceEating = 0

    while True:
        board = []
        # Update the position of the snake
        headPos[0] += direction[0]
        headPos[1] += direction[1]
        # headPos = [headPos[0] % 5, headPos[1] % 5]
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

        if CheckDeath(headPos, snakePos, obstacles) or timeSinceEating > 100: # Check for death and end the game if neccessary
            break
        UpdateBoard(headPos, applePos, snakePos, board, obstacles, portals) # Update the board with all the fields
        PrintBoard(board, screen, darkMode, portalUsed) # Print the board to the terminal
        direction = GenerateInput(net, board, direction)
        wait(1) # Wait 0.2 seconds for visibility
    print(f"You lost! Your score was {length-2}") # Print the score after the game is lost

if __name__ == '__main__':
    numOfApples = 1
    obstacles = []
    portals = []
    darkMode = False
    Main(numOfApples, obstacles, portals, darkMode) # Run the main function