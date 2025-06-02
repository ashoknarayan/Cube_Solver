import pygame
import kociemba
from pygame import Vector2

pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
CELL_SIZE = 40
COLOR_SIZE = 30
SPACING = 10
FPS = 60
TEXT_LINE_HEIGHT = 24
MAX_VISIBLE_LINES = 30
SOLUTION_X_START = 800

# Colors (RGB) — neon style colors
COLORS = {
    'W': (255, 255, 255),    # White (bright)
    'Y': (255, 255, 0),      # Yellow
    'R': (255, 50, 50),      # Neon Red
    'O': (255, 140, 0),      # Neon Orange
    'G': (0, 255, 128),      # Neon Green
    'B': (0, 128, 255),      # Neon Blue
    'X': (80, 80, 80)        # Dark gray for uncolored cells
}

BG_COLOR = (15, 15, 30)

# Face positions — shifted left face more right by 7 px
FACE_POSITIONS = {
    'U': Vector2(4 * CELL_SIZE + 2 * SPACING, 2 * SPACING + COLOR_SIZE + 40),
    'L': Vector2(SPACING + 40, 4 * CELL_SIZE + 2 * SPACING + 40), 
    'F': Vector2(4 * CELL_SIZE + 2 * SPACING, 4 * CELL_SIZE + 2 * SPACING + 40),
    'R': Vector2(7 * CELL_SIZE + 3 * SPACING, 4 * CELL_SIZE + 2 * SPACING + 40),
    'B': Vector2(10 * CELL_SIZE + 4 * SPACING, 4 * CELL_SIZE + 2 * SPACING + 40),
    'D': Vector2(4 * CELL_SIZE + 2 * SPACING, 7 * CELL_SIZE + 3 * SPACING + 40)
}

CUBE_STATE = {
    'U': [['X' if (row, col) != (1, 1) else 'W' for col in range(3)] for row in range(3)],
    'L': [['X' if (row, col) != (1, 1) else 'O' for col in range(3)] for row in range(3)],
    'F': [['X' if (row, col) != (1, 1) else 'G' for col in range(3)] for row in range(3)],
    'R': [['X' if (row, col) != (1, 1) else 'R' for col in range(3)] for row in range(3)],
    'B': [['X' if (row, col) != (1, 1) else 'B' for col in range(3)] for row in range(3)],
    'D': [['X' if (row, col) != (1, 1) else 'Y' for col in range(3)] for row in range(3)]
}

CENTER_CELLS = {(1, 1)}

PALETTE_POS = [(480 + i * (COLOR_SIZE + SPACING), SPACING + 40, c)
               for i, c in enumerate(['W', 'Y', 'R', 'O', 'G', 'B'])]

BUTTON_RECT = pygame.Rect(150, 500 + 40, 100, 40)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (120, 120, 120)
BUTTON_TEXT = "Solve"

SOLUTION_TEXT = []
FONT = pygame.font.SysFont('arial', 20)
TITLE_FONT = pygame.font.SysFont('arial', 30, bold=True)
scroll_offset = 0

selected_color = 'W'
running = True

def solve_cube(cube_string):
    try:
        if len(cube_string) != 54:
            return False, "Invalid cube string: must be 54 characters."
        valid_chars = {'U', 'R', 'F', 'D', 'L', 'B'}
        if not all(c in valid_chars for c in cube_string):
            return False, "Invalid cube string: contains invalid characters."
        solution = kociemba.solve(cube_string)
        return True, solution
    except Exception as e:
        return False, f"Solver error: {str(e)}"

def translate_moves(move_string):
    FACE_NAMES = {
        'U': 'top layer',
        'R': 'right layer',
        'F': 'front layer',
        'D': "bottom layer",
        'L': 'left layer',
        'B': 'back layer'
    }
    MODIFIER_NAMES = {
        '': 'clockwise once',
        '2': 'clockwise twice',
        "'": 'counterclockwise once'
    }
    moves = move_string.strip().split()
    instructions = []
    for move in moves:
        if not move:
            continue
        face = move[0]
        modifier = move[1:] if len(move) > 1 else ''
        if face not in FACE_NAMES or modifier not in MODIFIER_NAMES:
            instructions.append(f"Invalid move: {move}")
            continue
        instructions.append(f"• Turn {FACE_NAMES[face]} {MODIFIER_NAMES[modifier]}")
    return instructions

def setup():
    global screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Rubik's Cube Solver")

def draw_face(face, pos):
    center_colors = {'U': 'W', 'L': 'O', 'F': 'G', 'R': 'R', 'B': 'B', 'D': 'Y'}
    for row in range(3):
        for col in range(3):
            color_key = CUBE_STATE[face][row][col]
            color = COLORS[center_colors[face]] if (row, col) in CENTER_CELLS else COLORS[color_key]
            rect = pygame.Rect(pos.x + col * CELL_SIZE, pos.y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (50, 50, 50), rect, 2)

def draw_palette():
    for x, y, color_key in PALETTE_POS:
        rect = pygame.Rect(x, y, COLOR_SIZE, COLOR_SIZE)
        pygame.draw.rect(screen, COLORS[color_key], rect)
        if color_key == selected_color:
            pygame.draw.rect(screen, (0, 0, 0), rect, 3)
        else:
            pygame.draw.rect(screen, (100, 100, 100), rect, 1)

def draw_button():
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER_COLOR if BUTTON_RECT.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, BUTTON_RECT)
    text_surf = FONT.render(BUTTON_TEXT, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=BUTTON_RECT.center)
    screen.blit(text_surf, text_rect)

def draw_solution():
    # Draw "Solution" title
    solution_title = "Solution"
    title_surf = TITLE_FONT.render(solution_title, True, (0, 255, 255))  # neon cyan
    screen.blit(title_surf, (SOLUTION_X_START, SPACING + 40))

    # Draw the bullet point instructions below title with some padding
    start_idx = scroll_offset
    end_idx = min(start_idx + MAX_VISIBLE_LINES, len(SOLUTION_TEXT))
    for i, line in enumerate(SOLUTION_TEXT[start_idx:end_idx]):
        y = SPACING + 40 + 40 + i * TEXT_LINE_HEIGHT  # 40 px padding after title
        text_surf = FONT.render(line, True, (0, 255, 255))
        screen.blit(text_surf, (SOLUTION_X_START, y))

def draw_title():
    title_text = "Configure your cube colours here"
    text_surf = TITLE_FONT.render(title_text, True, (0, 255, 255))
    shadow_surf = TITLE_FONT.render(title_text, True, (0, 128, 128))
    screen.blit(shadow_surf, (SPACING + 2, SPACING + 2))
    screen.blit(text_surf, (SPACING, SPACING))

def get_cube_string():
    COLOR_TO_FACE = {
        'W': 'U',
        'Y': 'D',
        'R': 'R',
        'O': 'L',
        'G': 'F',
        'B': 'B',
        'X': 'U'
    }
    order = ['U', 'R', 'F', 'D', 'L', 'B']
    result = ''
    for face in order:
        for row in range(3):
            for col in range(3):
                color = CUBE_STATE[face][row][col]
                result += COLOR_TO_FACE[color]
    return result

def handle_click(pos):
    global selected_color, SOLUTION_TEXT, scroll_offset
    for x, y, color_key in PALETTE_POS:
        rect = pygame.Rect(x, y, COLOR_SIZE, COLOR_SIZE)
        if rect.collidepoint(pos):
            selected_color = color_key
            return
    for face, face_pos in FACE_POSITIONS.items():
        for row in range(3):
            for col in range(3):
                rect = pygame.Rect(face_pos.x + col * CELL_SIZE, face_pos.y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if rect.collidepoint(pos) and (row, col) not in CENTER_CELLS:
                    CUBE_STATE[face][row][col] = selected_color
                    return
    if BUTTON_RECT.collidepoint(pos):
        try:
            cube_string = get_cube_string()
            success, result = solve_cube(cube_string)
            if success:
                translated = translate_moves(result)
                SOLUTION_TEXT = translated if isinstance(translated, list) else [translated]
            else:
                SOLUTION_TEXT = [result]
            scroll_offset = 0
        except Exception as e:
            SOLUTION_TEXT = [f"Error: {str(e)}"]
            scroll_offset = 0

def main():
    setup()
    clock = pygame.time.Clock()
    global running, scroll_offset
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(event.pos)
            elif event.type == pygame.MOUSEWHEEL:
                if SOLUTION_TEXT:
                    scroll_offset -= event.y
                    scroll_offset = max(0, min(scroll_offset, len(SOLUTION_TEXT) - MAX_VISIBLE_LINES))

        screen.fill(BG_COLOR)
        draw_title()
        for face, pos in FACE_POSITIONS.items():
            draw_face(face, pos)
        draw_palette()
        draw_button()
        draw_solution()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
