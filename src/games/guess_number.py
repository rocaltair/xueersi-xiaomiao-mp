import time
import random


class GuessNumber:
    def __init__(self, ctx):
        self.ctx = ctx
        self.disp = ctx.ed.display

        self.target = random.randint(1, 99)
        self.guess = 50
        self.attempts = 0
        self.game_over = False
        self.message = ""
        self.low = 1
        self.high = 99

    def run(self):
        saved = (self.ctx.k_u.down_func, self.ctx.k_d.down_func,
                 self.ctx.k_a.down_func, self.ctx.k_b.down_func)

        for btn in (self.ctx.k_u, self.ctx.k_d, self.ctx.k_a, self.ctx.k_b):
            btn.down_func = None

        pins = (self.ctx.k_u.button, self.ctx.k_d.button,
                self.ctx.k_a.button, self.ctx.k_b.button)
        prev = [True] * 4

        running = True
        feedback_timer = 0
        show_feedback = False

        while running:
            for i, pin in enumerate(pins):
                state = pin.value()
                if not state and prev[i]:
                    if i == 3:  # B = quit
                        running = False
                    elif self.game_over:
                        pass
                    elif show_feedback:
                        pass
                    elif i == 0:  # Up = increase
                        self.guess = min(self.high, self.guess + 1)
                    elif i == 1:  # Down = decrease
                        self.guess = max(self.low, self.guess - 1)
                    elif i == 2:  # A = confirm guess
                        self.attempts += 1
                        if self.guess == self.target:
                            self.message = "Correct! {} tries!".format(self.attempts)
                            self.game_over = True
                        elif self.guess < self.target:
                            self.message = "Too low!"
                            self.low = self.guess + 1
                        else:
                            self.message = "Too high!"
                            self.high = self.guess - 1
                        show_feedback = True
                        feedback_timer = time.ticks_ms()
                    time.sleep_ms(100)
                prev[i] = state

            if show_feedback and not self.game_over:
                if time.ticks_ms() - feedback_timer > 600:
                    show_feedback = False

            self._draw(show_feedback)
            time.sleep_ms(30)

        self.ctx.k_u.down_func = saved[0]
        self.ctx.k_d.down_func = saved[1]
        self.ctx.k_a.down_func = saved[2]
        self.ctx.k_b.down_func = saved[3]

    def _draw(self, show_feedback):
        disp = self.disp
        disp.fill(0)

        disp.text("GUESS THE NUMBER", 0, 0, 0xFFFF)
        disp.text("Range: {}-{}".format(self.low, self.high), 0, 12, 0x7BEF)

        # Show guess big
        disp.text("Your guess:", 0, 35, 0xFFFF)
        disp.text(str(self.guess), 40, 48, 0xFFE0)

        if show_feedback:
            color = 0x07E0 if "Correct" in self.message else 0xF800
            disp.text(self.message, 0, 72, color)

        disp.text("Attempts: {}".format(self.attempts), 0, 110, 0x7BEF)
        disp.text("UP/DOWN A=ok B=quit", 0, 120, 0x7BEF)
        disp.show()


def run(ctx):
    game = GuessNumber(ctx)
    game.run()
