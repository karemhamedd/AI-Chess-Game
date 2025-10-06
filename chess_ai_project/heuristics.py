piece_values = {
    'p': 10,
    'r': 50,
    'n': 30,
    'b': 30,
    'q': 90,
    'k': 900
}

def evaluate_board(board):
    score = 0
    for row in board:
        for piece in row:
            if piece == '.':
                continue
            value = piece_values[piece.lower()]
            if piece.isupper():
                score -= value
            else:
                score += value
    return score
