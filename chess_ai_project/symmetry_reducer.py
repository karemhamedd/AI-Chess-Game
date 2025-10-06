def reduce_symmetry(moves):
    unique_moves = []
    seen_moves = set()

    for from_pos, to_pos in moves:
        move_str = f"{from_pos[0]}{from_pos[1]}{to_pos[0]}{to_pos[1]}"

        flipped_from = (from_pos[0], 7 - from_pos[1])
        flipped_to = (to_pos[0], 7 - to_pos[1])
        flipped_move_str = f"{flipped_from[0]}{flipped_from[1]}{flipped_to[0]}{flipped_to[1]}"

        if move_str not in seen_moves and flipped_move_str not in seen_moves:
            unique_moves.append((from_pos, to_pos))
            seen_moves.add(move_str)
            seen_moves.add(flipped_move_str)

    return unique_moves
