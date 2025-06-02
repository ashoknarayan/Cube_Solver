import pygame
import kociemba
from pygame import Vector2

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
CELL_SIZE = 40
COLOR_SIZE = 30
SPACING = 10
FPS = 60
TEXT_LINE_HEIGHT = 25
MAX_VISIBLE_LINES = 30  # Increased to show more lines on the right side
SOLUTION_X_START = 800  # Position for solution text on the right

# Colors (RGB)
COLORS = {
    'W': (255, 255, 255),  # White
    'Y': (255, 255, 0),    # Yellow
    'R': (255, 0, 0),      # Red
    'O': (255, 165, 0),    # Orange
    'G': (0, 255, 0),      # Green
    'B': (0, 0, 255),      # Blue
    'X': (200, 200, 200)   # Uncolored (gray for non-center cells initially)
}

# T-shaped layout: positions for each face (center of each 3x3 grid)
FACE_POSITIONS = {
    'U': Vector2(4 * CELL_SIZE + 2 * SPACING, 2 * SPACING + COLOR_SIZE),
    'L': Vector2(SPACING, 4 * CELL_SIZE + 2 * SPACING),
    'F': Vector2(4 * CELL_SIZE + 2 * SPACING, 4 * CELL_SIZE + 2 * SPACING),
    'R': Vector2(7 * CELL_SIZE + 3 * SPACING, 4 * CELL_SIZE + 2 * SPACING),
    'B': Vector2(10 * CELL_SIZE + 4 * SPACING, 4 * CELL_SIZE + 2 * SPACING),
    'D': Vector2(4 * CELL_SIZE + 2 * SPACING, 7 * CELL_SIZE + 3 * SPACING)
}

# Initialize cube state: 6 faces, each 3x3. Only centers are colored initially.
CUBE_STATE = {
    'U': [['X' if (row, col) != (1, 1) else 'W' for col in range(3)] for row in range(3)],
    'L': [['X' if (row, col) != (1, 1) else 'O' for col in range(3)] for row in range(3)],
    'F': [['X' if (row, col) != (1, 1) else 'G' for col in range(3)] for row in range(3)],
    'R': [['X' if (row, col) != (1, 1) else 'R' for col in range(3)] for row in range(3)],
    'B': [['X' if (row, col) != (1, 1) else 'B' for col in range(3)] for row in range(3)],
    'D': [['X' if (row, col) != (1, 1) else 'Y' for col in range(3)] for row in range(3)]
}

# Fixed center cells (row, col) for each face
CENTER_CELLS = {(1, 1)}

# Color palette positions (just to the right of the cube map)
PALETTE_POS = [(480 + i * (COLOR_SIZE + SPACING), SPACING, c) 
               for i, c in enumerate(['W', 'Y', 'R', 'O', 'G', 'B'])]

# Button properties
BUTTON_RECT = pygame.Rect(150, 500, 100, 40)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
BUTTON_TEXT = "Solve"

# Solution display
SOLUTION_TEXT = []
FONT = pygame.font.SysFont('arial', 20)
scroll_offset = 0  # Tracks the scroll position (in lines)

# State variables
selected_color = 'W'
running = True

# Solver function
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

# Translator function
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
        instructions.append(f"Turn {FACE_NAMES[face]} {MODIFIER_NAMES[modifier]}")
    return instructions

# GUI functions
def setup():
    global screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Rubik's Cube Solver")

def draw_face(face, pos):
    """Draw a 3x3 face at the given position."""
    center_colors = {'U': 'W', 'L': 'O', 'F': 'G', 'R': 'R', 'B': 'B', 'D': 'Y'}
    for row in range(3):
        for col in range(3):
            color_key = CUBE_STATE[face][row][col]
            if (row, col) in CENTER_CELLS:
                color = COLORS[center_colors[face]]  # Use the face's center color
            else:
                color = COLORS[color_key]
            rect = pygame.Rect(pos.x + col * CELL_SIZE, pos.y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

def draw_palette():
    """Draw the color palette just to the right of the cube map."""
    for x, y, color_key in PALETTE_POS:
        rect = pygame.Rect(x, y, COLOR_SIZE, COLOR_SIZE)
        pygame.draw.rect(screen, COLORS[color_key], rect)
        if color_key == selected_color:
            pygame.draw.rect(screen, (255, 255, 0), rect, 3)
        else:
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

def draw_button():
    """Draw the Solve button."""
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER_COLOR if BUTTON_RECT.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, BUTTON_RECT)
    text_surf = FONT.render(BUTTON_TEXT, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=BUTTON_RECT.center)
    screen.blit(text_surf, text_rect)

def draw_solution():
    """Draw the solution instructions on the right with scrolling."""
    start_idx = scroll_offset
    end_idx = min(start_idx + MAX_VISIBLE_LINES, len(SOLUTION_TEXT))
    
    for i, line in enumerate(SOLUTION_TEXT[start_idx:end_idx]):
        text_surf = FONT.render(line, True, (0, 0, 0))
        screen.blit(text_surf, (SOLUTION_X_START, SPACING + i * TEXT_LINE_HEIGHT))

def get_cube_string():
    """Convert cube state to Kociemba string format (URFDLB order with face letters)."""
    COLOR_TO_FACE = {
        'W': 'U',  # White -> Up
        'Y': 'D',  # Yellow -> Down
        'R': 'R',  # Red -> Right
        'O': 'L',  # Orange -> Left
        'G': 'F',  # Green -> Front
        'B': 'B',  # Blue -> Back
        'X': 'U'   # Uncolored cells default to U for Kociemba
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
    """Handle mouse clicks on palette, cube faces, or button."""
    global selected_color, SOLUTION_TEXT, scroll_offset
    # Check palette clicks
    for x, y, color_key in PALETTE_POS:
        rect = pygame.Rect(x, y, COLOR_SIZE, COLOR_SIZE)
        if rect.collidepoint(pos):
            selected_color = color_key
            return

    # Check cube face clicks
    for face, face_pos in FACE_POSITIONS.items():
        for row in range(3):
            for col in range(3):
                rect = pygame.Rect(face_pos.x + col * CELL_SIZE, face_pos.y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if rect.collidepoint(pos) and (row, col) not in CENTER_CELLS:
                    CUBE_STATE[face][row][col] = selected_color
                    return

    # Check button click
    if BUTTON_RECT.collidepoint(pos):
        try:
            cube_string = get_cube_string()
            success, result = solve_cube(cube_string)
            if success:
                translated = translate_moves(result)
                SOLUTION_TEXT = translated if isinstance(translated, list) else [translated]
            else:
                SOLUTION_TEXT = [result]
            scroll_offset = 0  # Reset scroll position when new solution is generated
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
                # Handle scrolling with mouse wheel
                if SOLUTION_TEXT:
                    scroll_offset -= event.y  # event.y is positive for scroll up, negative for scroll down
                    scroll_offset = max(0, min(scroll_offset, len(SOLUTION_TEXT) - MAX_VISIBLE_LINES))
                    scroll_offset = max(0, scroll_offset)  # Ensure it doesn't go negative

        screen.fill((200, 200, 200))
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