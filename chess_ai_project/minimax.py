from board import generate_moves, make_move, is_checkmate, is_stalemate, is_in_check
from symmetry_reducer import reduce_symmetry
import random

def evaluate_board_material(board, player):
    piece_values = {
        "pawn": 10,
        "knight": 30,
        "bishop": 30,
        "rook": 50,
        "queen": 90,
        "king": 1000
    }

    score = 0
    opponent = 'w' if player == 'b' else 'b'

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                color, ptype = piece.split("_")
                value = piece_values.get(ptype, 0)

                if color == player:
                    score += value
                else:
                    score -= value

    if is_checkmate(board, opponent):
        score += 10000
    elif is_checkmate(board, player):
        score -= 10000

    if is_in_check(board, opponent):
         score += 50

    return score

def evaluate_board_pst(board, player):
    pawn_pst = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    knight_pst = [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -30, -40, -50]
    ]

    bishop_pst = [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
    ]

    rook_pst = [
        [0, 0, 0, 5, 5, 0, 0, 0],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [5, 10, 10, 10, 10, 10, 10, 5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    queen_pst = [
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 5, 5, 5, 0, -10],
        [-5, 0, 5, 5, 5, 5, 0, -5],
        [0, 0, 5, 5, 5, 5, 0, -5],
        [-10, 5, 5, 5, 5, 5, 0, -10],
        [-10, 0, 5, 0, 0, 0, 0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ]

    king_pst_middle_game = [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [20, 20, 0, 0, 0, 0, 20, 20],
        [20, 30, 10, 0, 0, 10, 30, 20]
    ]

    pst_values = {
        "pawn": pawn_pst,
        "knight": knight_pst,
        "bishop": bishop_pst,
        "rook": rook_pst,
        "queen": queen_pst,
        "king": king_pst_middle_game
    }

    score = 0
    opponent = 'w' if player == 'b' else 'b'

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                color, ptype = piece.split("_")
                pst_table = pst_values.get(ptype)

                if pst_table:
                    r = row if color == 'w' else 7 - row
                    c = col

                    if color == player:
                        score += pst_table[r][c]
                    else:
                        score -= pst_table[r][c]

    if is_checkmate(board, opponent):
        score += 10000
    elif is_checkmate(board, player):
        score -= 10000

    if is_in_check(board, opponent):
         score += 50

    return score

def evaluate_board_combined(board, player):
    material_score = evaluate_board_material(board, player)
    pst_score = evaluate_board_pst(board, player)
    return material_score + pst_score

def minimax(board, depth, alpha, beta, maximizing_player, player, evaluate_func, use_symmetry=False):
    opponent = 'w' if player == 'b' else 'b'
    current_player = player if maximizing_player else opponent

    if depth == 0 or is_checkmate(board, opponent) or is_checkmate(board, player) or is_stalemate(board, player):
        return evaluate_func(board, player), None

    valid_moves = generate_moves(board, current_player)

    if use_symmetry:
        valid_moves = reduce_symmetry(valid_moves)

    if not valid_moves:
        return evaluate_func(board, player), None

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            new_board = make_move(board, move)
            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, False, player, evaluate_func, use_symmetry)

            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move

            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in valid_moves:
            new_board = make_move(board, move)
            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, True, player, evaluate_func, use_symmetry)

            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move

            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval, best_move

def minimax_no_ab(board, depth, maximizing_player, player, evaluate_func, use_symmetry=False):
    opponent = 'w' if player == 'b' else 'b'
    current_player = player if maximizing_player else opponent

    if depth == 0 or is_checkmate(board, opponent) or is_checkmate(board, player) or is_stalemate(board, player):
        return evaluate_func(board, player), None

    valid_moves = generate_moves(board, current_player)

    if use_symmetry:
        valid_moves = reduce_symmetry(valid_moves)

    if not valid_moves:
        return evaluate_func(board, player), None

    best_move = None

    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            new_board = make_move(board, move)
            evaluation, _ = minimax_no_ab(new_board, depth - 1, False, player, evaluate_func, use_symmetry)

            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in valid_moves:
            new_board = make_move(board, move)
            evaluation, _ = minimax_no_ab(new_board, depth - 1, True, player, evaluate_func, use_symmetry)

            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
        return min_eval, best_move


def simple_heuristic_ai(board, player, evaluate_func, use_symmetry=False):
    valid_moves = generate_moves(board, player)
    if not valid_moves:
        return None

    if use_symmetry:
        valid_moves = reduce_symmetry(valid_moves)

    best_move = None
    best_eval = float('-inf')

    for move in valid_moves:
        new_board = make_move(board, move)
        evaluation = evaluate_func(new_board, player)

        if evaluation > best_eval:
            best_eval = evaluation
            best_move = move
        elif evaluation == best_eval:
            if random.random() < 0.5:
                best_move = move

    return best_move

def pure_symmetry_reduction_ai(board, player, evaluate_func=None, use_symmetry=True):

    valid_moves = generate_moves(board, player)
    if not valid_moves:
        return None

    if use_symmetry:
        reduced_moves = reduce_symmetry(valid_moves)
        if reduced_moves:
            return reduced_moves[0]
        else:
            return valid_moves[0]
    else:
        return valid_moves[0]
