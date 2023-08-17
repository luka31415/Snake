# Import packages
import random
import matplotlib.pyplot as plt

class Dijsktra:
    def ValidNeighbor(pos):
        if not (-1 < pos[0] < 16):
            return False
        if not (-1 < pos[1] < 16):
            return False
        return True

    def GenerateNeighbors(self, pos):
        possibleNeighbors = [[pos[0], pos[1] + 1], [pos[0], pos[1] - 1], [pos[0] + 1, pos[1]], [pos[0] - 1, pos[1]]]
        neighborList = []
        for neighbor in possibleNeighbors:
            if self.ValidNeighbor(neighbor):
                neighborList.append(neighbor)
        return neighborList

    def GenerateDijkstraValues(self, applePos, snakePos, obstacles, portals):
        values = [128] * 256
        for pos in snakePos:
            values[(pos[0] + 16 * (pos[1] - 1)) - 1] = 129
            if pos in portals:
                values[(portals[portals.index(pos) - 1][0] + 16 * (portals[portals.index(pos) - 1][1] - 1)) - 1] = 129
        fields = applePos.copy()
        for pos in applePos:
            values[pos[0] + 16 * pos[1] - 17] = 0
        while fields != []:
            for pos in fields.copy():
                if pos in portals:
                    pos = portals[portals.index(pos) - 1].copy()
                neighbors = self.GenerateNeighbors(self, pos)
                for neighbor in neighbors:
                    if neighbor in obstacles:
                        values[neighbor[0] + 16 * (neighbor[1] - 1) - 1] = 200
                    elif values[neighbor[0] + 16 * (neighbor[1] - 1) - 1] == 128:
                        if neighbor in portals:
                            values[neighbor[0] + 16 * (neighbor[1] - 1) - 1] = values[pos[0] + 16 * (pos[1] - 1) - 1] + 1
                            neighbor = portals[portals.index(neighbor) - 1].copy()
                        values[neighbor[0] + 16 * (neighbor[1] - 1) - 1] = values[pos[0] + 16 * (pos[1] - 1) - 1] + 1
                        if neighbor in portals:
                            neighbor = portals[portals.index(neighbor) - 1].copy()
                        fields.append(neighbor)
                if pos in portals:
                    pos = portals[portals.index(pos) - 1].copy()
                fields.remove(pos)
            oldFields = fields.copy()
            fields = []
            for field in oldFields:
                if not field in fields:
                    fields.append(field)
        for pos in applePos:
            values[pos[0] + 16 * (pos[1] - 1) - 1] = 0
        for pos in snakePos:
            values[pos[0] + 16 * (pos[1] - 1) - 1] = 129
        return values

    def GenerateInput(self, board, direction): # Choose an appropriate input if possible and if not, choose a random one
        obstacles = []
        portals = []
        snakePos = []
        applePos = []
        headPos = []

        for i, content in enumerate(board):
            if content == "#":
                headPos = IndexToCoordinates(i)
                snakePos.append(IndexToCoordinates(i))
            elif content == "*":
                applePos.append(IndexToCoordinates(i))
            elif content == "?":
                obstacles.append(IndexToCoordinates(i))
            elif content == "%":
                portals.append(IndexToCoordinates(i))
            elif content == "+":
                snakePos.append(IndexToCoordinates(i))

        values = self.GenerateDijkstraValues(self, applePos, snakePos, obstacles, portals)
        headNeighbors = self.GenerateNeighbors(self, headPos)
        inputValue = values[headNeighbors[0][0] + 16 * (headNeighbors[0][1] - 1) - 1]
        inputNeighbor = headNeighbors[0]
        for neighborPos in headNeighbors:
            neighborValue = values[neighborPos[0] + 16 * (neighborPos[1] - 1) - 1]
            if neighborValue < inputValue:
                inputValue = neighborValue
                inputNeighbor = neighborPos
        input = [inputNeighbor[0] - headPos[0], inputNeighbor[1] - headPos[1]]
        return input

class Hamiltonian:
    def GenerateInput(self, board, direction):
        rightPos = [[0, 15], [1, 1], [2, 15], [3, 1], [4, 15], [5, 1], [6, 15], [7, 1], [8, 15], [9, 1], [10, 15], [11, 1], [12, 15], [13, 1], [14, 15]]
        upPos = [[1, 15], [3, 15], [5, 15], [7, 15], [9, 15], [11, 15], [13, 15], [15, 15]]
        leftPos = [[15, 0]]
        downPos = [[0, 0], [2, 1], [4, 1], [6, 1], [8, 1], [10, 1], [12, 1], [14, 1]]
        headPos = IndexToCoordinates(board.index("#"))

        if headPos == [9, 8]:
            return [0, -1]
        if headPos in rightPos:
            return [1, 0]
        if headPos in leftPos:
            return [-1, 0]
        if headPos in upPos:
            return [0, -1]
        if headPos in downPos:
            return [0, 1]
        return direction

class Random:
    def GenerateInput(self, board, direction): # Make sure that the snake can't do a 180 turn and generate new inputs
        inputs = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        inputs.remove([direction[0] * -1, direction[1] * -1])

        headPos = IndexToCoordinates(board.index("#"))

        while inputs != []:
            input = random.choice(inputs)
            newHeadPos = [headPos[0] + input[0], headPos[1] + input[1]]
            if not board[newHeadPos[0] + 16 * newHeadPos[1]] in ["+", "#"]:
                return input
            inputs.remove(input)
        return random.choice([[1, 0], [-1, 0], [0, 1], [0, -1]])

class Simple:
    def GenerateClosestApple(applePos, headPos):
        dist = []

        for pos in applePos:
            x = abs(pos[0] - headPos[0])
            y = abs(pos[1] - headPos[1])
            dist.append(x + y)
        
        return dist.index(min(dist))

    def CheckPotentialDeath(newHeadPos, snakePos, obstacles): # For a given input, check if the snake would die if it made that move
        if newHeadPos in snakePos or newHeadPos in obstacles:
            return True

        isOffScreen = not (-1 < newHeadPos[0] < 16) or not (-1 < newHeadPos[1] < 16)
        if isOffScreen:
            return True
        return False

    def ValidateInput(self, input, direction, headPos, snakePos, obstacles): # Make shure the snake doesn't do a 180 turn or would die for a given input
        if input == [-1 * direction[0], -1 * direction[1]] or self.CheckPotentialDeath([headPos[0] + input[0], headPos[1] + input[1]], snakePos, obstacles):
            return False
        return True

    def ChooseInput(self, applePos, headPos, direction, snakePos, obstacles): # Choose the input that would get the snake closest to the apple
        input = [0, 0]
        if applePos[0] < headPos[0]:
            input[0] = -1
        elif applePos[0] > headPos[0]:
            input[0] = 1
        else:
            if applePos[1] < headPos[1]:
                input[1] = -1
            elif applePos[1] > headPos[1]:
                input[1] = 1
        if not self.ValidateInput(self, input, direction, headPos, snakePos, obstacles):
            input = [0, 0]
            if applePos[1] < headPos[1]:
                input[1] = -1
            elif applePos[1] > headPos[1]:
                input[1] = 1
            else:
                if applePos[0] < headPos[0]:
                    input[0] = -1
                elif applePos[0] > headPos[0]:
                    input[0] = 1
        return input

    def GenerateInput(self, board, direction): # Choose an appropriate input if possible and if not, choose a random one
        obstacles = []
        snakePos = []
        applePos = []
        headPos = []

        for i, content in enumerate(board):
            if content == "#":
                headPos = IndexToCoordinates(i)
                snakePos.append(IndexToCoordinates(i))
            elif content == "*":
                applePos.append(IndexToCoordinates(i))
            elif content == "?":
                obstacles.append(IndexToCoordinates(i))
            elif content == "+":
                snakePos.append(IndexToCoordinates(i))
        
        targetApple = applePos[self.GenerateClosestApple(applePos, headPos)]

        choices = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        input = self.ChooseInput(self, targetApple, headPos, direction, snakePos, obstacles)
        while not self.ValidateInput(self, input, direction, headPos, snakePos, obstacles):
            if len(choices) > 0:
                input = random.choice(choices)
                choices.remove(input)
            else:
                return [2, 2]
        return input

def IndexToCoordinates(i):
    x = i % 16
    y = (i - i % 16) / 16
    return [int(x), int(y)]

def ChooseApplePosition(snakePos, applePos, obstacles, portals): # Choose a new position for the apple after it is eaten
    pos = [random.randint(0, 15), random.randint(0, 15)]
    while pos in snakePos or pos in applePos or pos in obstacles or pos in portals:
        pos = [random.randint(0, 15), random.randint(0, 15)]
    return pos

def EatApple(headPos, snakePos, applePos, length, obstacles, portals): # Lengthen the snake if the apple is eaten and choose a new position for it
    if headPos in applePos:
        i = applePos.index(headPos)
        length += 1
        applePos[i] = ChooseApplePosition(snakePos, applePos, obstacles, portals)
    else:
        snakePos.remove(snakePos[0])
    return applePos, length

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

def RunGames(numOfGames, bot, numOfApples, obstacles, portals):
    games = []
    for i in range(numOfGames):
        print(i)
        games.append(Game(bot, numOfApples, obstacles, portals))
    return games

def ProcessData(games):
    distribution = [0] * (max(games)+1)
    for game in games:
        distribution[game] += 1
    average = Average(distribution)
    return average, distribution

def Average(distribution):
    expectedValue = 0
    numOfGames = 0
    for index, score in enumerate(distribution):
        expectedValue += index * score
        numOfGames += score
    expectedValue /= numOfGames
    return expectedValue

def ProcessGames(games):
    average, distribution = ProcessData(games)
    print(average)
    print(distribution)
    xValues = []
    for i in range(len(distribution)):
        xValues.append(i)
    plt.bar(xValues, height=distribution)
    plt.show()
    return average, distribution

def SaveResults(numOfGames, average, distribution, fileLocation):
    string = f"Average: {average}\n\nScores:\n"
    for index, value in enumerate(distribution):
        string += f"{index}: {value}\n"
    string += f"\nTotal: {numOfGames}"
    WriteToFile(string, fileLocation)

def WriteToFile(string, fileLocation):
    with open(fileLocation, "w") as file:
        file.write(string)

def UpdateBoard(headPos, applePos, snakePos, board, obstacles, portals): # Update all the fields on the boards
    for y in range(0, 16):
        for x in range(0, 16):
            pos = [x, y]
            if pos in applePos:    content = "*"
            elif pos in obstacles: content = "?"
            elif pos in portals:   content = "%"
            elif pos == headPos:   content = "#"
            elif pos in snakePos:  content = "+"
            else:                  content = "0"
            board.append(content)

def Game(bot, numOfApples, obstacles, portals): # Play one game at a time
    board = []
    length = 1
    headPos = [8, 8]
    snakePos = [headPos.copy()]
    applePos = [[9, 8]]
    for i in range(numOfApples-1):
        applePos.append(ChooseApplePosition(snakePos, applePos, obstacles, portals))
    direction = [1, 0]

    while True:
        # Update the position of the snake
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
        applePos, length = EatApple(headPos, snakePos, applePos, length, obstacles, portals) # Update length and apple position

        if CheckDeath(headPos, snakePos, obstacles): # Check for death and end the game if neccessary
            break
        UpdateBoard(headPos, applePos, snakePos, board, obstacles, portals)
        direction = bot.GenerateInput(bot, board, direction) # Update the direction with the generated one
        if direction == [2, 2]: # End the game if no more move is possible
            break
    return length - 2

def Main(bot, numOfApples, obstacles, portals):
    numOfGames = 100000
    games = RunGames(numOfGames, bot, numOfApples, obstacles, portals)
    average, distribution = ProcessGames(games)
    SaveResults(numOfGames, average, distribution, "data/dijkstra_bot/square/results.txt")

if __name__ == '__main__':
    bot = Dijsktra
    numOfApples = 1
    obstacles = []
    portals = []

    try:
        Main(bot, numOfApples, obstacles, portals) # Run the main function
    except:
        pass