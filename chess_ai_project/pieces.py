import pygame
import os

PIECE_IMAGES = {}

def load_piece_images(square_size):
    pieces = [
        "w_pawn", "w_rook", "w_knight", "w_bishop", "w_queen", "w_king",
        "b_pawn", "b_rook", "b_knight", "b_bishop", "b_queen", "b_king"
    ]
    for piece in pieces:
        img_path = os.path.join("assets", piece + ".png")
        try:
            image = pygame.image.load(img_path)
            PIECE_IMAGES[piece] = pygame.transform.scale(image, (square_size, square_size))
        except pygame.error as e:
            print(f"Warning: Could not load piece image {img_path}: {e}")
            PIECE_IMAGES[piece] = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            PIECE_IMAGES[piece].fill((200, 200, 200, 100))
