import pygame
import random
import heapq
import sys
from collections import deque

# ===== CUSTOMIZABLE SETTINGS =====
# Colors
BG_TOP_COLOR = (13, 27, 42)      # Dark blue
BG_BOTTOM_COLOR = (27, 38, 59)   # Navy blue
TILE_COLOR = (168, 218, 220)     # Mint green
TILE_BORDER_COLOR = (65, 90, 119) # Light blue
EMPTY_TILE_COLOR = (27, 38, 59)  # Navy blue
TILE_TEXT_COLOR = (13, 27, 42)   # Dark blue
BTN_COLORS = {
    'manual': (233, 106, 91),    # Salmon
    'astar': (168, 218, 220),    # Mint
    'bfs': (198, 160, 246)       # Light purple
}
BTN_TEXT_COLOR = (13, 27, 42)    # Dark blue
BTN_SHADOW_COLOR = (50, 50, 50)  # Dark gray
TEXT_COLORS = {
    'title': (224, 225, 221),    # Cream
    'shadow': (50, 50, 50),      # Dark gray
    'mode': (224, 225, 221)      # Cream
}

# Game settings
WIDTH, HEIGHT = 650, 800
ROWS, COLS = 3, 3
TILE_SIZE = WIDTH // COLS
BUTTON_WIDTH, BUTTON_HEIGHT = 220, 60
ANIMATION_DELAY = 300  # ms between moves in auto mode

# ===== INITIALIZATION =====
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("N-Puzzle Game")

# Fonts
font_large = pygame.font.Font(None, 60)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 40)

# Goal state
goal_state = list(range(1, ROWS * COLS)) + [0]

# ===== GAME FUNCTIONS =====
def is_solvable(puzzle):
    """Check if puzzle is solvable by counting inversions"""
    inversions = 0
    for i in range(len(puzzle)):
        for j in range(i + 1, len(puzzle)):
            if puzzle[i] and puzzle[j] and puzzle[i] > puzzle[j]:
                inversions += 1
    return inversions % 2 == 0

def valid_moves(empty_pos):
    """Get valid moves from current empty position"""
    row, col = divmod(empty_pos, COLS)
    moves = []
    if row > 0: moves.append(empty_pos - COLS)  # Up
    if row < ROWS - 1: moves.append(empty_pos + COLS)  # Down
    if col > 0: moves.append(empty_pos - 1)  # Left
    if col < COLS - 1: moves.append(empty_pos + 1)  # Right
    return moves

def manhattan_distance(state):
    """Calculate Manhattan distance heuristic"""
    distance = 0
    for i, tile in enumerate(state):
        if tile == 0: continue
        goal_pos = goal_state.index(tile)
        goal_row, goal_col = divmod(goal_pos, COLS)
        current_row, current_col = divmod(i, COLS)
        distance += abs(goal_row - current_row) + abs(goal_col - current_col)
    return distance

def solve_puzzle_astar(start_state):
    """Solve using A* algorithm with Manhattan distance"""
    open_set = []
    heapq.heappush(open_set, (manhattan_distance(start_state), tuple(start_state)))
    came_from = {}
    g_score = {tuple(start_state): 0}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if list(current) == goal_state:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(tuple(start_state))
            return path[::-1]
        
        empty_pos = current.index(0)
        for move in valid_moves(empty_pos):
            new_state = list(current)
            new_state[empty_pos], new_state[move] = new_state[move], new_state[empty_pos]
            new_state_tuple = tuple(new_state)
            
            tentative_g = g_score[current] + 1
            if new_state_tuple not in g_score or tentative_g < g_score[new_state_tuple]:
                came_from[new_state_tuple] = current
                g_score[new_state_tuple] = tentative_g
                f_score = tentative_g + manhattan_distance(new_state)
                heapq.heappush(open_set, (f_score, new_state_tuple))
    
    return None

def solve_puzzle_bfs(start_state):
    """Solve using BFS algorithm"""
    queue = deque([tuple(start_state)])
    visited = {tuple(start_state): None}
    
    while queue:
        current = queue.popleft()
        
        if list(current) == goal_state:
            path = []
            while current in visited:
                path.append(current)
                current = visited[current]
            return path[::-1]
        
        empty_pos = current.index(0)
        for move in valid_moves(empty_pos):
            new_state = list(current)
            new_state[empty_pos], new_state[move] = new_state[move], new_state[empty_pos]
            new_state_tuple = tuple(new_state)
            
            if new_state_tuple not in visited:
                visited[new_state_tuple] = current
                queue.append(new_state_tuple)
    
    return None

def generate_solvable_puzzle():
    """Generate a solvable puzzle configuration"""
    while True:
        puzzle = goal_state.copy()
        random.shuffle(puzzle)
        if is_solvable(puzzle):
            return puzzle

# ===== UI FUNCTIONS =====
def draw_gradient_background():
    """Draw gradient background from top to bottom"""
    for y in range(HEIGHT):
        r = int(BG_TOP_COLOR[0] + (BG_BOTTOM_COLOR[0] - BG_TOP_COLOR[0]) * y / HEIGHT)
        g = int(BG_TOP_COLOR[1] + (BG_BOTTOM_COLOR[1] - BG_TOP_COLOR[1]) * y / HEIGHT)
        b = int(BG_TOP_COLOR[2] + (BG_BOTTOM_COLOR[2] - BG_TOP_COLOR[2]) * y / HEIGHT)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def draw_board(state):
    """Draw the current puzzle board"""
    draw_gradient_background()
    
    # Title with shadow
    title = font_large.render("N-Puzzle Genius", True, TEXT_COLORS['title'])
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
    
    # Mode indicator
    mode_text = font_small.render(
        f"Mode: {'Manual' if interactive_mode else 'Auto'} ({current_algorithm if current_algorithm else '--'})", 
        True, TEXT_COLORS['mode'])
    screen.blit(mode_text, (20, 110))
    
    # Puzzle board
    board_x = (WIDTH - COLS * TILE_SIZE) // 2
    board_y = 180
    
    for i in range(ROWS * COLS):
        value = state[i]
        row, col = divmod(i, COLS)
        x = board_x + col * TILE_SIZE
        y = board_y + row * TILE_SIZE
        
        tile_rect = pygame.Rect(x, y, TILE_SIZE - 10, TILE_SIZE - 10)
        
        if value == 0:
            pygame.draw.rect(screen, EMPTY_TILE_COLOR, tile_rect, border_radius=10)
        else:
            pygame.draw.rect(screen, TILE_COLOR, tile_rect, border_radius=10)
            text = font_medium.render(str(value), True, TILE_TEXT_COLOR)
            text_rect = text.get_rect(center=tile_rect.center)
            screen.blit(text, text_rect)
        
        pygame.draw.rect(screen, TILE_BORDER_COLOR, tile_rect, 2, border_radius=10)
    
    pygame.display.flip()

def draw_button(x, y, width, height, color, text):
    """Draw a button with hover effect"""
    mouse_pos = pygame.mouse.get_pos()
    hovered = (x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height)
    
    # Button shadow
    pygame.draw.rect(screen, BTN_SHADOW_COLOR, (x + 3, y + 3, width, height), border_radius=10)
    
    # Button with hover effect
    btn_color = (min(color[0] + 20, 255), min(color[1] + 20, 255), min(color[2] + 20, 255)) if hovered else color
    pygame.draw.rect(screen, btn_color, (x, y, width, height), border_radius=10)
    pygame.draw.rect(screen, (80, 80, 80), (x, y, width, height), 2, border_radius=10)
    
    # Button text
    text_surf = font_medium.render(text, True, BTN_TEXT_COLOR)
    text_rect = text_surf.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text_surf, text_rect)
    
    return pygame.Rect(x, y, width, height), hovered and pygame.mouse.get_pressed()[0]

def show_main_menu():
    """Display the main menu and return selected mode"""
    while True:
        draw_gradient_background()
        
        # Title
        title = font_large.render("N-Puzzle Genius", True, TEXT_COLORS['title'])
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Buttons
        btn_y = 250
        btn_spacing = 80
        
        manual_btn, manual_click = draw_button(
            WIDTH//2 - BUTTON_WIDTH//2, btn_y, 
            BUTTON_WIDTH, BUTTON_HEIGHT,
            BTN_COLORS['manual'], "Manual Play")
        
        astar_btn, astar_click = draw_button(
            WIDTH//2 - BUTTON_WIDTH//2, btn_y + btn_spacing, 
            BUTTON_WIDTH, BUTTON_HEIGHT,
            BTN_COLORS['astar'], "Auto (A*)")
        
        bfs_btn, bfs_click = draw_button(
            WIDTH//2 - BUTTON_WIDTH//2, btn_y + 2 * btn_spacing, 
            BUTTON_WIDTH, BUTTON_HEIGHT,
            BTN_COLORS['bfs'], "Auto (BFS)")
        
        # Footer
        footer = font_small.render("Press SPACE to toggle modes", True, TEXT_COLORS['mode'])
        screen.blit(footer, (WIDTH//2 - footer.get_width()//2, HEIGHT - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        if manual_click:
            return 'manual'
        if astar_click:
            return 'astar'
        if bfs_click:
            return 'bfs'

# ===== MAIN GAME LOOP =====
def main():
    global interactive_mode, current_algorithm
    
    # Initial game state
    board = generate_solvable_puzzle()
    path_to_solution = []
    step = 0
    solved = False
    
    # Game clock
    clock = pygame.time.Clock()
    last_move_time = 0
    
    # Start with menu
    selected_mode = show_main_menu()
    interactive_mode = selected_mode == 'manual'
    current_algorithm = 'A*' if selected_mode == 'astar' else 'BFS' if selected_mode == 'bfs' else None
    
    # If auto mode selected, calculate solution
    if not interactive_mode:
        solver = solve_puzzle_astar if selected_mode == 'astar' else solve_puzzle_bfs
        path_to_solution = solver(board)
        if not path_to_solution:
            print("No solution found - generating new puzzle")
            board = generate_solvable_puzzle()
            path_to_solution = solver(board)
    
    # Main game loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and interactive_mode and not solved:
                # Handle tile clicks in manual mode
                mouse_x, mouse_y = event.pos
                board_x = (WIDTH - COLS * TILE_SIZE) // 2
                board_y = 180
                
                if board_y <= mouse_y < board_y + ROWS * TILE_SIZE:
                    col = (mouse_x - board_x) // TILE_SIZE
                    row = (mouse_y - board_y) // TILE_SIZE
                    
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        clicked_pos = row * COLS + col
                        empty_pos = board.index(0)
                        
                        if clicked_pos in valid_moves(empty_pos):
                            board[empty_pos], board[clicked_pos] = board[clicked_pos], board[empty_pos]
                            
                            # Check if solved
                            if board == goal_state:
                                solved = True
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not solved:
                    # Toggle between manual and auto mode
                    interactive_mode = not interactive_mode
                    
                    if not interactive_mode:
                        # When switching to auto mode, use last selected algorithm
                        solver = solve_puzzle_astar if current_algorithm == 'A*' else solve_puzzle_bfs
                        path_to_solution = solver(board)
                        step = 0
                        
                        if not path_to_solution:
                            print("No solution found - switching back to manual")
                            interactive_mode = True
        
        # Auto mode movement
        if not interactive_mode and path_to_solution and not solved and current_time - last_move_time > ANIMATION_DELAY:
            if step < len(path_to_solution):
                board = list(path_to_solution[step])
                step += 1
                last_move_time = current_time
                
                # Check if solved
                if board == goal_state:
                    solved = True
            else:
                # Reached end of solution path but not solved (shouldn't happen)
                interactive_mode = True
        
        # Drawing
        draw_board(board)
        
        # Show victory message
        if solved:
            victory_text = font_medium.render("Puzzle Solved!", True, (218, 165, 32))  # Gold
            screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, 500))
            
            # Offer to play again
            again_text = font_small.render("Click to play again", True, TEXT_COLORS['mode'])
            screen.blit(again_text, (WIDTH//2 - again_text.get_width()//2, 570))
            
            pygame.display.flip()
            
            # Wait for click to restart
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        waiting = False
                        # Reset game
                        board = generate_solvable_puzzle()
                        path_to_solution = []
                        step = 0
                        solved = False
                        # Show menu again
                        selected_mode = show_main_menu()
                        interactive_mode = selected_mode == 'manual'
                        current_algorithm = 'A*' if selected_mode == 'astar' else 'BFS' if selected_mode == 'bfs' else None
                        if not interactive_mode:
                            solver = solve_puzzle_astar if selected_mode == 'astar' else solve_puzzle_bfs
                            path_to_solution = solver(board)
                            if not path_to_solution:
                                print("No solution found - generating new puzzle")
                                board = generate_solvable_puzzle()
                                path_to_solution = solver(board)
                
                clock.tick(30)
        
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()