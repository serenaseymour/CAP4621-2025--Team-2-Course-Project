from dataclasses import dataclass
from typing import Literal, Tuple, List, Optional

Player = Literal["X", "O"]
Board = Tuple[str, str, str, str, str, str, str, str, str]

EMPTY = " "
WIN_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)
CENTER = 4
CORNERS = (0, 2, 6, 8)
EDGES = (1, 3, 5, 7)

def empty_board() -> Board:
    return (EMPTY,) * 9

def place(board: Board, move: int, player: Player) -> Board:
    if not (0 <= move <= 8):
        raise ValueError("move out of range")
    if board[move] != EMPTY:
        raise ValueError("cell occupied")
    lst = list(board)
    lst[move] = player
    return tuple(lst)

def legal_moves(board: Board) -> List[int]:
    return [i for i, c in enumerate(board) if c == EMPTY]

def winner(board: Board) -> Optional[Player]:
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return None

def is_full(board: Board) -> bool:
    return all(c != EMPTY for c in board)

def terminal(board: Board) -> bool:
    return winner(board) is not None or is_full(board)

def next_player(board: Board) -> Player:
    x_count = board.count("X")
    o_count = board.count("O")
    return "X" if x_count == o_count else "O"

def ordered_moves(board: Board) -> List[int]:
    mv = set(legal_moves(board))
    out: List[int] = []
    if CENTER in mv:
        out.append(CENTER)
        mv.remove(CENTER)
    for m in CORNERS:
        if m in mv:
            out.append(m)
    for m in EDGES:
        if m in mv:
            out.append(m)
    return out

@dataclass
class SearchResult:
    best_move: Optional[int]
    score: int
    nodes: int

def terminal_score(board: Board, ai: Player, depth: int) -> int:
    w = winner(board)
    if w is None:
        return 0
    if w == ai:
        return 10 - depth
    return depth - 10

def minimax(board: Board, ai: Player, to_move: Player, alpha: int, beta: int, depth: int = 0) -> SearchResult:
    if terminal(board):
        return SearchResult(best_move=None, score=terminal_score(board, ai, depth), nodes=1)
    nodes = 0
    best_move: Optional[int] = None
    moves = ordered_moves(board)
    if to_move == ai:
        best_score = -10**9
        for m in moves:
            child = place(board, m, to_move)
            r = minimax(child, ai, "O" if to_move == "X" else "X", alpha, beta, depth + 1)
            nodes += r.nodes
            if r.score > best_score:
                best_score = r.score
                best_move = m
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
        return SearchResult(best_move=best_move, score=best_score, nodes=nodes)
    else:
        best_score = 10**9
        for m in moves:
            child = place(board, m, to_move)
            r = minimax(child, ai, "O" if to_move == "X" else "X", alpha, beta, depth + 1)
            nodes += r.nodes
            if r.score < best_score:
                best_score = r.score
                best_move = m
            beta = min(beta, best_score)
            if alpha >= beta:
                break
        return SearchResult(best_move=best_move, score=best_score, nodes=nodes)

def ai_best_move(board: Board, ai: Player = "O") -> int:
    res = minimax(board, ai=ai, to_move=ai, alpha=-10**9, beta=10**9, depth=0)
    if res.best_move is None:
        raise RuntimeError("No move found")
    return res.best_move

