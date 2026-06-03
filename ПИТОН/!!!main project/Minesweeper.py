import tkinter as tk
import tkinter.simpledialog as simpledialog
import random
import json
import os

# ─────────────────────────────────────────────────────────────────
#  Colour palette — mirrors SetDesign() in VBA exactly
# ─────────────────────────────────────────────────────────────────
TILE_COLORS = {
    0:    ("#d6cdc4", "#3f3f3f"),   # empty
    2:    ("#eee4da", "#3f3f3f"),
    4:    ("#ece0c8", "#3f3f3f"),
    8:    ("#f2b179", "#ffffff"),
    16:   ("#f59563", "#ffffff"),
    32:   ("#f57c5f", "#ffffff"),
    64:   ("#f65d3b", "#ffffff"),
    128:  ("#edce71", "#ffffff"),
    256:  ("#edcc61", "#ffffff"),
    512:  ("#ecc850", "#ffffff"),
    1024: ("#edc53f", "#ffffff"),
    2048: ("#eec22e", "#ffffff"),
}
TILE_COLOR_BEYOND = ("#3f3f3f", "#ffffff")

BOARD_BG   = "#bbada0"
ROOT_BG    = "#faf8fb"          # matches VBA &HEFF8FB converted
SCORE_BG   = "#bbada0"
SCORE_FG   = "#ffffff"
HEADER_FG  = "#776e65"

# Save file — replaces wsDATA sheet
SAVE_FILE = "2048_save.json"

# ─────────────────────────────────────────────────────────────────
class Game2048:
    """
    Full faithful port of the VBA 2048 implementation.

    State mapping:
        self.board[r][c]  ←→  wsMAIN.Cells(r+2, c+2)   (0-based, 4×4)
        self.undo_board   ←→  wsDATA.Range("B8:E11")
        self.score        ←→  score.Caption
        self.undo_score   ←→  wsDATA.Range("G8")
        self.best_score   ←→  wsDATA.Range("J2")
        self.already_won  ←→  AlreadyWon
        self.locked_perm  ←→  LockedPerm
        self.did_moved    ←→  DidMoved
        self.filter_prop  ←→  FILTERproperties
        self.spawn_prop   ←→  SPAWNproperties
    """

    # ── geometry ──────────────────────────────────────────────────
    CELL   = 96          # pixel size of one tile
    GAP    = 12          # gap between tiles
    MARGIN = 16          # board outer margin
    TOP_H  = 120         # header height (scores + title)

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("2048")
        self.root.resizable(False, False)
        self.root.configure(bg=ROOT_BG)

        # ── state ─────────────────────────────────────────────────
        self.board       = [[0]*4 for _ in range(4)]
        self.undo_board  = [[0]*4 for _ in range(4)]
        self.score       = 0
        self.undo_score  = 0
        self.best_score  = 0
        self.already_won = 0        # AlreadyWon
        self.locked_perm = False    # LockedPerm
        self.did_moved   = False    # DidMoved
        self.filter_prop = 2        # FILTERproperties
        self.spawn_prop  = 11       # SPAWNproperties (2^11=2048)

        # overlay state
        self._overlay_state = None  # None | "win" | "lose" | "restart"

        self._load_persistent()
        self._build_ui()
        self._initialize()
        self.root.bind("<KeyRelease>", self._on_key_release)
        self.root.mainloop()

    # ══════════════════════════════════════════════════════════════
    #  PERSISTENT DATA  (replaces wsDATA sheet)
    # ══════════════════════════════════════════════════════════════
    def _load_persistent(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    d = json.load(f)
                self.best_score = d.get("best_score", 0)
                # saved board / score are loaded at game start by CanSummonStartCheck
                self._saved_board      = d.get("board", [[0]*4 for _ in range(4)])
                self._saved_score      = d.get("score", 0)
                self._saved_undo_board = d.get("undo_board", [[0]*4 for _ in range(4)])
                self._saved_undo_score = d.get("undo_score", 0)
            except Exception:
                self._reset_persistent_cache()
        else:
            self._reset_persistent_cache()

    def _reset_persistent_cache(self):
        self._saved_board      = [[0]*4 for _ in range(4)]
        self._saved_score      = 0
        self._saved_undo_board = [[0]*4 for _ in range(4)]
        self._saved_undo_score = 0

    def _write_persistent(self):
        d = {
            "best_score":  self.best_score,
            "board":       self.board,
            "score":       self.score,
            "undo_board":  self.undo_board,
            "undo_score":  self.undo_score,
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(d, f)
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════
    #  UI BUILD
    # ══════════════════════════════════════════════════════════════
    def _build_ui(self):
        board_px = 4 * self.CELL + 5 * self.GAP          # 4*96 + 5*12 = 444
        side_w   = 200
        win_w    = board_px + 2 * self.MARGIN + side_w + self.MARGIN
        win_h    = self.TOP_H + board_px + 2 * self.MARGIN + 40
        self.root.geometry(f"{win_w}x{win_h}")

        # ── header ────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=ROOT_BG)
        hdr.pack(fill="x", padx=self.MARGIN, pady=(self.MARGIN, 0))

        title_lbl = tk.Label(hdr, text="2048", font=("Arial", 40, "bold"),
                             bg=ROOT_BG, fg=HEADER_FG)
        title_lbl.pack(side="left")

        score_frame = tk.Frame(hdr, bg=ROOT_BG)
        score_frame.pack(side="right")

        self.score_var      = tk.StringVar(value="0")
        self.bestscore_var  = tk.StringVar(value="0")

        for lbl_text, var, name in [
            ("SCORE", self.score_var, "score"),
            ("BEST",  self.bestscore_var, "best"),
        ]:
            box = tk.Frame(score_frame, bg=SCORE_BG, padx=10, pady=4)
            box.pack(side="left", padx=4)
            tk.Label(box, text=lbl_text, font=("Arial", 9, "bold"),
                     bg=SCORE_BG, fg=SCORE_FG).pack()
            tk.Label(box, textvariable=var, font=("Arial", 18, "bold"),
                     bg=SCORE_BG, fg=SCORE_FG).pack()

        # ── button row ────────────────────────────────────────────
        btn_row = tk.Frame(self.root, bg=ROOT_BG)
        btn_row.pack(fill="x", padx=self.MARGIN, pady=6)

        btn_cfg = dict(font=("Arial", 11, "bold"), relief="flat",
                       cursor="hand2", padx=10, pady=4)

        tk.Button(btn_row, text="Restart", bg="#8f7a66", fg="#f9f6f2",
                  command=self._btn_restart, **btn_cfg).pack(side="left", padx=2)
        tk.Button(btn_row, text="Undo (Ctrl)", bg="#8f7a66", fg="#f9f6f2",
                  command=self._btn_undo, **btn_cfg).pack(side="left", padx=2)
        tk.Button(btn_row, text="Quit", bg="#8f7a66", fg="#f9f6f2",
                  command=self._btn_exit, **btn_cfg).pack(side="left", padx=2)
        tk.Button(btn_row, text="Clear Best", bg="#a09090", fg="#f9f6f2",
                  command=self._best_score_clear, **btn_cfg).pack(side="right", padx=2)

        # ── main area: board + sidebar ─────────────────────────────
        main_frame = tk.Frame(self.root, bg=ROOT_BG)
        main_frame.pack(fill="both", expand=True,
                        padx=self.MARGIN, pady=(0, self.MARGIN))

        # board canvas
        self.canvas = tk.Canvas(main_frame,
                                width=board_px,
                                height=board_px,
                                bg=BOARD_BG, highlightthickness=0)
        self.canvas.pack(side="left")

        # sidebar (special/debug controls — matches VBA's SPECIAL* buttons)
        sidebar = tk.Frame(main_frame, bg=ROOT_BG, padx=8)
        sidebar.pack(side="left", fill="y", pady=0)

        tk.Label(sidebar, text="Dev tools", font=("Arial", 9, "bold"),
                 bg=ROOT_BG, fg=HEADER_FG).pack(pady=(0, 4))

        self.filter_var = tk.StringVar(value=f"(filter: {self.filter_prop})")
        self.object_var = tk.StringVar(
            value=f"pow={self.spawn_prop} ({2**self.spawn_prop})")

        dev_cfg = dict(font=("Arial", 9), relief="flat",
                       bg="#c8bdb2", fg="#3f3f3f", cursor="hand2",
                       padx=6, pady=3, anchor="w")

        tk.Button(sidebar, text="Force restart",
                  command=self._special_forced_restart, **dev_cfg).pack(fill="x", pady=1)
        tk.Button(sidebar, text="Unlock",
                  command=self._special_unlock, **dev_cfg).pack(fill="x", pady=1)
        tk.Button(sidebar, text="Summon tile",
                  command=self._special_summon, **dev_cfg).pack(fill="x", pady=1)

        # Filter button — left-click applies, right-click sets threshold
        filter_btn = tk.Button(sidebar, textvariable=self.filter_var,
                               command=self._special_filter_left, **dev_cfg)
        filter_btn.pack(fill="x", pady=1)
        filter_btn.bind("<Button-3>", lambda e: self._special_filter_right())

        # Del1 / DelAll
        tk.Button(sidebar, text="Delete cell",
                  command=self._special_del1, **dev_cfg).pack(fill="x", pady=1)
        tk.Button(sidebar, text="Delete all",
                  command=self._special_del_all, **dev_cfg).pack(fill="x", pady=1)

        # Set / Add1 / AddAll — left sets value, right sets spawn_prop
        set_btn = tk.Button(sidebar, text="Set cell", **dev_cfg,
                            command=self._special_set_left)
        set_btn.pack(fill="x", pady=1)
        set_btn.bind("<Button-3>", lambda e: self._special_set_right())

        add1_btn = tk.Button(sidebar, text="Add 1 tile", **dev_cfg,
                             command=self._special_add1_left)
        add1_btn.pack(fill="x", pady=1)
        add1_btn.bind("<Button-3>", lambda e: self._special_add1_right())

        addall_btn = tk.Button(sidebar, text="Fill all", **dev_cfg,
                               command=self._special_add_all_left)
        addall_btn.pack(fill="x", pady=1)
        addall_btn.bind("<Button-3>", lambda e: self._special_add_all_right())

        tk.Label(sidebar, textvariable=self.object_var, font=("Arial", 8),
                 bg=ROOT_BG, fg=HEADER_FG).pack(pady=(2, 0))

        # ── overlay canvas (win / lose / restart dialogs) ─────────
        self.overlay = tk.Canvas(self.canvas, width=board_px, height=board_px,
                                 bg="", highlightthickness=0)
        self.overlay.place(x=0, y=0)
        self._draw_tiles()   # initial blank draw

    # ══════════════════════════════════════════════════════════════
    #  INITIALISE  (mirrors UserForm_Initialize + CanSummonStartCheck)
    # ══════════════════════════════════════════════════════════════
    def _initialize(self):
        self.already_won = 0
        self.did_moved   = False
        self.locked_perm = False
        self.filter_prop = 2
        self.spawn_prop  = 11

        self.best_score = self._saved_score and self.best_score or self.best_score

        # Restore saved game if board has any tile (CanSummonStartCheck → False)
        if self._can_summon_start_check():
            # Board is all empty → fresh start
            self.board = [[0]*4 for _ in range(4)]
            self.score = 0
            self._summon()
            self._summon()
            self._save()
        else:
            # Resume from saved state
            self.board      = [row[:] for row in self._saved_board]
            self.score      = self._saved_score
            self.undo_board = [row[:] for row in self._saved_undo_board]
            self.undo_score = self._saved_undo_score

        self._refresh()

    def _can_summon_start_check(self) -> bool:
        """Returns True when the saved board is completely empty."""
        for row in self._saved_board:
            for v in row:
                if v != 0:
                    return False
        return True

    # ══════════════════════════════════════════════════════════════
    #  SAVE / RESTORE  (wsDATA operations)
    # ══════════════════════════════════════════════════════════════
    def _save(self):
        """Save current board as undo snapshot + persist to file."""
        self.undo_board = [row[:] for row in self.board]
        self.undo_score = self.score
        self._write_persistent()

    def _restore(self):
        """Restore from undo snapshot (called when nothing moved)."""
        self.board = [row[:] for row in self.undo_board]
        self.score = self.undo_score
        self._refresh()

    # ══════════════════════════════════════════════════════════════
    #  REFRESH  (mirrors Sub Refresh)
    # ══════════════════════════════════════════════════════════════
    def _refresh(self):
        self._draw_tiles()
        self._update_score_labels()

        lost = self._check_lost()
        won  = self._check_won()

        if won:
            if self.already_won < 4:
                self.already_won += 1
        self._best_score_counter()

    # ══════════════════════════════════════════════════════════════
    #  DRAWING
    # ══════════════════════════════════════════════════════════════
    def _draw_tiles(self):
        self.canvas.delete("tile")
        for r in range(4):
            for c in range(4):
                x0 = self.GAP + c * (self.CELL + self.GAP)
                y0 = self.GAP + r * (self.CELL + self.GAP)
                x1 = x0 + self.CELL
                y1 = y0 + self.CELL
                val = self.board[r][c]

                if val in TILE_COLORS:
                    bg, fg = TILE_COLORS[val]
                elif val > 2048:
                    bg, fg = TILE_COLOR_BEYOND
                else:
                    bg, fg = TILE_COLORS[0]

                self.canvas.create_rectangle(x0, y0, x1, y1,
                                             fill=bg, outline="", tags="tile")
                if val != 0:
                    font_size = 28 if val <= 9999 else 20
                    self.canvas.create_text(
                        (x0 + x1) // 2, (y0 + y1) // 2,
                        text=str(val),
                        font=("Arial", font_size, "bold"),
                        fill=fg, tags="tile")

    def _update_score_labels(self):
        self.score_var.set(str(self.score))
        self.bestscore_var.set(str(self.best_score))
        self.filter_var.set(f"(filter: {self.filter_prop})")
        self.object_var.set(f"pow={self.spawn_prop} ({2**self.spawn_prop})")

    # ── Overlay helpers (GroupWin/Lose/Restart show/hide) ─────────
    def _show_overlay(self, state: str):
        """state ∈ {'win', 'lose', 'restart'}"""
        self._overlay_state = state
        self.overlay.delete("all")
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])

        if state == "restart":
            # semi-transparent dark backdrop
            self.overlay.create_rectangle(0, 0, w, h,
                                          fill="#000000", stipple="gray50",
                                          tags="all")
            self.overlay.create_text(w//2, h//2 - 40,
                                     text="Restart?",
                                     font=("Arial", 28, "bold"),
                                     fill="#ffffff", tags="all")
            # YES button
            self.overlay.create_rectangle(w//2 - 110, h//2,
                                          w//2 - 10,  h//2 + 44,
                                          fill="#8f7a66", outline="", tags="all")
            self.overlay.create_text(w//2 - 60, h//2 + 22,
                                     text="Yes", font=("Arial", 16, "bold"),
                                     fill="#ffffff", tags="all")
            # NO button
            self.overlay.create_rectangle(w//2 + 10, h//2,
                                          w//2 + 110, h//2 + 44,
                                          fill="#8f7a66", outline="", tags="all")
            self.overlay.create_text(w//2 + 60, h//2 + 22,
                                     text="No", font=("Arial", 16, "bold"),
                                     fill="#ffffff", tags="all")
            self.overlay.bind("<Button-1>", self._overlay_click)

        elif state == "win":
            self.overlay.create_rectangle(0, 0, w, h,
                                          fill="#edcc61", stipple="gray50",
                                          tags="all")
            self.overlay.create_text(w//2, h//2,
                                     text="You win! 🎉",
                                     font=("Arial", 32, "bold"),
                                     fill="#ffffff", tags="all")
            self.overlay.create_text(w//2, h//2 + 48,
                                     text="(keep playing)",
                                     font=("Arial", 13),
                                     fill="#ffffff", tags="all")

        elif state == "lose":
            self.overlay.create_rectangle(0, 0, w, h,
                                          fill="#3f3f3f", stipple="gray50",
                                          tags="all")
            self.overlay.create_text(w//2, h//2,
                                     text="Game Over",
                                     font=("Arial", 32, "bold"),
                                     fill="#ffffff", tags="all")

    def _hide_overlay(self):
        self._overlay_state = None
        self.overlay.delete("all")
        self.overlay.unbind("<Button-1>")

    def _overlay_click(self, event):
        if self._overlay_state != "restart":
            return
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])
        # Yes zone
        if (w//2 - 110 <= event.x <= w//2 - 10 and
                h//2 <= event.y <= h//2 + 44):
            self._restart_yes()
        # No zone
        elif (w//2 + 10 <= event.x <= w//2 + 110 and
              h//2 <= event.y <= h//2 + 44):
            self._restart_no()

    # ══════════════════════════════════════════════════════════════
    #  WIN / LOSE CHECKS  (CheckPobeda / CheckProigral)
    # ══════════════════════════════════════════════════════════════
    def _check_won(self) -> bool:
        for r in range(4):
            for c in range(4):
                if self.board[r][c] == 2048:
                    if self.already_won < 3:
                        self._show_overlay("win")
                    return True
        return False

    def _check_lost(self) -> bool:
        if self._check_won():
            return False

        is_full    = all(self.board[r][c] != 0
                         for r in range(4) for c in range(4))
        cant_merge = True
        for r in range(4):
            for c in range(4):
                v = self.board[r][c]
                if v == 0:
                    cant_merge = False
                    continue
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 4 and 0 <= nc < 4:
                        if self.board[nr][nc] == v:
                            cant_merge = False

        if is_full and cant_merge:
            self._show_overlay("lose")
            self.locked_perm = True
            return True
        return False

    # ══════════════════════════════════════════════════════════════
    #  BEST SCORE  (BestScoreCounter)
    # ══════════════════════════════════════════════════════════════
    def _best_score_counter(self):
        if self.score > self.best_score:
            self.best_score = self.score
        self._update_score_labels()

    # ══════════════════════════════════════════════════════════════
    #  SUMMON  (Sub Summon — 90 % chance 2, 10 % chance 4)
    # ══════════════════════════════════════════════════════════════
    def _summon(self):
        empty = [(r, c) for r in range(4) for c in range(4)
                 if self.board[r][c] == 0]
        if not empty:
            return
        r, c = random.choice(empty)
        self.board[r][c] = 2 if random.random() <= 0.9 else 4

    # ══════════════════════════════════════════════════════════════
    #  KEYBOARD  (UserForm_KeyUp)
    # ══════════════════════════════════════════════════════════════
    def _on_key_release(self, event):
        # Ctrl = keycode 17
        if event.keycode == 17 or event.keysym == "Control_L" or event.keysym == "Control_R":
            self._btn_undo()
            self._hide_overlay()
            self._refresh()
            return

        arrow_map = {
            "Left":  self._gravity_left,
            "Right": self._gravity_right,
            "Up":    self._gravity_up,
            "Down":  self._gravity_down,
        }
        if event.keysym not in arrow_map:
            return

        if self.locked_perm:
            return

        self._hide_overlay()
        self._save()
        arrow_map[event.keysym]()
        if not self.did_moved:
            self._restore()
        self._refresh()

    # ══════════════════════════════════════════════════════════════
    #  GRAVITY MOVES  (exact VBA logic, 0-based 4×4 indices)
    # ══════════════════════════════════════════════════════════════
    def _gravity_left(self):
        self.did_moved = False
        can_summon = False

        for row in range(4):
            # slide
            for col in range(4):
                if self.board[row][col] == 0:
                    for j in range(col + 1, 4):
                        if self.board[row][j] != 0:
                            self.board[row][col] = self.board[row][j]
                            self.board[row][j] = 0
                            can_summon = True
                            self.did_moved = True
                            break
            # merge
            for col in range(3):
                if (self.board[row][col] != 0 and
                        self.board[row][col] == self.board[row][col + 1]):
                    self.board[row][col] *= 2
                    self.score += self.board[row][col]
                    self.board[row][col + 1] = 0
                    self.did_moved = True
                    can_summon = True
                    for j in range(col + 1, 3):
                        self.board[row][j] = self.board[row][j + 1]
                    self.board[row][3] = 0

        if can_summon:
            self._summon()

    def _gravity_right(self):
        self.did_moved = False
        can_summon = False

        for row in range(4):
            # slide
            for col in range(3, -1, -1):
                if self.board[row][col] == 0:
                    for j in range(col - 1, -1, -1):
                        if self.board[row][j] != 0:
                            self.board[row][col] = self.board[row][j]
                            self.board[row][j] = 0
                            can_summon = True
                            self.did_moved = True
                            break
            # merge
            for col in range(3, 0, -1):
                if (self.board[row][col] != 0 and
                        self.board[row][col] == self.board[row][col - 1]):
                    self.board[row][col] *= 2
                    self.score += self.board[row][col]
                    self.board[row][col - 1] = 0
                    self.did_moved = True
                    can_summon = True
                    for j in range(col - 1, 0, -1):
                        self.board[row][j] = self.board[row][j - 1]
                    self.board[row][0] = 0

        if can_summon:
            self._summon()

    def _gravity_up(self):
        self.did_moved = False
        can_summon = False

        for col in range(4):
            # slide
            for row in range(4):
                if self.board[row][col] == 0:
                    for j in range(row + 1, 4):
                        if self.board[j][col] != 0:
                            self.board[row][col] = self.board[j][col]
                            self.board[j][col] = 0
                            can_summon = True
                            self.did_moved = True
                            break
            # merge
            for row in range(3):
                if (self.board[row][col] != 0 and
                        self.board[row][col] == self.board[row + 1][col]):
                    self.board[row][col] *= 2
                    self.score += self.board[row][col]
                    self.board[row + 1][col] = 0
                    self.did_moved = True
                    can_summon = True
                    for j in range(row + 1, 3):
                        self.board[j][col] = self.board[j + 1][col]
                    self.board[3][col] = 0

        if can_summon:
            self._summon()

    def _gravity_down(self):
        self.did_moved = False
        can_summon = False

        for col in range(4):
            # slide
            for row in range(3, -1, -1):
                if self.board[row][col] == 0:
                    for j in range(row - 1, -1, -1):
                        if self.board[j][col] != 0:
                            self.board[row][col] = self.board[j][col]
                            self.board[j][col] = 0
                            can_summon = True
                            self.did_moved = True
                            break
            # merge
            for row in range(3, 0, -1):
                if (self.board[row][col] != 0 and
                        self.board[row][col] == self.board[row - 1][col]):
                    self.board[row][col] *= 2
                    self.score += self.board[row][col]
                    self.board[row - 1][col] = 0
                    self.did_moved = True
                    can_summon = True
                    for j in range(row - 1, 0, -1):
                        self.board[j][col] = self.board[j - 1][col]
                    self.board[0][col] = 0

        if can_summon:
            self._summon()

    # ══════════════════════════════════════════════════════════════
    #  BUTTON HANDLERS
    # ══════════════════════════════════════════════════════════════
    def _btn_exit(self):
        """btn_exit_Click — saves then clears persistent state."""
        self._write_persistent()
        self.best_score = 0          # AlreadyWon = 0
        # Clear board & score in file (VBA clears wsDATA after saving)
        self.board  = [[0]*4 for _ in range(4)]
        self.score  = 0
        self._write_persistent()
        self.root.destroy()

    def _btn_undo(self):
        """btn_undo_Click"""
        self.board = [row[:] for row in self.undo_board]
        self.score = self.undo_score
        self._hide_overlay()
        self.locked_perm = False
        self.already_won = 0
        self._refresh()

    def _btn_restart(self):
        """btn_restart_Click — shows restart dialog."""
        self._show_overlay("restart")
        # hide win/lose implicitly (overlay replaced)

    def _best_score_clear(self):
        """bestscoreCLEAR_Click"""
        self.best_score = 0
        self.bestscore_var.set("0")
        self._write_persistent()

    def _restart_yes(self):
        """RestartY_Click"""
        self.board      = [[0]*4 for _ in range(4)]
        self.undo_board = [[0]*4 for _ in range(4)]
        self._hide_overlay()
        self._form_initialize()

    def _restart_no(self):
        """RestartN_Click"""
        self._hide_overlay()
        self._refresh()

    def _form_initialize(self):
        """Mirrors UserForm_Initialize for restart path."""
        self.already_won = 0
        self.did_moved   = False
        self.locked_perm = False
        self.score       = 0
        self._summon()
        self._summon()
        self._save()
        self._refresh()

    # ══════════════════════════════════════════════════════════════
    #  SPECIAL / DEBUG BUTTONS
    # ══════════════════════════════════════════════════════════════
    def _special_forced_restart(self):
        self._restart_yes()

    def _special_unlock(self):
        self.locked_perm = False
        self._hide_overlay()

    def _special_summon(self):
        self._summon()
        self._refresh()

    # Filter ──────────────────────────────────────────────────────
    def _special_filter_left(self):
        """Left-click: remove all tiles ≤ filter_prop, summon one."""
        for r in range(4):
            for c in range(4):
                v = self.board[r][c]
                if v != 0 and (v == 2 or v <= self.filter_prop):
                    self.board[r][c] = 0
        self._summon()
        self._special_unlock()
        self._refresh()

    def _special_filter_right(self):
        """Right-click: change filter threshold."""
        val = simpledialog.askstring(
            "Filter",
            f"Current limit: {self.filter_prop}\nChange to...")
        if val and val.isdigit():
            self.filter_prop = max(2, int(val))
        self._update_score_labels()

    # Del1 / DelAll ───────────────────────────────────────────────
    def _special_del1(self):
        addr = simpledialog.askstring(
            "Delete cell",
            "Cell address (e.g. B2..E5)\n\nB2 C2 D2 E2\nB3 C3 D3 E3\n"
            "B4 C4 D4 E4\nB5 C5 D5 E5")
        if addr:
            pos = self._addr_to_rc(addr.strip().upper())
            if pos:
                r, c = pos
                self.board[r][c] = 0
        self._special_unlock()
        self._refresh()

    def _special_del_all(self):
        self.board = [[0]*4 for _ in range(4)]
        self._summon()
        self._special_unlock()
        self._refresh()

    # Set ─────────────────────────────────────────────────────────
    def _special_set_left(self):
        addr = simpledialog.askstring(
            "Set cell",
            "Cell address (e.g. B2..E5)\n\nB2 C2 D2 E2\nB3 C3 D3 E3\n"
            "B4 C4 D4 E4\nB5 C5 D5 E5")
        if addr:
            pos = self._addr_to_rc(addr.strip().upper())
            if pos:
                r, c = pos
                self.board[r][c] = 2 ** self.spawn_prop
        self._special_unlock()
        self._refresh()

    def _special_set_right(self):
        val = simpledialog.askstring(
            "Spawn power",
            f"Current power: {self.spawn_prop}\n"
            f"2^{self.spawn_prop} = {2**self.spawn_prop}\nChange to...")
        if val and val.isdigit():
            self.spawn_prop = max(1, min(20, int(val)))
        self._update_score_labels()

    # Add1 ────────────────────────────────────────────────────────
    def _special_add1_left(self):
        target = 2 ** self.spawn_prop
        empty  = [(r, c) for r in range(4) for c in range(4)
                  if self.board[r][c] == 0 or self.board[r][c] < target]
        if empty:
            r, c = random.choice(empty)
            self.board[r][c] = target
        self._special_unlock()
        self._refresh()

    def _special_add1_right(self):
        self._special_set_right()

    # AddAll ──────────────────────────────────────────────────────
    def _special_add_all_left(self):
        target = 2 ** self.spawn_prop
        for r in range(4):
            for c in range(4):
                if self.board[r][c] == 0 or self.board[r][c] < target:
                    self.board[r][c] = target
        self._special_unlock()
        self._refresh()

    def _special_add_all_right(self):
        val = simpledialog.askstring(
            "Spawn power",
            f"Current power: {self.spawn_prop}\n"
            f"2^{self.spawn_prop} = {2**self.spawn_prop}\nChange to...")
        if val and val.isdigit():
            self.spawn_prop = max(1, min(18, int(val)))
        self._update_score_labels()

    # ── Address helper (B2..E5 → 0-based row, col) ───────────────
    @staticmethod
    def _addr_to_rc(addr: str):
        """Convert Excel-style address 'B2'..'E5' to (row, col) 0-based."""
        if len(addr) < 2:
            return None
        col_letter = addr[0]
        row_digit  = addr[1]
        col_map = {"B": 0, "C": 1, "D": 2, "E": 3}
        row_map = {"2": 0, "3": 1, "4": 2, "5": 3}
        if col_letter in col_map and row_digit in row_map:
            return row_map[row_digit], col_map[col_letter]
        return None

    def _special_unlock(self):
        self.locked_perm = False
        self._hide_overlay()


# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Game2048()