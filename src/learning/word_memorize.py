import time
import random


WORDS = [
    ("apple", "苹果"), ("book", "书"), ("cat", "猫"), ("dog", "狗"),
    ("egg", "鸡蛋"), ("fish", "鱼"), ("girl", "女孩"), ("house", "房子"),
    ("ice", "冰"), ("juice", "果汁"), ("key", "钥匙"), ("lion", "狮子"),
    ("moon", "月亮"), ("nose", "鼻子"), ("orange", "橙子"), ("pig", "猪"),
    ("queen", "女王"), ("rabbit", "兔子"), ("sun", "太阳"), ("tree", "树"),
    ("umbrella", "雨伞"), ("van", "面包车"), ("water", "水"), ("fox", "狐狸"),
    ("yellow", "黄色"), ("zoo", "动物园"), ("bird", "鸟"), ("cloud", "云"),
    ("duck", "鸭子"), ("eye", "眼睛"), ("flower", "花"), ("grass", "草"),
    ("hand", "手"), ("island", "岛屿"), ("jump", "跳"), ("kite", "风筝"),
    ("leaf", "叶子"), ("milk", "牛奶"), ("name", "名字"), ("owl", "猫头鹰"),
]


class WordMemorize:
    def __init__(self, ctx):
        self.ctx = ctx
        self.disp = ctx.ed.display

        self.score = 0
        self.total = 0
        self._new_word()

    def _new_word(self):
        n = len(WORDS)
        self.word_en, self.word_cn = WORDS[random.randint(0, n - 1)]
        # Generate 3 wrong options
        opts = [self.word_cn]
        while len(opts) < 4:
            w = WORDS[random.randint(0, n - 1)][1]
            if w not in opts:
                opts.append(w)
        random.shuffle(opts)
        self.options = opts
        self.selected = 0
        self.answered = False
        self.correct = False

    def run(self):
        saved = (self.ctx.k_u.down_func, self.ctx.k_d.down_func,
                 self.ctx.k_a.down_func, self.ctx.k_b.down_func)

        for btn in (self.ctx.k_u, self.ctx.k_d, self.ctx.k_a, self.ctx.k_b):
            btn.down_func = None

        pins = (self.ctx.k_u.button, self.ctx.k_d.button,
                self.ctx.k_a.button, self.ctx.k_b.button)
        prev = [True] * 4

        running = True
        result_timer = 0
        showing_result = False

        while running:
            for i, pin in enumerate(pins):
                state = pin.value()
                if not state and prev[i]:
                    if i == 3:  # B = quit
                        running = False
                    elif showing_result:
                        pass
                    elif i == 0:  # Up - prev option
                        self.selected = max(0, self.selected - 1)
                    elif i == 1:  # Down - next option
                        self.selected = min(3, self.selected + 1)
                    elif i == 2:  # A - submit
                        self.total += 1
                        self.correct = self.options[self.selected] == self.word_cn
                        if self.correct:
                            self.score += 1
                        showing_result = True
                        result_timer = time.ticks_ms()
                    time.sleep_ms(100)
                prev[i] = state

            if showing_result and time.ticks_ms() - result_timer > 1500:
                showing_result = False
                self._new_word()

            self._draw(showing_result)
            time.sleep_ms(30)

        self.ctx.k_u.down_func = saved[0]
        self.ctx.k_d.down_func = saved[1]
        self.ctx.k_a.down_func = saved[2]
        self.ctx.k_b.down_func = saved[3]

    def _draw(self, showing_result):
        disp = self.disp
        disp.fill(0)

        if showing_result:
            if self.correct:
                disp.text("CORRECT!", 20, 56, 0x07E0)
            else:
                disp.text("WRONG!", 20, 48, 0xF800)
                disp.text(self.word_cn, 20, 60, 0xFFFF)
        else:
            disp.text("What is:", 0, 8, 0xFFFF)
            disp.text(self.word_en, 0, 20, 0xFFE0)

            for i, opt in enumerate(self.options):
                prefix = " >" if i == self.selected else "  "
                y = 50 + i * 16
                disp.text(prefix + opt, 0, y, 0xFFFF)

        pct = (self.score * 100 // self.total) if self.total > 0 else 0
        disp.text("Score: {}/{} {}%".format(self.score, self.total, pct),
                  0, 0, 0xFFFF)

        if not showing_result:
            disp.text("UP/DOWN choose A=ok", 0, 118, 0x7BEF)

        disp.show()


def run(ctx):
    game = WordMemorize(ctx)
    game.run()
