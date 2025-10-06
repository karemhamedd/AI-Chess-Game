import pygame
import sys
import os
import time
from pieces import load_piece_images, PIECE_IMAGES
from board import generate_moves, make_move, is_valid_move, is_checkmate, is_stalemate, is_in_check, board_state as initial_board_state
from minimax import minimax, minimax_no_ab, evaluate_board_material, evaluate_board_pst, evaluate_board_combined, simple_heuristic_ai, pure_symmetry_reduction_ai
from symmetry_reducer import reduce_symmetry
import random

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 721
ROWS, COLS = 8, 8
SQUARE_SIZE = min(WIDTH, HEIGHT) // COLS

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess AI Project")

LIGHT_SQUARE = (245, 222, 179)
DARK_SQUARE = (139, 69, 19)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
TRANSPARENT_GRAY = (128, 128, 128, 150)

START_MENU = 0
MAIN_MENU = 1
GAME = 2
GAME_OVER = 3

current_state = START_MENU

ASSETS_DIR = "assets"
COVER1_PATH = os.path.join(ASSETS_DIR, "cover1.png")
COVER2_PATH = os.path.join(ASSETS_DIR, "cover2.png")
BACKGROUND_MUSIC_PATH = os.path.join(ASSETS_DIR, "background.wav")
WIN_SOUND_PATH = os.path.join(ASSETS_DIR, "win.wav")
LOSE_SOUND_PATH = os.path.join(ASSETS_DIR, "lose.wav")
CLICK_SOUND_PATH = os.path.join(ASSETS_DIR, "click.wav")

try:
    cover1_img = pygame.image.load(COVER1_PATH)
    cover1_img = pygame.transform.scale(cover1_img, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Warning: Could not load cover1.png: {e}")
    cover1_img = None

try:
    cover2_img = pygame.image.load(COVER2_PATH)
    cover2_img = pygame.transform.scale(cover2_img, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Warning: Could not load cover2.png: {e}")
    cover2_img = None

try:
    background_music = pygame.mixer.Sound(BACKGROUND_MUSIC_PATH)
except pygame.error as e:
    print(f"Warning: Could not load background.wav: {e}")
    background_music = None

try:
    win_sound = pygame.mixer.Sound(WIN_SOUND_PATH)
except pygame.error as e:
    print(f"Warning: Could not load win.wav: {e}")
    win_sound = None

try:
    lose_sound = pygame.mixer.Sound(LOSE_SOUND_PATH)
except pygame.error as e:
    print(f"Warning: Could not load lose.wav: {e}")
    lose_sound = None

try:
    click_sound = pygame.mixer.Sound(CLICK_SOUND_PATH)
except pygame.error as e:
    print(f"Warning: Could not load click.wav: {e}")
    click_sound = None

board_state = [row[:] for row in initial_board_state]
selected_piece = None
valid_moves_for_selected = []
player_turn = "w"
dragging = False
game_over = False
result_message = ""
last_ai_move = None
ai_algorithm_func = None
ai_heuristic_func = None
ai_use_symmetry = False
ai_response_time = 0.0

font = pygame.font.SysFont('Arial', 40)
button_font = pygame.font.SysFont('Arial', 30)
timer_font = pygame.font.SysFont('Arial', 25)

class Button:
    def __init__(self, text, x, y, width, height, color, text_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def draw(self, win):
        self.surface.fill(TRANSPARENT_GRAY)
        win.blit(self.surface, (self.rect.x, self.rect.y))

        pygame.draw.rect(win, self.color, self.rect, 2)

        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        win.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

start_button = Button("Start New Game", 50, HEIGHT - 100, 250, 60, GRAY, WHITE, action="start_game")
exit_button = Button("Exit", 350, HEIGHT - 100, 250, 60, GRAY, WHITE, action="exit")

main_menu_buttons = []

def create_main_menu_buttons():
    global main_menu_buttons
    button_width = 600
    button_height = 60
    spacing = 15
    options = [
        ("Minimax (No Alpha-Beta, Material)", {"algorithm": "minimax_no_ab", "heuristic": "material", "symmetry": False}),
        ("Minimax with Alpha-Beta (Material)", {"algorithm": "minimax_ab", "heuristic": "material", "symmetry": False}),
        ("Heuristic (Material Balance)", {"algorithm": "greedy", "heuristic": "material", "symmetry": False}),
        ("Heuristic (Piece-Square Tables)", {"algorithm": "greedy", "heuristic": "pst", "symmetry": False}),
        ("Minimax (Alpha-Beta, PST)", {"algorithm": "minimax_ab", "heuristic": "pst", "symmetry": False}),
        ("Minimax (Alpha-Beta, Combined Heuristics)", {"algorithm": "minimax_ab", "heuristic": "combined", "symmetry": False}),
        ("Symmetry Reduction Only (Pure)", {"algorithm": "pure_symmetry", "heuristic": None, "symmetry": True}),
        ("Heuristic Reduction (Greedy Material + Symmetry)", {"algorithm": "greedy", "heuristic": "material", "symmetry": True}),
    ]

    total_buttons = len(options)
    total_height = total_buttons * button_height + (total_buttons - 1) * spacing
    start_y = (HEIGHT - total_height) // 2
    center_x = WIDTH // 2

    main_menu_buttons = []
    for i, (text, action_params) in enumerate(options):
        y = start_y + i * (button_height + spacing)
        x = center_x - button_width // 2
        main_menu_buttons.append(Button(text, x, y, button_width, button_height, GRAY, WHITE, action=action_params))

create_main_menu_buttons()


def draw_board(win):
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    if last_ai_move:
        from_pos, to_pos = last_ai_move
        for pos in [from_pos, to_pos]:
            row, col = pos[0], pos[1]
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((255, 255, 0, 100))
            win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))


def draw_pieces(win, board):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != "":
                img = PIECE_IMAGES.get(piece)
                if img:
                    rect = img.get_rect(center=(
                        col * SQUARE_SIZE + SQUARE_SIZE // 2,
                        row * SQUARE_SIZE + SQUARE_SIZE // 2))
                    win.blit(img, rect)


def draw_valid_moves(win, valid_moves):
    for move in valid_moves:
        row, col = move
        center = (col * SQUARE_SIZE + SQUARE_SIZE // 2,
                  row * SQUARE_SIZE + SQUARE_SIZE // 2)
        radius = SQUARE_SIZE // 6
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(s, (100, 200, 100, 100), (SQUARE_SIZE // 2, SQUARE_SIZE // 2), radius)
        win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))


def display_game_over(win, message):
    font = pygame.font.SysFont('Arial', 40)
    text = font.render(message, True, WHITE)

    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    win.blit(s, (0, 0))

    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    win.blit(text, text_rect)

    restart_font = pygame.font.SysFont('Arial', 30)
    restart_text = restart_font.render("Click anywhere to return to main menu", True, (200, 200, 200))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    win.blit(restart_text, restart_rect)

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return True


def reset_game():
    global board_state, player_turn, selected_piece, valid_moves_for_selected, dragging, game_over, result_message, last_ai_move, ai_response_time
    board_state = [row[:] for row in initial_board_state]
    player_turn = "w"
    selected_piece = None
    valid_moves_for_selected = []
    dragging = False
    game_over = False
    result_message = ""
    last_ai_move = None
    ai_response_time = 0.0


def handle_start_menu_click(pos):
    global current_state
    if start_button.is_clicked(pos):
        if click_sound:
            click_sound.play()
        current_state = MAIN_MENU
    elif exit_button.is_clicked(pos):
        if click_sound:
            click_sound.play()
        pygame.quit()
        sys.exit()

def handle_main_menu_click(pos):
    global current_state, ai_algorithm_func, ai_heuristic_func, ai_use_symmetry, ai_response_time
    for button in main_menu_buttons:
        if button.is_clicked(pos):
            if click_sound:
                click_sound.play()
            action_params = button.action

            ai_type = action_params.get("algorithm")
            heuristic_type = action_params.get("heuristic")
            ai_use_symmetry = action_params.get("symmetry", False)

            if ai_type == "minimax_ab":
                ai_algorithm_func = minimax
            elif ai_type == "minimax_no_ab":
                 ai_algorithm_func = minimax_no_ab
            elif ai_type == "greedy":
                ai_algorithm_func = simple_heuristic_ai
            elif ai_type == "pure_symmetry":
                 ai_algorithm_func = pure_symmetry_reduction_ai
            else:
                ai_algorithm_func = minimax

            if heuristic_type == "material":
                ai_heuristic_func = evaluate_board_material
            elif heuristic_type == "pst":
                ai_heuristic_func = evaluate_board_pst
            elif heuristic_type == "combined":
                 ai_heuristic_func = evaluate_board_combined
            else:
                 ai_heuristic_func = None

            reset_game()
            ai_response_time = 0.0
            current_state = GAME
            if background_music:
                background_music.stop()


def game_loop():
    global selected_piece, valid_moves_for_selected, player_turn, board_state, dragging, game_over, result_message, last_ai_move, current_state, ai_algorithm_func, ai_heuristic_func, ai_use_symmetry, ai_response_time

    clock = pygame.time.Clock()
    load_piece_images(SQUARE_SIZE)

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_state == START_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    handle_start_menu_click(event.pos)

            elif current_state == MAIN_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    handle_main_menu_click(event.pos)

            elif current_state == GAME:
                if not game_over and player_turn == "w":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        col = pos[0] // SQUARE_SIZE
                        row = pos[1] // SQUARE_SIZE
                        if 0 <= row < 8 and 0 <= col < 8:
                            piece = board_state[row][col]
                            if piece.startswith(player_turn):
                                selected_piece = (row, col)
                                all_valid_moves = generate_moves(board_state, player_turn)
                                valid_moves_for_selected = [move[1] for move in all_valid_moves if move[0] == selected_piece]
                                dragging = True

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if dragging and selected_piece:
                            pos = event.pos
                            col = pos[0] // SQUARE_SIZE
                            row = pos[1] // SQUARE_SIZE
                            if 0 <= row < 8 and 0 <= col < 8:
                                move = (selected_piece, (row, col))
                                if (row, col) in valid_moves_for_selected and is_valid_move(board_state, move, player_turn):
                                    if click_sound:
                                        click_sound.play()
                                    board_state = make_move(board_state, move)
                                    if is_checkmate(board_state, "b"):
                                        game_over = True
                                        result_message = "You Win! Checkmate."
                                        if win_sound:
                                            win_sound.play()
                                    elif is_stalemate(board_state, "b"):
                                        game_over = True
                                        result_message = "Draw! Stalemate."
                                    else:
                                        player_turn = "b"
                                else:
                                    selected_piece = None
                                    valid_moves_for_selected = []
                                    dragging = False
                                    continue

                            selected_piece = None
                            valid_moves_for_selected = []
                            dragging = False

        if current_state == START_MENU:
            if cover1_img:
                WIN.blit(cover1_img, (0, 0))
            else:
                WIN.fill(BLACK)
            start_button.draw(WIN)
            exit_button.draw(WIN)

        elif current_state == MAIN_MENU:
            if cover2_img:
                WIN.blit(cover2_img, (0, 0))
            else:
                WIN.fill(BLACK)
            for button in main_menu_buttons:
                button.draw(WIN)

        elif current_state == GAME:
            WIN.fill(BLACK)
            draw_board(WIN)
            draw_pieces(WIN, board_state)

            if selected_piece and not game_over:
                draw_valid_moves(WIN, valid_moves_for_selected)

            if game_over:
                if display_game_over(WIN, result_message):
                    current_state = MAIN_MENU
                    if background_music:
                        background_music.play(-1)

            if not game_over and player_turn == "b" and ai_algorithm_func:
                pygame.display.update()

                start_time = time.time()

                if ai_algorithm_func == minimax:
                    ai_move_eval, ai_move = ai_algorithm_func(board_state, depth=3, alpha=float('-inf'), beta=float('inf'), maximizing_player=True, player="b", evaluate_func=ai_heuristic_func, use_symmetry=ai_use_symmetry)
                elif ai_algorithm_func == minimax_no_ab:
                     ai_move_eval, ai_move = ai_algorithm_func(board_state, depth=3, maximizing_player=True, player="b", evaluate_func=ai_heuristic_func, use_symmetry=ai_use_symmetry)
                elif ai_algorithm_func == simple_heuristic_ai:
                    ai_move = ai_algorithm_func(board_state, player="b", evaluate_func=ai_heuristic_func, use_symmetry=ai_use_symmetry)
                elif ai_algorithm_func == pure_symmetry_reduction_ai:
                     ai_move = ai_algorithm_func(board_state, player="b", use_symmetry=ai_use_symmetry)
                else:
                    ai_move = None

                end_time = time.time()
                ai_response_time = end_time - start_time

                if ai_move:
                    last_ai_move = ai_move
                    board_state = make_move(board_state, ai_move)
                    if click_sound:
                        click_sound.play()
                    if is_checkmate(board_state, "w"):
                        game_over = True
                        result_message = "AI Wins! Checkmate."
                        if lose_sound:
                            lose_sound.play()
                    elif is_stalemate(board_state, "w"):
                        game_over = True
                        result_message = "Draw! Stalemate."
                    else:
                        player_turn = "w"
                else:
                    if is_in_check(board_state, "b"):
                        game_over = True
                        result_message = "You Win! Checkmate."
                        if win_sound:
                            win_sound.play()
                    else:
                        game_over = True
                        result_message = "Draw! Stalemate."

            if ai_response_time > 0:
                timer_text = timer_font.render(f"AI Response Time: {ai_response_time:.4f} seconds", True, WHITE)
                WIN.blit(timer_text, (10, 10))


        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    if background_music:
        background_music.play(-1)
    game_loop()
