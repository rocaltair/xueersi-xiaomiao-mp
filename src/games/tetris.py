import time
import random


class Tetris:
    COLS = 10
    ROWS = 14
    CELL = 8
    GRID_X = 28
    GRID_Y = 16
    PANEL_X = 116

    SHAPES = [
        [(0, 0), (0, 1), (0, 2), (0, 3)],  # I
        [(0, 0), (0, 1), (1, 0), (1, 1)],  # O
        [(0, 0), (0, 1), (0, 2), (1, 1)],  # T
        [(0, 1), (0, 2), (1, 0), (1, 1)],  # S
        [(0, 0), (0, 1), (1, 1), (1, 2)],  # Z
        [(0, 0), (1, 0), (1, 1), (1, 2)],  # J
        [(0, 2), (1, 0), (1, 1), (1, 2)],  # L
    ]

    COLORS = [
        0x07FF,  # I - Cyan
        0xFFE0,  # O - Yellow
        0xF81F,  # T - Magenta
        0x07E0,  # S - Green
        0xF800,  # Z - Red
        0x001F,  # J - Blue
        0xFD20,  # L - Orange
    ]

    def __init__(self, ctx):
        self.ctx = ctx
        self.ed = ctx.ed

        self.reset()

    def reset(self):
        self.board = [[0] * self.COLS for _ in range(self.ROWS)]
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.playing = False
        self.paused = False
        self.next_idx = random.randint(0, len(self.SHAPES) - 1)
        self._new_piece()

    def _new_piece(self):
        idx = self.next_idx
        self.piece = [list(p) for p in self.SHAPES[idx]]
        self.piece_color = self.COLORS[idx]
        self.piece_row = 0
        self.piece_col = self.COLS // 2 - 2
        self.next_idx = random.randint(0, len(self.SHAPES) - 1)
        if not self._valid(self.piece, self.piece_row, self.piece_col):
            self.game_over = True

    def _valid(self, shape, row, col):
        for r, c in shape:
            nr, nc = row + r, col + c
            if nc < 0 or nc >= self.COLS or nr >= self.ROWS:
                return False
            if nr >= 0 and self.board[nr][nc]:
                return False
        return True

    def _move_left(self):
        if self._valid(self.piece, self.piece_row, self.piece_col - 1):
            self.piece_col -= 1

    def _move_right(self):
        if self._valid(self.piece, self.piece_row, self.piece_col + 1):
            self.piece_col += 1

    def _move_down(self):
        if self._valid(self.piece, self.piece_row + 1, self.piece_col):
            self.piece_row += 1
            return True
        self._lock()
        return False

    def _rotate(self):
        r, c = self.piece_row, self.piece_col
        rotated = [(cc, -rr) for rr, cc in self.piece]
        if not rotated:
            return
        min_r = min(x for x, _ in rotated)
        min_c = min(x for _, x in rotated)
        rotated = [(x - min_r, y - min_c) for x, y in rotated]
        if self._valid(rotated, r, c):
            self.piece = rotated

    def _drop(self):
        while self._valid(self.piece, self.piece_row + 1, self.piece_col):
            self.piece_row += 1
        self._lock()

    def _lock(self):
        for r, c in self.piece:
            nr = self.piece_row + r
            nc = self.piece_col + c
            if 0 <= nr < self.ROWS and 0 <= nc < self.COLS:
                self.board[nr][nc] = self.piece_color
        self._clear_lines()
        self._new_piece()

    def _clear_lines(self):
        new_board = [row for row in self.board if any(c == 0 for c in row)]
        cleared = self.ROWS - len(new_board)
        if cleared:
            self.score += cleared * 100
            self.lines += cleared
        while len(new_board) < self.ROWS:
            new_board.insert(0, [0] * self.COLS)
        self.board = new_board

    def _get_level(self):
        return min(self.lines // 100, 8) + 1  # 1-9

    def _get_speed(self):
        level = self._get_level()
        return max(100, 500 - (level - 1) * 50)

    def draw(self):
        disp = self.ed.display
        disp.fill(0)

        # Grid border
        disp.rect(self.GRID_X, self.GRID_Y,
                  self.COLS * self.CELL, self.ROWS * self.CELL, 0xFFFF)

        # Board cells
        for r in range(self.ROWS):
            for c in range(self.COLS):
                color = self.board[r][c]
                if color:
                    x = self.GRID_X + c * self.CELL + 1
                    y = self.GRID_Y + r * self.CELL + 1
                    disp.fill_rect(x, y, self.CELL - 2, self.CELL - 2, color)

        # Current piece
        for r, c in self.piece:
            nr = self.piece_row + r
            nc = self.piece_col + c
            if nr >= 0:
                x = self.GRID_X + nc * self.CELL + 1
                y = self.GRID_Y + nr * self.CELL + 1
                disp.fill_rect(x, y, self.CELL - 2, self.CELL - 2, self.piece_color)

        # Score (framebuf built-in 8x8 font)
        s = str(self.score)
        disp.text("SCORE", self.PANEL_X, 0, 0xFFFF)
        disp.text(s, self.PANEL_X, 10, 0xFFE0)

        # Next piece
        disp.text("NEXT", self.PANEL_X, 24, 0xFFFF)
        px, py = self.PANEL_X, 34
        disp.rect(px, py, 40, 40, 0xFFFF)
        shape = self.SHAPES[self.next_idx]
        color = self.COLORS[self.next_idx]
        rows = [r for r, _ in shape]
        cols = [c for _, c in shape]
        min_r, max_r = min(rows), max(rows)
        min_c, max_c = min(cols), max(cols)
        pw = (max_c - min_c + 1) * self.CELL
        ph = (max_r - min_r + 1) * self.CELL
        ox = px + (40 - pw) // 2
        oy = py + (40 - ph) // 2
        for r, c in shape:
            x = ox + (c - min_c) * self.CELL + 1
            y = oy + (r - min_r) * self.CELL + 1
            disp.fill_rect(x, y, self.CELL - 2, self.CELL - 2, color)

        # Level
        disp.text("LEVEL", self.PANEL_X, 78, 0xFFFF)
        disp.text(str(self._get_level()), self.PANEL_X, 88, 0xFFE0)

        # Paused overlay
        if self.paused:
            disp.text("PAUSED", self.GRID_X + 8,
                      self.GRID_Y + 55, 0xFFE0)

        # Game over
        if self.game_over:
            disp.text("GAME OVER", self.GRID_X + 8,
                      self.GRID_Y + 50, 0xF800)

        disp.show()

    def _quit(self):
        self.playing = False

    def play(self):
        self.reset()
        self.draw()

        saved = (self.ctx.k_u.down_func, self.ctx.k_d.down_func,
                 self.ctx.k_l.down_func, self.ctx.k_r.down_func,
                 self.ctx.k_a.down_func, self.ctx.k_b.down_func)

        # Disable IRQ-based handlers (poll GPIO directly instead)
        for btn in (self.ctx.k_u, self.ctx.k_d, self.ctx.k_l,
                     self.ctx.k_r, self.ctx.k_a, self.ctx.k_b):
            btn.down_func = None

        # GPIO pins (True = released / HIGH, False = pressed / LOW)
        # Order: left, right, down, up, a, b
        pins = (self.ctx.k_l.button, self.ctx.k_r.button, self.ctx.k_d.button,
                self.ctx.k_u.button, self.ctx.k_a.button, self.ctx.k_b.button)
        prev = [True] * 6  # previous pin state (all released)

        self.playing = True
        self.paused = False
        last_tick = time.ticks_ms()

        while self.playing and not self.game_over:
            # Poll GPIO pins
            for i, pin in enumerate(pins):
                state = pin.value()
                if not state and prev[i]:  # falling edge: just pressed
                    if i == 4:  # A button = rotate
                        if not pins[5].value():  # B also pressed = quit
                            self._quit()
                        else:
                            self._rotate()
                    elif i == 5:  # B button = drop
                        if not pins[4].value():  # A also pressed = quit
                            self._quit()
                        else:
                            self._drop()
                    elif i == 3:  # Up button = pause/resume
                        self.paused = not self.paused
                    elif not self.paused:
                        if i == 0:
                            self._move_left()
                        elif i == 1:
                            self._move_right()
                        elif i == 2:
                            self._move_down()
                    time.sleep_ms(80)  # debounce
                prev[i] = state

            # Gravity (only when not paused)
            if not self.paused:
                now = time.ticks_ms()
                if now - last_tick >= self._get_speed():
                    last_tick = now
                    self._move_down()

            self.draw()
            time.sleep_ms(20)

        if self.game_over:
            self.draw()
            time.sleep_ms(2000)

        self.ctx.k_u.down_func = saved[0]
        self.ctx.k_d.down_func = saved[1]
        self.ctx.k_l.down_func = saved[2]
        self.ctx.k_r.down_func = saved[3]
        self.ctx.k_a.down_func = saved[4]
        self.ctx.k_b.down_func = saved[5]


def run(ctx):
    game = Tetris(ctx)
    game.play()
