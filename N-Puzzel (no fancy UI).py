import pygame
import random
import heapq
import sys
from collections import deque

# Constants: Board settings 
WIDTH, HEIGHT = 600, 700  # Increased height to accommodate new button
ROWS, COLS = 3, 3
TILE_SIZE = WIDTH // COLS
FONT_SIZE = 50

# Colors
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("N-Puzzle Game")
font = pygame.font.Font(None, FONT_SIZE)

# Goal state for comparison [1, 2, 3, 4, 5, 6, 7, 8, 0]
goal_state = list(range(1, ROWS * COLS)) + [0] 

# Helper Functions
def manhattan_distance(state):
    distance = 0
    for i, tile in enumerate(state):
        if tile == 0: continue
        target_pos = goal_state.index(tile)
        target_row, target_col = divmod(target_pos, COLS)
        current_row, current_col = divmod(i, COLS)
        distance += abs(target_row - current_row) + abs(target_col - current_col)
    return distance

def is_solvable(puzzle):
    inv_count = 0
    for i in range(len(puzzle)):
        for j in range(i + 1, len(puzzle)):
            if puzzle[i] and puzzle[j] and puzzle[i] > puzzle[j]:
                inv_count += 1
    return inv_count % 2 == 0

def valid_moves(empty_pos):
    row, col = divmod(empty_pos, COLS)
    moves = []
    if row > 0: moves.append(empty_pos - COLS)   # move up
    if row < ROWS - 1: moves.append(empty_pos + COLS)  # move down
    if col > 0: moves.append(empty_pos - 1)     # move left
    if col < COLS - 1: moves.append(empty_pos + 1)  # move right
    return moves

def solve_puzzle_astar(start_state):
    open_list = []
    closed_list = set()
    parent_map = {}
    g_cost = {tuple(start_state): 0}
    f_cost = {tuple(start_state): manhattan_distance(start_state)}

    heapq.heappush(open_list, (f_cost[tuple(start_state)], tuple(start_state)))

    while open_list:
        _, current_state = heapq.heappop(open_list)
        
        if current_state == tuple(goal_state):
            path = []
            while current_state in parent_map:
                path.append(current_state)
                current_state = parent_map[current_state]
            path.append(tuple(start_state))
            return path[::-1]

        closed_list.add(current_state)

        empty_pos = current_state.index(0)
        for move in valid_moves(empty_pos):
            new_state = list(current_state)
            new_state[empty_pos], new_state[move] = new_state[move], new_state[empty_pos]
            new_state_tuple = tuple(new_state)
            if new_state_tuple in closed_list:
                continue

            tentative_g = g_cost[tuple(current_state)] + 1
            if new_state_tuple not in g_cost or tentative_g < g_cost[new_state_tuple]:
                g_cost[new_state_tuple] = tentative_g
                f = tentative_g + manhattan_distance(new_state)
                f_cost[new_state_tuple] = f
                heapq.heappush(open_list, (f, new_state_tuple))
                parent_map[new_state_tuple] = current_state

    return None  # No solution found

def solve_puzzle_bfs(start_state):
    queue = deque()
    visited = set()
    parent_map = {}
    
    queue.append(tuple(start_state))
    visited.add(tuple(start_state))
    parent_map[tuple(start_state)] = None
    
    while queue:
        current_state = queue.popleft()
        
        if current_state == tuple(goal_state):
            path = []
            while current_state in parent_map and parent_map[current_state] is not None:
                path.append(current_state)
                current_state = parent_map[current_state]
            path.append(tuple(start_state))
            return path[::-1]
        
        empty_pos = current_state.index(0)
        for move in valid_moves(empty_pos):
            new_state = list(current_state)
            new_state[empty_pos], new_state[move] = new_state[move], new_state[empty_pos]
            new_state_tuple = tuple(new_state)
            
            if new_state_tuple not in visited:
                visited.add(new_state_tuple)
                parent_map[new_state_tuple] = current_state
                queue.append(new_state_tuple)
    
    return None  # No solution found

# Initialize the game state
board = list(range(1, ROWS * COLS)) + [0]
random.shuffle(board)
while not is_solvable(board):
    random.shuffle(board)

# Game variables
running = True
step = 0
interactive_mode = True
path_to_solution = []
current_algorithm = None

def draw_board(state):
    screen.fill(GRAY)

    # Draw game title at the top
    title = font.render("N-Puzzle Game", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # Leave some space below title
    offset_y = 60

    for i in range(ROWS * COLS):
        value = state[i]
        x = (i % COLS) * TILE_SIZE
        y = (i // COLS) * TILE_SIZE + offset_y

        tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

        if value == 0:
            pygame.draw.rect(screen, GRAY, tile_rect)
        else:
            pygame.draw.rect(screen, WHITE, tile_rect, border_radius=12)
            pygame.draw.rect(screen, BLACK, tile_rect, 2, border_radius=12)
            text = font.render(str(value), True, BLACK)
            rect = text.get_rect(center=tile_rect.center)
            screen.blit(text, rect)

    pygame.display.flip()

def display_main_menu():
    screen.fill(GRAY)

    title = font.render("8-Puzzle Game", True, BLACK)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 5))
    screen.blit(title, title_rect)

    # Manual button
    manual_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 3, 200, 50)
    pygame.draw.rect(screen, WHITE, manual_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, manual_rect, 2, border_radius=10)
    manual_text = font.render("Manual", True, BLACK)
    screen.blit(manual_text, manual_text.get_rect(center=manual_rect.center))

    # A* button
    astar_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 3 + 70, 200, 50)
    pygame.draw.rect(screen, BLUE, astar_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, astar_rect, 2, border_radius=10)
    astar_text = font.render("A*", True, WHITE)
    screen.blit(astar_text, astar_text.get_rect(center=astar_rect.center))

    # BFS button
    bfs_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 3 + 140, 200, 50)
    pygame.draw.rect(screen, RED, bfs_rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, bfs_rect, 2, border_radius=10)
    bfs_text = font.render("BFS", True, WHITE)
    screen.blit(bfs_text, bfs_text.get_rect(center=bfs_rect.center))

    pygame.display.update()

# Main menu loop
mode_selected = False
while not mode_selected:
    display_main_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            if HEIGHT // 3 <= mouse_y <= HEIGHT // 3 + 50:
                # Manual mode
                mode_selected = True
                interactive_mode = True
            elif HEIGHT // 3 + 70 <= mouse_y <= HEIGHT // 3 + 120:
                # A* mode
                mode_selected = True
                interactive_mode = False
                current_algorithm = "A*"
                path_to_solution = solve_puzzle_astar(board)
            elif HEIGHT // 3 + 140 <= mouse_y <= HEIGHT // 3 + 190:
                # BFS mode
                mode_selected = True
                interactive_mode = False
                current_algorithm = "BFS"
                path_to_solution = solve_puzzle_bfs(board)

    if path_to_solution is None:
        print("No solution found")
        pygame.quit()
        sys.exit()

# Game loop after mode selection
while running:
    draw_board(board)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if interactive_mode:
                # Get the mouse position to find which tile was clicked
                mouse_x, mouse_y = event.pos
                clicked_row = (mouse_y - 60) // TILE_SIZE  # Adjusted for title space
                clicked_col = mouse_x // TILE_SIZE
                clicked_pos = clicked_row * COLS + clicked_col

                # Find the empty space (0) and check if the clicked tile is a valid move
                empty_pos = board.index(0)
                if clicked_pos in valid_moves(empty_pos):
                    board[empty_pos], board[clicked_pos] = board[clicked_pos], board[empty_pos]
                    if board == goal_state:
                        interactive_mode = False  # Puzzle solved

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Space key to switch to auto mode
                interactive_mode = not interactive_mode
                if not interactive_mode and not path_to_solution:
                    current_algorithm = "A*"  # Default to A* if no algorithm selected
                    path_to_solution = solve_puzzle_astar(board)

    if not interactive_mode and path_to_solution:
        # Show the solution path step by step
        if step < len(path_to_solution) - 1:
            step += 1
            board = list(path_to_solution[step])  # Update the board to the next step in the solution path
            pygame.time.wait(500)  # Delay to show the next step
        else:
            running = False  # Stop the game after the solution is fully displayed

    pygame.display.update()

pygame.quit()
sys.exit()