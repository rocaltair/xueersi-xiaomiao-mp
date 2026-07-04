import time


# Simple maze: 0=path, 1=wall, 2=start, 3=end
MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 1, 0, 0, 0, 0, 0, 1, 3, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

COLS = 13
ROWS = 9
CELL = 12
GRID_X = 2
GRID_Y = 8


class Maze:
    def __init__(self, ctx):
        self.ctx = ctx
        self.disp = ctx.ed.display
        self.map = [row[:] for row in MAZE]
        self.start_pos = self._find(2)
        self.end_pos = self._find(3)
        self.px, self.py = self.start_pos

    def _find(self, val):
        for r in range(ROWS):
            for c in range(COLS):
                if self.map[r][c] == val:
                    return (c, r)
        return (1, 1)

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
        steps = 0
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
                            nx, ny = self.px + dx, self.py + dy
                            if 0 <= nx < COLS and 0 <= ny < ROWS:
                                if self.map[ny][nx] != 1:
                                    self.px, self.py = nx, ny
                                    steps += 1
                                    if (self.px, self.py) == self.end_pos:
                                        won = True
                    time.sleep_ms(100)
                prev[i] = state

            self._draw(won, steps)
            time.sleep_ms(30)

        self.ctx.k_u.down_func = saved[0]
        self.ctx.k_d.down_func = saved[1]
        self.ctx.k_l.down_func = saved[2]
        self.ctx.k_r.down_func = saved[3]
        self.ctx.k_a.down_func = saved[4]
        self.ctx.k_b.down_func = saved[5]

    def _draw(self, won, steps):
        disp = self.disp
        disp.fill(0)

        # Title
        disp.text("MAZE", 0, 0, 0xFFFF)

        # Draw maze
        for r in range(ROWS):
            for c in range(COLS):
                x = GRID_X + c * CELL
                y = GRID_Y + r * CELL
                val = self.map[r][c]
                if val == 1:  # wall
                    disp.fill_rect(x, y, CELL, CELL, 0x001F)
                elif val == 3:  # end
                    disp.fill_rect(x, y, CELL, CELL, 0x07E0)

        # Player
        px = GRID_X + self.px * CELL
        py = GRID_Y + self.py * CELL
        disp.fill_rect(px + 1, py + 1, CELL - 2, CELL - 2, 0xFFE0)

        if won:
            disp.text("YOU WIN! Steps:{}".format(steps), 0, 120, 0x07E0)
            disp.text("B=exit", 60, 120, 0x7BEF)
        else:
            disp.text("Steps:{} B=quit".format(steps), 0, 120, 0x7BEF)

        disp.show()


def run(ctx):
    game = Maze(ctx)
    game.run()
