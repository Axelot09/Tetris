import pygame
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Define shapes of Tetrominoes (in 4x4 grids)
SHAPES = [
    [['.....', '.....', '..00.', '..00.', '.....']],  # O shape
    [['.....', '...0.', '..000', '.....', '.....'],  # T shape
     ['.....', '..0..', '..00.', '..0..', '.....'],
     ['.....', '.....', '..000', '...0.', '.....'],
     ['.....', '..0..', '.00..', '..0..', '.....']],
    [['.....', '...0.', '...0.', '...00', '.....'],  # L shape
     ['.....', '.....', '..000', '..0..', '.....'],
     ['.....', '.00..', '..0..', '..0..', '.....'],
     ['.....', '..0..', '..000', '.....', '.....']],
    [['.....', '...0.', '...0.', '..00.', '.....'],  # J shape
     ['.....', '..0..', '..000', '.....', '.....'],
     ['.....', '.00..', '.0...', '.0...', '.....'],
     ['.....', '..000', '..0..', '.....', '.....']],
    [['.....', '..00.', '.00..', '.....', '.....'],  # Z shape
     ['.....', '..0..', '..00.', '...0.', '.....']],
    [['.....', '.00..', '..00.', '.....', '.....'],  # S shape
     ['.....', '...0.', '..00.', '..0..', '.....']],
    [['.....', '...0.', '...0.', '...0.', '...0.']]  # I shape
]

# Tetromino class
class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.rotation = 0
        self.x = SCREEN_WIDTH // 2 // BLOCK_SIZE - 2
        self.y = 0

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)

    def get_shape(self):
        return self.shape[self.rotation]

# Define grid
def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]

    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]

    return grid

# Draw a rounded rectangle block
def draw_rounded_block(surface, color, pos):
    rect = pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surface, color, rect, border_radius=6)

# Draw grid lines
def draw_grid(surface):
    for y in range(SCREEN_HEIGHT // BLOCK_SIZE):
        for x in range(SCREEN_WIDTH // BLOCK_SIZE):
            pygame.draw.rect(surface, GRAY, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

# Draw tetrominoes on the grid
def draw_window(surface, grid, score, level):
    surface.fill(BLACK)

    # Draw background gradient
    for i in range(SCREEN_HEIGHT):
        color = tuple(min(c + i // 3, 255) for c in (30, 30, 30))
        pygame.draw.line(surface, color, (0, i), (SCREEN_WIDTH, i))

    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if grid[y][x] != BLACK:
                draw_rounded_block(surface, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE))

    draw_grid(surface)
    
    # Draw score and level with shadows
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', 1, WHITE)
    surface.blit(label, (10, 10))
    
    label = font.render(f'Level: {level}', 1, WHITE)
    surface.blit(label, (10, 40))
    
    pygame.display.update()

# Check if position is valid
def valid_position(tetromino, grid):
    accepted_positions = [[(x, y) for x in range(SCREEN_WIDTH // BLOCK_SIZE) if grid[y][x] == BLACK] for y in range(SCREEN_HEIGHT // BLOCK_SIZE)]
    accepted_positions = [x for sub in accepted_positions for x in sub]

    formatted_shape = convert_shape_format(tetromino)

    for pos in formatted_shape:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

# Convert the tetromino shape from its 4x4 grid to positions on the main grid
def convert_shape_format(tetromino):
    positions = []
    shape = tetromino.get_shape()

    for i, line in enumerate(shape):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((tetromino.x + j, tetromino.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0], pos[1] - 4)

    return positions

# Check for full rows and remove them
def clear_rows(grid, locked):
    full_rows = 0
    for y in range(len(grid) - 1, -1, -1):
        row = grid[y]
        if BLACK not in row:
            full_rows += 1
            del_row = y
            for x in range(SCREEN_WIDTH // BLOCK_SIZE):
                del locked[(x, y)]
            
            for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
                x, y = key
                if y < del_row:
                    new_key = (x, y + 1)
                    locked[new_key] = locked.pop(key)

    return full_rows

# Game over condition
def check_game_over(locked_positions):
    for pos in locked_positions:
        if pos[1] < 1:
            return True
    return False

# Main game function
def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = Tetromino(random.choice(SHAPES), random.choice([RED, GREEN, BLUE, CYAN, YELLOW, PURPLE, ORANGE]))
    next_piece = Tetromino(random.choice(SHAPES), random.choice([RED, GREEN, BLUE, CYAN, YELLOW, PURPLE, ORANGE]))
    clock = pygame.time.Clock()

    score = 0
    level = 1
    fall_time = 0
    fall_speed = 0.5
    full_rows_cleared = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Level up system: increase speed every 10 rows cleared
        if full_rows_cleared >= 10:
            full_rows_cleared -= 10
            level += 1
            fall_speed = max(0.05, fall_speed - 0.05)

        # Piece falls down automatically
        if fall_time / 1000 >= fall_speed:
            current_piece.y += 1
            if not valid_position(current_piece, grid):
                current_piece.y -= 1
                change_piece = True
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_position(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_position(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_position(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_position(current_piece, grid):
                        current_piece.rotate()

        shape_pos = convert_shape_format(current_piece)

        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = Tetromino(random.choice(SHAPES), random.choice([RED, GREEN, BLUE, CYAN, YELLOW, PURPLE, ORANGE]))
            change_piece = False
            full_rows_cleared += clear_rows(grid, locked_positions)
            score += full_rows_cleared * 10

        # Check for game over
        if check_game_over(locked_positions):
            run = False

        draw_window(screen, grid, score, level)

    pygame.quit()

# Set up the game screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

# Start the game
main()