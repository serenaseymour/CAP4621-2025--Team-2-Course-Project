import tkinter as tk
from typing import List, Optional, Tuple

from ttt_engine import (
    Player,
    EMPTY,
    empty_board,
    place,
    winner,
    is_full,
    terminal,
    next_player,
    ai_best_move,
    WIN_LINES,
)

BG = "#0f172a"
PANEL = "#111827"
TEXT = "#e5e7eb"
SUBTLE = "#94a3b8"
GRID = "#38bdf8"
HOVER = "#1f2937"
X_COLOR = "#f43f5e"
O_COLOR = "#22c55e"
WIN_COLOR = "#fbbf24"
BTN_BG = "#1d4ed8"
BTN_FG = "#ffffff"
BTN_BG2 = "#047857"

class TTTApp:
    def __init__(self, root: "tk.Tk") -> None:
        self.root = root
        self.root.title("Tic-Tac-Toe • Minimax AI")
        self.root.configure(bg=BG)
        self.board = empty_board()
        self.human: Player = "X"
        self.ai: Player = "O"
        self.score_x = 0
        self.score_o = 0
        self.score_d = 0
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", pady=(12, 6))
        self.title_lbl = tk.Label(header, text="Tic-Tac-Toe", fg=TEXT, bg=BG, font=("Helvetica", 18, "bold"))
        self.title_lbl.pack(side="left", padx=16)
        self.badge_turn = tk.Label(header, text="Your turn: X", fg=BG, bg="#a7f3d0", font=("Helvetica", 11, "bold"), padx=10, pady=4)
        self.badge_turn.pack(side="right", padx=12)
        scores = tk.Frame(root, bg=BG)
        scores.pack(fill="x", pady=(0, 10))
        self.sx = tk.Label(scores, text="X: 0", fg=X_COLOR, bg=BG, font=("Helvetica", 12, "bold"))
        self.so = tk.Label(scores, text="O: 0", fg=O_COLOR, bg=BG, font=("Helvetica", 12, "bold"))
        self.sd = tk.Label(scores, text="Draws: 0", fg=SUBTLE, bg=BG, font=("Helvetica", 12, "bold"))
        self.sx.pack(side="left", padx=16)
        self.sd.pack(side="left", padx=16)
        self.so.pack(side="left", padx=16)
        panel = tk.Frame(root, bg=PANEL, bd=0, highlightthickness=0)
        panel.pack(padx=16, pady=8)
        self.canvas = tk.Canvas(panel, width=360, height=360, bg=PANEL, highlightthickness=0)
        self.canvas.pack()
        controls = tk.Frame(root, bg=BG)
        controls.pack(fill="x", pady=(8, 16))
        self.new_btn = tk.Button(controls, text="New Game", command=self.restart, bg=BTN_BG, fg=BTN_FG, activebackground="#1e40af", activeforeground=BTN_FG, relief="flat", padx=16, pady=8)
        self.new_btn.pack(side="left", padx=(16, 8))
        self.swap_btn = tk.Button(controls, text="Play First: ON", command=self.toggle_first, bg=BTN_BG2, fg=BTN_FG, activebackground="#065f46", activeforeground=BTN_FG, relief="flat", padx=16, pady=8)
        self.swap_btn.pack(side="left", padx=8)
        self.status = tk.Label(root, text="Click any empty square.", fg=SUBTLE, bg=BG, font=("Helvetica", 11))
        self.status.pack(pady=(0, 8))
        self.cell_size = 120
        self.cells_rect: List[int] = []
        self.hover_rect: Optional[int] = None
        self.win_line: Optional[int] = None
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Button-1>", self.on_click)
        self.draw_grid()
        self.refresh()

    def idx_rc(self, idx: int) -> Tuple[int, int]:
        return idx // 3, idx % 3

    def rc_idx(self, r: int, c: int) -> int:
        return r * 3 + c

    def cell_bounds(self, r: int, c: int) -> Tuple[int, int, int, int]:
        x0 = c * self.cell_size
        y0 = r * self.cell_size
        x1 = x0 + self.cell_size
        y1 = y0 + self.cell_size
        return x0, y0, x1, y1

    def draw_grid(self) -> None:
        self.canvas.delete("all")
        self.cells_rect.clear()
        for r in range(3):
            for c in range(3):
                x0, y0, x1, y1 = self.cell_bounds(r, c)
                rect = self.canvas.create_rectangle(x0+2, y0+2, x1-2, y1-2, fill=HOVER, outline=PANEL, width=2)
                self.cells_rect.append(rect)
        for i in range(1, 3):
            self.canvas.create_line(i*self.cell_size, 15, i*self.cell_size, 360-15, fill=GRID, width=4, capstyle="round")
            self.canvas.create_line(15, i*self.cell_size, 360-15, i*self.cell_size, fill=GRID, width=4, capstyle="round")

    def draw_marks(self) -> None:
        for i, mark in enumerate(self.board):
            r, c = self.idx_rc(i)
            x0, y0, x1, y1 = self.cell_bounds(r, c)
            pad = 26
            if mark == "X":
                self.canvas.create_line(x0+pad, y0+pad, x1-pad, y1-pad, fill=X_COLOR, width=10, capstyle="round")
                self.canvas.create_line(x0+pad, y1-pad, x1-pad, y0+pad, fill=X_COLOR, width=10, capstyle="round")
            elif mark == "O":
                self.canvas.create_oval(x0+pad, y0+pad, x1-pad, y1-pad, outline=O_COLOR, width=10)

    def highlight_winner(self) -> None:
        self.clear_win_line()
        w = winner(self.board)
        if not w:
            return
        for a, b, c in WIN_LINES:
            if self.board[a] == self.board[b] == self.board[c] != EMPTY:
                ra, ca = self.idx_rc(a)
                rc, cc = self.idx_rc(c)
                ax = ca * self.cell_size + self.cell_size // 2
                ay = ra * self.cell_size + self.cell_size // 2
                cx = cc * self.cell_size + self.cell_size // 2
                cy = rc * self.cell_size + self.cell_size // 2
                self.win_line = self.canvas.create_line(ax, ay, cx, cy, fill=WIN_COLOR, width=12, capstyle="round")
                break

    def clear_win_line(self) -> None:
        if self.win_line:
            self.canvas.delete(self.win_line)
            self.win_line = None

    def on_motion(self, e: tk.Event) -> None:
        if terminal(self.board) or next_player(self.board) != self.human:
            self.clear_hover()
            return
        c = e.x // self.cell_size
        r = e.y // self.cell_size
        if not (0 <= r < 3 and 0 <= c < 3):
            self.clear_hover()
            return
        idx = self.rc_idx(r, c)
        if self.board[idx] != EMPTY:
            self.clear_hover()
            return
        self.set_hover(idx)

    def on_leave(self, _e: tk.Event) -> None:
        self.clear_hover()

    def set_hover(self, idx: int) -> None:
        self.clear_hover()
        rect = self.cells_rect[idx]
        self.canvas.itemconfigure(rect, fill="#0b1220")
        self.hover_rect = rect

    def clear_hover(self) -> None:
        if self.hover_rect:
            self.canvas.itemconfigure(self.hover_rect, fill=HOVER)
            self.hover_rect = None

    def on_click(self, e: tk.Event) -> None:
        if terminal(self.board) or next_player(self.board) != self.human:
            return
        c = e.x // self.cell_size
        r = e.y // self.cell_size
        if not (0 <= r < 3 and 0 <= c < 3):
            return
        idx = self.rc_idx(r, c)
        if self.board[idx] != EMPTY:
            return
        self.board = place(self.board, idx, self.human)
        self.update_ui()
        if not terminal(self.board):
            self.root.after(140, self.ai_move)

    def ai_move(self) -> None:
        if terminal(self.board) or next_player(self.board) != self.ai:
            return
        mv = ai_best_move(self.board, ai=self.ai)
        self.board = place(self.board, mv, self.ai)
        self.update_ui()

    def update_turn_badge(self) -> None:
        if terminal(self.board):
            w = winner(self.board)
            if w is None:
                self.badge_turn.configure(text="Draw", bg="#e5e7eb", fg=BG)
            elif w == self.human:
                self.badge_turn.configure(text="You win", bg="#34d399", fg=BG)
            else:
                self.badge_turn.configure(text="AI wins", bg="#f87171", fg=BG)
        else:
            if next_player(self.board) == self.human:
                self.badge_turn.configure(text="Your turn: X", bg="#a7f3d0", fg=BG)
            else:
                self.badge_turn.configure(text="AI thinking…", bg="#fde68a", fg=BG)

    def refresh(self) -> None:
        self.draw_grid()
        self.draw_marks()
        self.highlight_winner()
        self.update_turn_badge()
        self.status.configure(text=self.status_text())

    def status_text(self) -> str:
        if terminal(self.board):
            w = winner(self.board)
            if w is None:
                return "Result: draw."
            if w == self.human:
                return "Nice! You won."
            return "Tough one. AI won."
        return "Click any empty square."

    def update_scores(self) -> None:
        w = winner(self.board)
        if w is None and is_full(self.board):
            self.score_d += 1
        elif w == "X":
            self.score_x += 1
        elif w == "O":
            self.score_o += 1
        self.sx.configure(text=f"X: {self.score_x}")
        self.so.configure(text=f"O: {self.score_o}")
        self.sd.configure(text=f"Draws: {self.score_d}")

    def update_ui(self) -> None:
        self.refresh()
        if terminal(self.board):
            self.update_scores()

    def restart(self) -> None:
        self.board = empty_board()
        self.clear_win_line()
        self.refresh()
        if self.ai == "X" and next_player(self.board) == "X":
            self.root.after(160, self.ai_move)

    def toggle_first(self) -> None:
        if self.human == "X":
            self.human, self.ai = "O", "X"
            self.swap_btn.configure(text="Play First: OFF")
        else:
            self.human, self.ai = "X", "O"
            self.swap_btn.configure(text="Play First: ON")
        self.restart()

def main() -> None:
    root = tk.Tk()
    TTTApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
