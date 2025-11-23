# test_gui.py
import unittest
import tkinter as tk
from ttt_gui import TTTApp
from ttt_engine import winner, is_full

class GUITest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = TTTApp(self.root)
        self.root.update_idletasks()

    def tearDown(self):
        self.root.destroy()

    def click_cell(self, idx):
        r, c = idx // 3, idx % 3
        x = c * self.app.cell_size + self.app.cell_size // 2
        y = r * self.app.cell_size + self.app.cell_size // 2
        self.app.canvas.event_generate("<Button-1>", x=x, y=y)
        self.root.update()
        self.root.after(300)
        self.root.update()

    def test_gui_starts_and_human_can_play(self):
        self.click_cell(4)  # center
        self.assertEqual(self.app.board[4], "X")
        self.assertIn(self.app.board.count("O"), (1,))  # AI moved
        # Fill to draw
        for idx in [0,1,2,3,5,6,7,8]:
            if self.app.board[idx] == " ":
                self.click_cell(idx)
        self.assertTrue(is_full(self.app.board))
        self.assertIsNone(winner(self.app.board))

if __name__ == "__main__":
    unittest.main()