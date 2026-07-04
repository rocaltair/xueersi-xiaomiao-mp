import time
import random


class Arithmetic:
    def __init__(self, ctx, params=None):
        self.ctx = ctx
        self.ed = ctx.ed
        self.disp = ctx.ed.display

        self.max_num = 10
        self.allowed_op = None  # None = random + and -
        if params:
            self.max_num = params.get("max_num", self.max_num)
            self.allowed_op = params.get("op", self.allowed_op)

        self.score = 0
        self.total = 0
        self.showing_result = False
        self._new_question()

    def _new_question(self):
        if self.allowed_op == "+":
            self.a = random.randint(1, self.max_num - 1)
            self.b = random.randint(1, self.max_num - self.a)
            self.op = "+"
            self.answer = self.a + self.b
        elif self.allowed_op == "-":
            self.a = random.randint(1, self.max_num)
            self.b = random.randint(1, self.a)
            self.op = "-"
            self.answer = self.a - self.b
        else:
            self.a = random.randint(1, self.max_num)
            self.b = random.randint(1, self.max_num)
            if random.randint(0, 1) == 0:
                self.op = "+"
                self.answer = self.a + self.b
            else:
                if self.a < self.b:
                    self.a, self.b = self.b, self.a
                self.op = "-"
                self.answer = self.a - self.b

        self.guess = 0
        self.correct = False
        self.showing_result = False

    def _draw_apple(self, x, y):
        cx, cy = x + 3, y + 4
        r = 3
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.disp.pixel(cx + dx, cy + dy, 0xF800)
        self.disp.pixel(cx, y, 0x7B2C)
        self.disp.pixel(cx - 1, y + 1, 0x7B2C)
        self.disp.pixel(cx, y + 1, 0x7B2C)
        self.disp.pixel(cx + 1, y + 1, 0x7B2C)
        self.disp.pixel(cx + 1, y, 0x07E0)

    def _draw_bitten_apple(self, x, y):
        cx, cy = x + 3, y + 4
        r = 3
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.disp.pixel(cx + dx, cy + dy, 0xF800)
        self.disp.pixel(cx, y, 0x7B2C)
        self.disp.pixel(cx - 1, y + 1, 0x7B2C)
        self.disp.pixel(cx, y + 1, 0x7B2C)
        self.disp.pixel(cx + 1, y + 1, 0x7B2C)
        self.disp.pixel(cx + 1, y, 0x07E0)
        bite_cx, bite_cy = cx + 2, cy - 2
        bite_r = 2
        for dy in range(-bite_r, bite_r + 1):
            for dx in range(-bite_r, bite_r + 1):
                if dx * dx + dy * dy <= bite_r * bite_r:
                    self.disp.pixel(bite_cx + dx, bite_cy + dy, 0x0000)

    def _draw_apples(self, count, x, y, bitten=False):
        draw = self._draw_bitten_apple if bitten else self._draw_apple
        for _ in range(count):
            if x + 8 > 156:
                x = 4
                y += 8
            draw(x, y)
            x += 8
        return x, y

    def _draw_equation(self, y, show_answer):
        disp = self.disp
        x = 4
        start_y = y

        x, y = self._draw_apples(self.a, x, y, bitten=False)

        if x + 8 > 156:
            x = 4
            y += 10
        disp.text(self.op, x, y + 1, 0xFFFF)
        x += 8

        x, y = self._draw_apples(self.b, x, y, bitten=(self.op == "-"))

        if show_answer:
            if x + 8 > 156:
                x = 4
                y += 10
            disp.text("=", x, y + 1, 0xFFFF)
            x += 8
            x, y = self._draw_apples(self.answer, x, y, bitten=False)
        else:
            if x + 14 > 156:
                x = 4
                y += 10
            disp.text("=?", x, y + 1, 0xFFFF)

        return y + 10 - start_y

    def run(self):
        random.seed(time.ticks_ms())

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

        while running:
            for i, pin in enumerate(pins):
                state = pin.value()
                if not state and prev[i]:
                    if i == 5:  # B = quit
                        running = False
                    elif i == 4:  # A = submit / next
                        if self.showing_result:
                            self._new_question()
                        else:
                            self.total += 1
                            self.correct = self.guess == self.answer
                            if self.correct:
                                self.score += 1
                            self.showing_result = True
                    elif not self.showing_result:
                        if i == 3:  # Up
                            self.guess = min(20, self.guess + 1)
                        elif i == 2:  # Down
                            self.guess = max(0, self.guess - 1)
                        elif i == 0:  # Left = -5
                            self.guess = max(0, self.guess - 5)
                        elif i == 1:  # Right = +5
                            self.guess = min(20, self.guess + 5)
                    time.sleep_ms(100)
                prev[i] = state

            self._draw()
            time.sleep_ms(30)

        self.ctx.k_u.down_func = saved[0]
        self.ctx.k_d.down_func = saved[1]
        self.ctx.k_l.down_func = saved[2]
        self.ctx.k_r.down_func = saved[3]
        self.ctx.k_a.down_func = saved[4]
        self.ctx.k_b.down_func = saved[5]

    def _draw(self):
        disp = self.disp
        disp.fill(0)

        # Title + score on one line
        if self.allowed_op == "+":
            mode = "{}以内加法".format(self.max_num)
        elif self.allowed_op == "-":
            mode = "{}以内减法".format(self.max_num)
        else:
            mode = "1~{}加减法".format(self.max_num)
        self.ed.text(mode, 0, 0, 0xFFFF, show=False)
        disp.text("{}/{}".format(self.score, self.total), 120, 0, 0xFFE0)

        if self.showing_result:
            eq = "{} {} {} = {}".format(self.a, self.op, self.b, self.answer)
            disp.text(eq, 4, 22, 0xFFFF)
            h = self._draw_equation(34, show_answer=True)

            fy = 34 + max(h, 30)
            if self.correct:
                disp.text("CORRECT! Press A", 4, fy, 0x07E0)
            else:
                disp.text("WRONG!  Press A", 4, fy, 0xF800)
        else:
            eq = "{} {} {} = ?".format(self.a, self.op, self.b)
            disp.text(eq, 4, 22, 0xFFFF)
            h = self._draw_equation(34, show_answer=False)

            fy = 34 + max(h, 30)
            disp.text("Your answer:", 4, fy, 0x7BEF)
            disp.text(str(self.guess), 48, fy + 12, 0xFFE0)

        disp.text("A=submit  B=quit", 0, 118, 0x7BEF)
        disp.show()


def run(ctx, params=None):
    game = Arithmetic(ctx, params)
    game.run()
