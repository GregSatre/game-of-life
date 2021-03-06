import pygame, sys
from pygame.locals import *

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

FPS = 5

CELL_SIZE = 30
assert WINDOW_WIDTH%CELL_SIZE == 0
assert WINDOW_HEIGHT%CELL_SIZE == 0
CELL_WIDTH = WINDOW_WIDTH//CELL_SIZE
CELL_HEIGHT = WINDOW_HEIGHT//CELL_SIZE

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = WHITE

def main():
    global FPSCLOCK, SCREEN

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Game of Life')
    # Get initial cell positions
    cell_positions = initializeGame()
    # Run game on those positions
    runGame(cell_positions, [])

def initializeGame():
    """Checks for user mouse clicks and updates cell_positions accordingly. Returns game's initial state"""
    # Positions of upper left corners of cells on the grid. List of tuples
    cell_positions = set()
    # Main game loop
    while True:
        # Event handling loop
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                cell_x = mouse_x - mouse_x%CELL_WIDTH
                cell_y = mouse_y - mouse_y%CELL_HEIGHT
                cell_pos = (cell_x, cell_y)
                if cell_pos in cell_positions:
                    cell_positions.remove(cell_pos)
                else:
                    cell_positions.add(cell_pos)
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return cell_positions
                elif event.key == K_ESCAPE:
                    terminate()

        SCREEN.fill(BGCOLOR)
        drawGrid()
        drawCells(cell_positions)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def runGame(cell_positions, history):
    """Using initial state as input and a set of rules updates cell_positions and displays the result. Infinite loop"""
    while True:
        # Event handling loop
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_SPACE:
                    pauseGame(cell_positions, history)
                elif event.key == K_r:
                    resetGame()

        history.append(list(cell_positions))
        cell_positions = updateCells(cell_positions)

        SCREEN.fill(BGCOLOR)
        drawGrid()
        drawCells(cell_positions)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def resetGame():
    # Get initial cell positions
    cell_positions = initializeGame()
    # Run game on those positions
    runGame(cell_positions, [])

def pauseGame(cell_positions, history):
    while True:
        # Event handling loop
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_SPACE:
                    runGame(cell_positions, history)
                elif event.key == K_RIGHT:
                    history.append(list(cell_positions))
                    cell_positions = updateCells(cell_positions)
                elif event.key == K_LEFT:
                    cell_positions = set(history.pop())
                elif event.key == K_r:
                    resetGame()

        SCREEN.fill(BGCOLOR)
        drawGrid()
        drawCells(cell_positions)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def updateCells(cell_positions):
    """Use rules of the game of life to update the cell positions"""
    # Build a set of canditates for live cells at the next generation, instead of looking through the whole grid
    # These will be dead neighbours of living cells
    possible_future_cells = set()
    # Make sets of cells to add and remove at the end of the check
    cells_remove = set()
    cells_add = set()
    for cell in cell_positions:
        # Get adjacent squares
        neighbours_dict = cellNeighbours(cell)
        number_live_neighbours = 0
        # Check which of these corresponds to another living cell
        for square in neighbours_dict.values():
            if square in cell_positions:
                number_live_neighbours+=1
            else:
                possible_future_cells.add(square)

        # Any live cell with fewer than two live neighbours dies, as if caused by under-population
        if number_live_neighbours<2:
            cells_remove.add(cell)
        # Any live cell with two or three live neighbours lives on to the next generation
        # do nothing
        # Any live cell with more than three live neighbours dies, as if by overcrowding
        elif number_live_neighbours>3:
            cells_remove.add(cell)
    # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction
    for cell_candidate in possible_future_cells:
        cell_candidate_neighbours = cellNeighbours(cell_candidate).values()
        # Count number of live neighbours
        count = 0
        for square in cell_candidate_neighbours:
            if square in cell_positions:
                count+=1
        if count == 3:
            cells_add.add(cell_candidate)
    # Update cell_positions by removing dead cells and adding new-born cells
    for cell in cells_add:
        cell_positions.add(cell)
    for cell in cells_remove:
        cell_positions.remove(cell)
    # Return the update live cell list
    return cell_positions

def cellNeighbours((cell_x,cell_y)):
    """Get 4 adjacent squares. May not be in grid"""
    dict = {}
    dict["neighbour_up"] = (cell_x,  cell_y - CELL_HEIGHT)
    dict["neighbour_down"] = (cell_x, cell_y + CELL_HEIGHT)
    dict["neighbour_left"] = (cell_x - CELL_WIDTH, cell_y)
    dict["neighbour_right"] = (cell_x + CELL_WIDTH, cell_y)
    dict["neighbour_up_left"] = (cell_x - CELL_WIDTH, cell_y - CELL_HEIGHT)
    dict["neighbour_up_right"] = (cell_x + CELL_WIDTH, cell_y - CELL_HEIGHT)
    dict["neighbour_down_left"] = (cell_x - CELL_WIDTH, cell_y + CELL_HEIGHT)
    dict["neighbour_down_right"] = (cell_x + CELL_WIDTH, cell_y + CELL_HEIGHT)
    keys_to_delete = []
    for key,value in dict.iteritems():
        if not inWindow(value):
           keys_to_delete.append(key)
    for key in keys_to_delete:
        del dict[key]
    return dict

def drawGrid():
    for x in range(0,WINDOW_WIDTH+CELL_WIDTH,CELL_WIDTH):
        pygame.draw.line(SCREEN, BLACK, (x,0), (x,WINDOW_HEIGHT))
    for y in range(0,WINDOW_HEIGHT+CELL_HEIGHT,CELL_HEIGHT):
        pygame.draw.line(SCREEN, BLACK, (0,y), (WINDOW_WIDTH,y))

def drawCells(cell_positions):
    """Draws cells on the display"""
    for (cell_x, cell_y) in cell_positions:
        cellRect = pygame.Rect(cell_x, cell_y, CELL_WIDTH, CELL_HEIGHT)
        pygame.draw.rect(SCREEN, BLACK, cellRect)

def inWindow((square_x, square_y)):
    """Returns True if the square is in the window. False otherwise"""
    # Take care in the conditions. Since cells are tracked by theur upper-left corner,
    # there is a cell-wide gap on the right and bottom of the window
    if 0<=square_x<=WINDOW_WIDTH-CELL_WIDTH and 0<=square_y<=WINDOW_HEIGHT-CELL_HEIGHT:
        return True
    else:
        return False

def terminate():
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()