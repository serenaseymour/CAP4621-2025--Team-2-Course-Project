# test_engine.py
import unittest
from ttt_engine import (
    EMPTY, WIN_LINES,
    empty_board, place, winner, is_full, terminal,
    next_player, legal_moves, ordered_moves,
    ai_best_move
)

class TestTTTEngine(unittest.TestCase):

    def test_empty_board(self):
        board = empty_board()
        self.assertEqual(len(board), 9)
        self.assertTrue(all(c == EMPTY for c in board))

    def test_place_valid(self):
        board = empty_board()
        new_board = place(board, 4, "X")
        self.assertEqual(new_board[4], "X")

    def test_place_invalid(self):
        board = place(empty_board(), 0, "X")
        with self.assertRaises(ValueError):
            place(board, 0, "O")
        with self.assertRaises(ValueError):
            place(board, 9, "O")

    def test_winner_row(self):
        board = place(place(place(empty_board(), 0, "X"), 1, "X"), 2, "X")
        self.assertEqual(winner(board), "X")

    def test_winner_column(self):
        board = place(place(place(empty_board(), 1, "O"), 4, "O"), 7, "O")
        self.assertEqual(winner(board), "O")

    def test_winner_diagonal(self):
        board = place(place(place(empty_board(), 0, "X"), 4, "X"), 8, "X")
        self.assertEqual(winner(board), "X")

    def test_no_winner(self):
        board = place(empty_board(), 0, "X")
        self.assertIsNone(winner(board))

    def test_is_full_draw(self):
        board = ("X", "O", "X", "X", "O", "O", "O", "X", "X")
        self.assertTrue(is_full(board))
        self.assertIsNone(winner(board))

    def test_next_player_start(self):
        self.assertEqual(next_player(empty_board()), "X")

    def test_next_player_after_one_move(self):
        board = place(empty_board(), 0, "X")
        self.assertEqual(next_player(board), "O")

    def test_ordered_moves_center_first(self):
        board = empty_board()
        moves = ordered_moves(board)
        self.assertEqual(moves[0], 4)

    def test_ai_takes_center_when_free(self):
        self.assertEqual(ai_best_move(empty_board(), "O"), 4)

    def test_ai_blocks_immediate_win(self):
        board = place(place(empty_board(), 0, "X"), 1, "X")
        self.assertEqual(ai_best_move(board, "O"), 2)

    def test_ai_forces_win_when_possible(self):
        board = place(place(place(empty_board(), 0, "O"), 1, "O"), 3, "X")
        self.assertEqual(ai_best_move(board, "O"), 2)

    def test_ai_never_loses(self):
        board = empty_board()
        human_moves = [0, 1, 3, 6]  # Try to trap AI
        for i, m in enumerate(human_moves):
            board = place(board, m, "X")
            if not terminal(board):
                ai_move = ai_best_move(board, "O")
                board = place(board, ai_move, "O")
        self.assertTrue(is_full(board) or winner(board) == "O")

if __name__ == "__main__":
    unittest.main(verbosity=2)