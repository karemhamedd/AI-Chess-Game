def inside_board(row, col):
    return 0 <= row < 8 and 0 <= col < 8


def is_square_threatened_by_pawn(board, row, col, player):
    enemy = 'b' if player == 'w' else 'w'
    pawn_direction = 1 if enemy == 'b' else -1

    for dc in [-1, 1]:
        pr, pc = row - pawn_direction, col + dc
        if inside_board(pr, pc):
            piece = board[pr][pc]
            if piece == f"{enemy}_pawn":
                return True
    return False


def generate_moves(board, player):
    moves = []
    enemy_prefix = "w_" if player == "b" else "b_"
    enemy = 'b' if player == 'w' else 'w'

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if not piece.startswith(player):
                continue

            piece_type = piece[2:]

            if piece_type == "pawn":
                direction = 1 if player == "b" else -1

                nr, nc = r + direction, c
                if inside_board(nr, nc) and board[nr][nc] == "":
                    temp_board = make_move(board, ((r, c), (nr, nc)))
                    if not is_in_check(temp_board, player):
                        moves.append(((r, c), (nr, nc)))

                    start_row = 1 if player == "b" else 6
                    if r == start_row:
                        nr2 = r + 2 * direction
                        if inside_board(nr2, nc) and board[nr2][nc] == "" and board[nr][nc] == "":
                            temp_board = make_move(board, ((r, c), (nr2, nc)))
                            if not is_in_check(temp_board, player):
                                moves.append(((r, c), (nr2, nc)))

                for dc in [-1, 1]:
                    nr, nc = r + direction, c + dc
                    if inside_board(nr, nc) and board[nr][nc].startswith(enemy_prefix):
                        if not board[nr][nc].endswith("king"):
                            temp_board = make_move(board, ((r, c), (nr, nc)))
                            if not is_in_check(temp_board, player):
                                moves.append(((r, c), (nr, nc)))

            elif piece_type == "king":
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if inside_board(nr, nc) and not board[nr][nc].startswith(player):
                            temp_board = [row[:] for row in board]
                            temp_board[r][c] = ""
                            temp_board[nr][nc] = f"{player}_king"
                            if not is_in_check(temp_board, player):
                                moves.append(((r, c), (nr, nc)))

            elif piece_type == "knight":
                for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                    nr, nc = r + dr, c + dc
                    if inside_board(nr, nc) and not board[nr][nc].startswith(player):
                        if not board[nr][nc].endswith("king"):
                            temp_board = make_move(board, ((r, c), (nr, nc)))
                            if not is_in_check(temp_board, player):
                                moves.append(((r, c), (nr, nc)))

            elif piece_type == "bishop":
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nr, nc = r + dr, c + dc
                    while inside_board(nr, nc):
                        if board[nr][nc] == "":
                            temp_board = make_move(board, ((r, c), (nr, nc)))
                            if not is_in_check(temp_board, player):
                                moves.append(((r, c), (nr, nc)))
                        elif board[nr][nc].startswith(enemy_prefix):
                            if not board[nr][nc].endswith("king"):
                                temp_board = make_move(board, ((r, c), (nr, nc)))
                                if not is_in_check(temp_board, player):
                                    moves.append(((r, c), (nr, nc)))
                            break
                        else:
                            break
                        nr += dr
                        nc += dc

            elif piece_type == "rook":
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    while inside_board(nr, nc):
                        if board[nr][nc] == "":
                            temp_board = make_move(board, ((r, c), (nr, nc)))
                            if not is_in_check(temp_board, player):
                                moves.append(((r, c), (nr, nc)))
                        elif board[nr][nc].startswith(enemy_prefix):
                            if not board[nr][nc].endswith("king"):
                                temp_board = make_move(board, ((r, c), (nr, nc)))
                                if not is_in_check(temp_board, player):
                                    moves.append(((r, c), (nr, nc)))
                            break
                        else:
                            break
                        nr += dr
                        nc += dc

            elif piece_type == "queen":
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    while inside_board(nr, nc):
                        if board[nr][nc] == "":
                            temp_board = make_move(board, ((r, c), (nr, nc)))
                            if not is_in_check(temp_board, player):
                                moves.append(((r, c), (nr, nc)))
                        elif board[nr][nc].startswith(enemy_prefix):
                            if not board[nr][nc].endswith("king"):
                                temp_board = make_move(board, ((r, c), (nr, nc)))
                                if not is_in_check(temp_board, player):
                                    moves.append(((r, c), (nr, nc)))
                            break
                        else:
                            break
                        nr += dr
                        nc += dc

    return moves


def is_valid_move(board, move, player):
    from_pos, to_pos = move
    from_row, from_col = from_pos
    to_row, to_col = to_pos

    if not inside_board(from_row, from_col) or not board[from_row][from_col].startswith(player):
        return False

    if not inside_board(to_row, to_col):
        return False

    if board[to_row][to_col].startswith(player):
        return False

    if board[to_row][to_col].endswith("king"):
        return False

    legal_moves = generate_moves(board, player)
    return move in legal_moves


def make_move(board, move):
    from_row, from_col = move[0]
    to_row, to_col = move[1]

    new_board = [row[:] for row in board]

    piece = new_board[from_row][from_col]
    new_board[from_row][from_col] = ""

    if piece.endswith("pawn"):
        if (piece.startswith("w") and to_row == 0) or (piece.startswith("b") and to_row == 7):
            promoted_piece = piece[0] + "_queen"
            new_board[to_row][to_col] = promoted_piece
            return new_board

    new_board[to_row][to_col] = piece

    return new_board


def find_king(board, player):
    for r in range(8):
        for c in range(8):
            if board[r][c] == f"{player}_king":
                return (r, c)
    return None


def is_in_check(board, player):
    king_pos = find_king(board, player)
    if not king_pos:
        return False

    king_row, king_col = king_pos
    opponent = 'w' if player == 'b' else 'b'

    if is_square_threatened_by_pawn(board, king_row, king_col, player):
        return True

    for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
        nr, nc = king_row + dr, king_col + dc
        if inside_board(nr, nc):
            piece = board[nr][nc]
            if piece == f"{opponent}_knight":
                return True

    for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = king_row + dr, king_col + dc
        while inside_board(nr, nc):
            piece = board[nr][nc]
            if piece != "":
                if piece.startswith(opponent):
                    piece_type = piece[2:]
                    if (piece_type == "bishop" and abs(dr) == abs(dc)) or \
                       (piece_type == "rook" and (dr == 0 or dc == 0)) or \
                       (piece_type == "queen"):
                        return True
                break
            nr += dr
            nc += dc

    return False


def is_checkmate(board, player):
    if is_in_check(board, player):
        return len(generate_moves(board, player)) == 0
    return False


def is_stalemate(board, player):
    if not is_in_check(board, player):
        return len(generate_moves(board, player)) == 0
    return False

board_state = [
    ["b_rook", "b_knight", "b_bishop", "b_queen", "b_king", "b_bishop", "b_knight", "b_rook"],
    ["b_pawn"] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    ["w_pawn"] * 8,
    ["w_rook", "w_knight", "w_bishop", "w_queen", "w_king", "w_bishop", "w_knight", "w_rook"],
]