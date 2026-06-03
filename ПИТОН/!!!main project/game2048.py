import tkinter as tk
import random
import copy

TILE_COLORS = {
    0: {"bg": "#D6CDB4", "fg": "#3F3F3F"},
    2: {"bg": "#EEE4DA", "fg": "#3F3F3F"},
    4: {"bg": "#ECE0C8", "fg": "#3F3F3F"},
    8: {"bg": "#F2B179", "fg": "#FFFFFF"},
    16: {"bg": "#F59563", "fg": "#FFFFFF"},
    32: {"bg": "#F57C5F", "fg": "#FFFFFF"},
    64: {"bg": "#F65D3B", "fg": "#FFFFFF"},
    128: {"bg": "#EDCE71", "fg": "#FFFFFF"},
    256: {"bg": "#EDCC61", "fg": "#FFFFFF"},
    512: {"bg": "#ECC850", "fg": "#FFFFFF"},
    1024: {"bg": "#EDC53F", "fg": "#FFFFFF"},
    2048: {"bg": "#EEC22E", "fg": "#FFFFFF"},
}
TILE_COLOR_OVER_2048 = {"bg": "#3F3F3F", "fg": "#FFFFFF"}

WIN_BG = "#EFF8FB"
BOARD_BG = "#BBADA0"
CELL_PAD = 12
CELL_SIZE = 90
BOARD_CELLS = 4

FONT_LARGE = ("Monocraft", 26)   
FONT_SMALL = ("Monocraft", 18, "bold") 
FONT_UI = ("Monocraft", 16)
FONT_LABEL = ("Monocraft", 10, "bold")
FONT_OVERLAY = ("Monocraft", 28, "bold")
FONT_OVERLAY_SUB = ("Monocraft", 10)



class Game2048:
    def __init__(self):
        self.board = [[0]*4 for _ in range(4)]
        self.score = 0
        self.best_score = 0
        self.undo_board = [[0]*4 for _ in range(4)]
        self.undo_score = 0

        self.did_moved = False
        self.locked_perm = False
        self.already_won = 0

        self._overlay_state = None
        self._overlay_items = []
        self._restart_yes_btn = None
        self._restart_no_btn  = None

        self._build_ui()
        self._new_game()



    # UI
    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("2048")
        self.root.resizable(False, False)
        self.root.configure(bg=WIN_BG)
        
        # Top bar
        top = tk.Frame(self.root, bg=WIN_BG)
        top.pack(padx=18, pady=(18, 6), fill="x")

        tk.Label(top, text="2048", font=("Monocraft", 40, "bold"), bg=WIN_BG, fg="#776E65").pack(side="left")

        # Score
        score_frame = tk.Canvas(top, bg=WIN_BG)
        score_frame.pack(side="right")

        best_box = tk.Frame(score_frame, bg="#BBADA0", padx=10, pady=4)
        best_box.pack(side="right", padx=(6, 0))
        tk.Label(best_box, text="RECORD", font=FONT_LABEL, bg="#BBADA0", fg="#EEE4DA").pack()
        self.best_lbl = tk.Label(best_box, text="0", font=FONT_UI, bg="#BBADA0", fg="white")
        self.best_lbl.pack()

        score_box = tk.Frame(score_frame, bg="#BBADA0", padx=10, pady=4)
        score_box.pack(side="right")
        tk.Label(score_box, text="SCORE", font=FONT_LABEL, bg="#BBADA0", fg="#EEE4DA").pack()
        self.score_lbl = tk.Label(score_box, text="0", font=FONT_UI, bg="#BBADA0", fg="white")
        self.score_lbl.pack()

        # Buttons
        btn_row = tk.Canvas(self.root, bg=WIN_BG)
        btn_row.pack(padx=18, pady=(0, 8), fill="x")
        
        btn_newgame = tk.Button(btn_row, text="New Game (R)", bg="#8F7A66", fg="white", command=self._btn_restart_click, font=FONT_LABEL, relief="flat", cursor="hand2", padx=10, pady=4)
        btn_newgame.pack(side="left", padx=(0, 6))

        btn_undo = tk.Button(btn_row, text="Undo (Q)", bg="#8F7A66", fg="white", command=self._btn_undo_click, font=FONT_LABEL, relief="flat", cursor="hand2", padx=10, pady=4)
        btn_undo.pack(side="left")

        btn_exit = tk.Button(btn_row, text="Exit (ESC)", bg="#8F7A66", fg="white", command=self._btn_exit_click, font=FONT_LABEL, relief="flat", cursor="hand2", padx=10, pady=4)
        btn_exit.pack(side="right")
        
        # Board
        board_px = BOARD_CELLS * CELL_SIZE + (BOARD_CELLS + 1) * CELL_PAD
        self.board_px = board_px
        self.canvas = tk.Canvas(self.root, width=board_px, height=board_px, bg=BOARD_BG, highlightthickness=0)
        self.canvas.pack(padx=18, pady=(0, 18))

        # Make cells
        px = 6
        self.cell_rect = [[None]*4 for _ in range(4)]
        self.cell_text = [[None]*4 for _ in range(4)]
        for r in range(4):
            for c in range(4):
                x1 = CELL_PAD + c * (CELL_SIZE + CELL_PAD)
                y1 = CELL_PAD + r * (CELL_SIZE + CELL_PAD)
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=TILE_COLORS[0]["bg"], outline="")
                text = self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text="", font=FONT_LARGE, fill=TILE_COLORS[0]["fg"])
                self.cell_rect[r][c] = rect
                self.cell_text[r][c] = text
                
                corner_things = [(x1, y1), (x2 - px, y1), (x1, y2 - px), (x2 - px, y2 - px)]
                for cx, cy in corner_things:
                    self.canvas.create_rectangle(cx, cy, cx + px, cy + px, fill=BOARD_BG, outline="")
            
        b_right  = board_px - px
        b_bottom = board_px - px

        self.canvas.create_rectangle(0, 0, px, px, fill=WIN_BG, outline="")
        self.canvas.create_rectangle(b_right, 0, board_px, px, fill=WIN_BG, outline="")
        self.canvas.create_rectangle(0, b_bottom, px, board_px, fill=WIN_BG, outline="")
        self.canvas.create_rectangle(b_right, b_bottom, board_px, board_px, fill=WIN_BG, outline="")

        #binds
        self.root.bind("<KeyRelease>", self._on_key_up)
        self.root.focus_set()



    # INITIALIZE
    def _new_game(self):
        self.board = [[0]*4 for _ in range(4)]
        self.score = 0
        self.undo_board = [[0]*4 for _ in range(4)]
        self.undo_score = 0
        self.did_moved = False
        self.locked_perm = False
        self.already_won = 0
        self._hide_overlay()
        self._summon()
        self._summon()
        self._save()
        self._refresh()

    # Summoner
    def _summon(self):
        empty = [(r, c) for r in range(4) for c in range(4) if self.board[r][c] == 0]
        if not empty:
            return
        r, c = random.choice(empty)
        self.board[r][c] = 4 if random.random() > 0.9 else 2

    # Saves
    def _save(self):
        self.undo_board = copy.deepcopy(self.board)
        self.undo_score = self.score

    def _restore(self):
        self.board = copy.deepcopy(self.undo_board)
        self.score = self.undo_score

    # Record score
    def _best_score_counter(self):
        if self.score > self.best_score:
            self.best_score = self.score

    # Check Z
    def _check_pobeda(self) -> bool:
        for row in self.board:
            if 2048 in row:
                return True
        return False

    # CheckProigral
    def _check_proigral(self) -> bool:
        if self._check_pobeda():
            return False
        for row in self.board:
            if 0 in row:
                return False
        for r in range(4):
            for c in range(4):
                v = self.board[r][c]
                if r < 3 and self.board[r+1][c] == v:
                    return False
                if c < 3 and self.board[r][c+1] == v:
                    return False
        return True

    # Refresh
    def _refresh(self):
        self.root.update_idletasks()
        
        for r in range(4):
            for c in range(4):
                self._set_design(r, c)

        self.score_lbl.config(text=str(self.score))
        self._best_score_counter()
        self.best_lbl.config(text=str(self.best_score))

        defeated = self._check_proigral()
        won = self._check_pobeda()

        if won:
            if not self.already_won >= 4:
                self.already_won += 1
            if self.already_won < 3:
                self._show_overlay('win')
            else:
                self._hide_overlay()
        elif defeated:
            self.locked_perm = True
            self._show_overlay('lose')

    # Set design
    def _set_design(self, r: int, c: int):
        val    = self.board[r][c]
        colors = TILE_COLORS.get(val, TILE_COLOR_OVER_2048)
        font   = FONT_LARGE if val <= 9999 else FONT_SMALL
        text   = str(val) if val != 0 else ""
        self.canvas.itemconfig(self.cell_rect[r][c], fill=colors["bg"])
        self.canvas.itemconfig(self.cell_text[r][c], text=text, fill=colors["fg"], font=font)



    # Overlays
    def _show_overlay(self, kind: str):
        if self._overlay_state == kind:
            return
        self._hide_overlay()
        self._overlay_state = kind

        bpx = self.board_px
        cx, cy = bpx // 2, bpx // 2

        bg = self.canvas.create_rectangle(0, 0, bpx, bpx,
                                          fill="#EFF8FB", outline="")
        self._overlay_items.append(bg)

        if kind == 'win':
            msg  = "You win!"
            sub  = "Keep going with arrow keys  |  Q to undo"
            mfg  = "#F9F6F2"
        elif kind == 'lose':
            msg  = "Game over!"
            sub  = "New Game to start over  |  Q to undo"
            mfg  = "#F9F6F2"
        elif kind == 'restart':
            msg  = "Restart?"
            sub  = ""
            mfg  = "#776E65"
        else:
            return

        self._overlay_items.append(
            self.canvas.create_text(cx, cy - 30, text=msg, font=FONT_OVERLAY, fill=mfg))
        if sub:
            self._overlay_items.append(
                self.canvas.create_text(cx, cy + 18, text=sub, font=FONT_OVERLAY_SUB, fill="#776E65"))

        if kind == 'restart':
            self._restart_yes_btn = tk.Button(
                self.root, text="Yes",
                font=FONT_LABEL, bg="#8F7A66", fg="white",
                relief="flat", padx=14, pady=6,
                activebackground="#9F8B77",
                command=self._confirm_restart)
            self._restart_no_btn = tk.Button(
                self.root, text="No",
                font=FONT_LABEL, bg="#BBADA0", fg="white",
                relief="flat", padx=14, pady=6,
                activebackground="#CCC0B3",
                command=self._cancel_restart)
            self._overlay_items.append(
                self.canvas.create_window(cx - 55, cy + 62,
                                          window=self._restart_yes_btn))
            self._overlay_items.append(
                self.canvas.create_window(cx + 55, cy + 62,
                                          window=self._restart_no_btn))

    def _hide_overlay(self):
        for item in self._overlay_items:
            self.canvas.delete(item)
        self._overlay_items.clear()
        self._overlay_state = None
        for attr in ("_restart_yes_btn", "_restart_no_btn"):
            btn = getattr(self, attr, None)
            if btn is not None:
                btn.destroy()
                setattr(self, attr, None)



    # Button controllers
    def _btn_restart_click(self):
        self._hide_overlay()
        self._show_overlay('restart')

    def _confirm_restart(self):
        self._hide_overlay()
        self._new_game()

    def _cancel_restart(self):
        self._hide_overlay()
        self._refresh()

    def _btn_undo_click(self):
        self._restore()
        self.locked_perm = False
        self.already_won = 0
        self._hide_overlay()
        self._refresh()

    def _btn_exit_click(self):
        self.board = [[0]*4 for _ in range(4)]
        self.score = 0
        self.undo_board = [[0]*4 for _ in range(4)]
        self.undo_score = 0
        self.root.destroy()

    # Key controller
    def _on_key_up(self, event):
        if event.keysym in ("q", "Q"):
            self._btn_undo_click()
            return
        if event.keysym in ("r", "R"):
            self._btn_restart_click()
            return
        
        if event.keysym == "Return":
            if self._overlay_state == 'restart':
                self._confirm_restart()
            if self._overlay_state in ('win', 'lose'):
                self._hide_overlay()
                self._refresh()
            return
        
        
        if event.keysym == "Escape":
            if self._overlay_state == 'restart':
                self._cancel_restart()
                self._refresh()
                return
            self._btn_exit_click()
            return

        if event.keysym not in ("Left", "Right", "Up", "Down", "a", "A", "w", "W", "s", "S", "d", "D"):
            return
        if self.locked_perm:
            return

        self._hide_overlay()
        self._save()

        if event.keysym in ("Left", "a", "A"): self._gravity_left()
        elif event.keysym in ("Right", "d", "D"): self._gravity_right()
        elif event.keysym in ("Up", "w", "W"): self._gravity_up()
        elif event.keysym in ("Down", "s", "S"): self._gravity_down()

        if not self.did_moved:
            self._restore()

        self._refresh()



    # GravityLeft
    def _gravity_left(self):
        self.did_moved = False
        can_summon = False

        for row in range(4):

            for col in range(4):
                if self.board[row][col] == 0:
                    for j in range(col + 1, 4):
                        if self.board[row][j] != 0:
                            self.board[row][col] = self.board[row][j]
                            self.board[row][j]   = 0
                            can_summon = True
                            self.did_moved = True
                            break

            for col in range(3):
                if (self.board[row][col] != 0 and self.board[row][col] == self.board[row][col + 1]):
                    self.board[row][col] *= 2
                    self.score += self.board[row][col]
                    self.board[row][col + 1] = 0
                    can_summon = True
                    self.did_moved = True
                    for j in range(col + 1, 3):
                        self.board[row][j] = self.board[row][j + 1]
                    self.board[row][3] = 0

        if can_summon:
            self._summon()

    # GravityRight
    def _gravity_right(self):
        self.did_moved = False
        can_summon = False

        for row in range(4):
            for col in range(3, -1, -1):
                if self.board[row][col] == 0:
                    for j in range(col - 1, -1, -1):
                        if self.board[row][j] != 0:
                            self.board[row][col] = self.board[row][j]
                            self.board[row][j]   = 0
                            can_summon = True
                            self.did_moved = True
                            break
            for col in range(3, 0, -1):
                if (self.board[row][col] != 0 and self.board[row][col] == self.board[row][col - 1]):
                    self.board[row][col] *= 2
                    self.score += self.board[row][col]
                    self.board[row][col - 1] = 0
                    can_summon = True
                    self.did_moved = True
                    for j in range(col - 1, 0, -1):
                        self.board[row][j] = self.board[row][j - 1]
                    self.board[row][0] = 0

        if can_summon:
            self._summon()

    # GravityUp
    def _gravity_up(self):
        self.did_moved = False
        can_summon = False

        for col in range(4):
            for row in range(4):
                if self.board[row][col] == 0:
                    for j in range(row + 1, 4):
                        if self.board[j][col] != 0:
                            self.board[row][col] = self.board[j][col]
                            self.board[j][col]   = 0
                            can_summon = True
                            self.did_moved = True
                            break
            for row in range(3):
                if (self.board[row][col] != 0 and self.board[row][col] == self.board[row + 1][col]):
                    self.board[row][col] *= 2
                    self.score += self.board[row][col]
                    self.board[row + 1][col] = 0
                    can_summon = True
                    self.did_moved = True
                    for j in range(row + 1, 3):
                        self.board[j][col] = self.board[j + 1][col]
                    self.board[3][col] = 0

        if can_summon:
            self._summon()

    # GravityDown
    def _gravity_down(self):
        self.did_moved = False
        can_summon = False

        for col in range(4):
            for row in range(3, -1, -1):
                if self.board[row][col] == 0:
                    for j in range(row - 1, -1, -1):
                        if self.board[j][col] != 0:
                            self.board[row][col] = self.board[j][col]
                            self.board[j][col]   = 0
                            can_summon = True
                            self.did_moved = True
                            break
            for row in range(3, 0, -1):
                if (self.board[row][col] != 0 and self.board[row][col] == self.board[row - 1][col]):
                    self.board[row][col] *= 2
                    self.score += self.board[row][col]
                    self.board[row - 1][col] = 0
                    can_summon = True
                    self.did_moved = True
                    for j in range(row - 1, 0, -1):
                        self.board[j][col] = self.board[j - 1][col]
                    self.board[0][col] = 0

        if can_summon:
            self._summon()



# something
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = Game2048()
    game.run()