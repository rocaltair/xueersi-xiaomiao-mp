import time


# Sokoban level: 0=floor, 1=wall, 2=player, 3=box, 4=target, 5=box+target
# 8 columns x 8 rows to fit CELL=16 in 128px
LEVEL = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 1],
    [1, 0, 3, 0, 0, 4, 0, 1],
    [1, 0, 1, 0, 0, 4, 0, 1],
    [1, 0, 3, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

COLS = 8
ROWS = 8
CELL = 16
GRID_X = 16
GRID_Y = 16


class Sokoban:
    def __init__(self, ctx):
        self.ctx = ctx
        self.disp = ctx.ed.display
        self.map = [row[:] for row in LEVEL]
        self.px, self.py = self._find_player()
        self.targets = self._find_targets()
        self.boxes = self._find_boxes()
        self.steps = 0

    def _find_player(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.map[r][c] == 2:
                    return (c, r)
        return (1, 1)

    def _find_targets(self):
        t = []
        for r in range(ROWS):
            for c in range(COLS):
                if self.map[r][c] == 4 or self.map[r][c] == 5:
                    t.append((c, r))
        return t

    def _find_boxes(self):
        b = []
        for r in range(ROWS):
            for c in range(COLS):
                if self.map[r][c] == 3 or self.map[r][c] == 5:
                    b.append((c, r))
        return b

    def _is_box(self, x, y):
        return (x, y) in self.boxes

    def _is_target(self, x, y):
        return (x, y) in self.targets

    def _move(self, dx, dy):
        nx, ny = self.px + dx, self.py + dy
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
            return
        if self.map[ny][nx] == 1:
            return  # wall

        if self._is_box(nx, ny):
            # Push box
            bx, by = nx + dx, ny + dy
            if bx < 0 or bx >= COLS or by < 0 or by >= ROWS:
                return
            if self.map[by][bx] == 1 or self._is_box(bx, by):
                return
            # Move box
            self.boxes.remove((nx, ny))
            self.boxes.append((bx, by))
            self.map[ny][nx] = 5 if self._is_target(nx, ny) else 0  # was box, now target or empty
            self.map[by][bx] = 5  # box on target (we'll check targets separately)

        self.map[self.py][self.px] = 0
        self.px, self.py = nx, ny
        self.map[ny][nx] = 2
        self.steps += 1

    def _check_win(self):
        for bx, by in self.boxes:
            if not self._is_target(bx, by):
                return False
        return True

    def _draw_map(self, won):
        disp = self.disp
        for r in range(ROWS):
            for c in range(COLS):
                x = GRID_X + c * CELL
                y = GRID_Y + r * CELL
                val = self.map[r][c]
                is_target = self._is_target(c, r)
                is_box = self._is_box(c, r)

                if val == 1:  # wall
                    disp.fill_rect(x, y, CELL, CELL, 0x001F)
                elif is_box and is_target:
                    disp.fill_rect(x + 1, y + 1, CELL - 2, CELL - 2, 0x07E0)  # green box on target
                elif is_box:
                    disp.fill_rect(x + 1, y + 1, CELL - 2, CELL - 2, 0xFFE0)  # yellow box
                elif is_target:
                    disp.fill_rect(x + 3, y + 3, CELL - 6, CELL - 6, 0xF81F)  # target dot
                elif val == 2:
                    disp.fill_rect(x + 1, y + 1, CELL - 2, CELL - 2, 0x07FF)  # player cyan

    def run(self):
        saved = (self.ctx.k_u.down_func, self.ctx.k_d.down_func,
                 self.ctx.k_l.down_func, self.ctx.k_r.down_func,
                 self.ctx.k_a.down_func, self.ctx.k_b.down_func)

        for btn in (self.ctx.k_u, self.ctx.k_d, self.ctx.k_l,
                     self.ctx.k_r, self.ctx.k_a, self.ctx.k_b):
            btn.down_func = None

        pins = (self.ctx.k_l.button, self.ctx.k_r.button,
                self.ctx.k_d.button, self.ctx.k_u.button,
                self.ctx.k_a.button, self.ctx.k_b.button)
        prev = [True] * 6

        running = True
        won = False

        while running:
            for i, pin in enumerate(pins):
                state = pin.value()
                if not state and prev[i]:
                    if i == 5:  # B = quit
                        running = False
                    elif not won:
                        dx, dy = 0, 0
                        if i == 0: dx = -1
                        elif i == 1: dx = 1
                        elif i == 2: dy = 1
                        elif i == 3: dy = -1
                        if dx or dy:
                            self._move(dx, dy)
                            if self._check_win():
                                won = True
                        elif i == 4:  # A = reset
                            self.map = [row[:] for row in LEVEL]
                            self.px, self.py = self._find_player()
                            self.targets = self._find_targets()
                            self.boxes = self._find_boxes()
                            self.steps = 0
                            won = False
                    time.sleep_ms(100)
                prev[i] = state

            self._draw(won)
            time.sleep_ms(30)

        self.ctx.k_u.down_func = saved[0]
        self.ctx.k_d.down_func = saved[1]
        self.ctx.k_l.down_func = saved[2]
        self.ctx.k_r.down_func = saved[3]
        self.ctx.k_a.down_func = saved[4]
        self.ctx.k_b.down_func = saved[5]

    def _draw(self, won):
        disp = self.disp
        disp.fill(0)

        self._draw_map(won)

        # Info line
        if won:
            disp.text("YOU WIN! Steps:{}".format(self.steps), 0, 0, 0x07E0)
        else:
            disp.text("SOKOBAN Steps:{}".format(self.steps), 0, 0, 0xFFFF)
            disp.text("A=reset B=quit", 0, 120, 0x7BEF)

        disp.show()


def run(ctx):
    game = Sokoban(ctx)
    game.run()
