# --- Smarter Chess Engine Logic ---

import random

# Piece-square tables for basic positional value (white's POV; adjust for black)
PIECE_SQUARE_TABLES = {
    'p': [  # Pawn
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 5, 10, 10,-20,-20, 10, 10,  5],
        [ 5, -5,-10,  0,  0,-10, -5,  5],
        [ 0,  0,  0, 20, 20,  0,  0,  0],
        [ 5,  5, 10, 25, 25, 10,  5,  5],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [ 0,  0,  0,  0,  0,  0,  0,  0]
    ],
    'N': [  # Knight
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50],
    ],
    # Add tables for other pieces ('B', 'R', 'Q', 'K') for even smarter play.
}

def is_white(piece): return piece and piece[0] == "w"
def is_black(piece): return piece and piece[0] == "b"

def all_moves(board, turn):
    # TODO: Add castling, en passant, and promotion support for full rules.
    moves = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if not piece: continue
            if (turn == "w" and not is_white(piece)) or (turn == "b" and not is_black(piece)): continue
            ptype = piece[1]
            direction = -1 if turn=="w" else 1
            # Pawn moves
            if ptype == "p":
                nr = r + direction
                if 0 <= nr < 8:
                    if not board[nr][c]:
                        # Promotion support
                        if (turn == "w" and nr == 0) or (turn == "b" and nr == 7):
                            moves.append((r, c, nr, c, 'Q'))
                        else:
                            moves.append((r, c, nr, c, None))
                    for dc in [-1,1]:
                        nc = c + dc
                        if 0 <= nc < 8 and board[nr][nc] and ((turn == "w" and is_black(board[nr][nc])) or (turn == "b" and is_white(board[nr][nc]))):
                            # Promotion on capture
                            if (turn == "w" and nr == 0) or (turn == "b" and nr == 7):
                                moves.append((r, c, nr, nc, 'Q'))
                            else:
                                moves.append((r, c, nr, nc, None))
            elif ptype == "N":
                for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                    nr, nc = r + dr, c + dc
                    if 0<=nr<8 and 0<=nc<8 and (not board[nr][nc] or (turn == "w" and is_black(board[nr][nc])) or (turn == "b" and is_white(board[nr][nc]))):
                        moves.append((r,c,nr,nc,None))
            elif ptype in "BRQ":
                directions = []
                if ptype in "BQ": directions += [(-1,-1),(1,1),(-1,1),(1,-1)]
                if ptype in "RQ": directions += [(-1,0),(1,0),(0,-1),(0,1)]
                for dr, dc in directions:
                    nr, nc = r+dr, c+dc
                    while 0<=nr<8 and 0<=nc<8:
                        if not board[nr][nc]:
                            moves.append((r,c,nr,nc,None))
                        elif (turn=="w" and is_black(board[nr][nc])) or (turn=="b" and is_white(board[nr][nc])):
                            moves.append((r,c,nr,nc,None))
                            break
                        else: break
                        nr += dr; nc += dc
            elif ptype == "K":
                for dr in [-1,0,1]:
                    for dc in [-1,0,1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = r+dr, c+dc
                        if 0<=nr<8 and 0<=nc<8 and (not board[nr][nc] or (turn=="w" and is_black(board[nr][nc])) or (turn=="b" and is_white(board[nr][nc]))):
                            moves.append((r,c,nr,nc,None))
    return moves

def do_move(board, move):
    # move: (from_r, from_c, to_r, to_c, promotion_type)
    r1, c1, r2, c2, promotion = move
    new_board = [row[:] for row in board]
    if promotion:
        new_board[r2][c2] = new_board[r1][c1][0] + promotion
    else:
        new_board[r2][c2] = new_board[r1][c1]
    new_board[r1][c1] = ""
    return new_board

def score_board(board):
    # Improved material + piece-square table + random for variety.
    values = {'p':100, 'N':320, 'B':330, 'R':500, 'Q':900, 'K':20000}
    total = 0
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if not p: continue
            val = values.get(p[1], 0)
            color_factor = 1 if p[0]=='w' else -1
            total += color_factor * val
            # Positional value
            pst = PIECE_SQUARE_TABLES.get(p[1])
            if pst:
                idx_r = r if p[0] == 'w' else 7 - r # invert for black
                total += color_factor * pst[idx_r][c]
    # Add random tweak for unpredictability
    total += random.randint(-5, 5)
    return total

def is_checkmate(board, turn):
    # No moves, king attacked
    moves = all_moves(board, turn)
    if moves: return False
    # TODO: Actually check if king is attacked for true checkmate detection
    return True

def alphabeta(board, turn, depth, alpha, beta):
    if depth == 0 or is_checkmate(board, turn):
        return score_board(board), None
    moves = all_moves(board, turn)
    best_move = None
    if turn == "w":
        max_eval = -float("inf")
        for move in moves:
            new_board = do_move(board, move)
            score, _ = alphabeta(new_board, "b", depth-1, alpha, beta)
            if score > max_eval:
                max_eval = score
                best_move = move
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float("inf")
        for move in moves:
            new_board = do_move(board, move)
            score, _ = alphabeta(new_board, "w", depth-1, alpha, beta)
            if score < min_eval:
                min_eval = score
                best_move = move
            beta = min(beta, score)
            if beta <= alpha:
                break
        return min_eval, best_move

# Example call
# score, move = alphabeta(board, turn, 3, -float("inf"), float("inf"))
