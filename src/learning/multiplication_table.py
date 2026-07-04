import time


def run(ctx):
    ed = ctx.ed
    disp = ed.display

    # Save button handlers
    saved = (ctx.k_u.down_func, ctx.k_d.down_func,
             ctx.k_a.down_func, ctx.k_b.down_func)

    for btn in (ctx.k_u, ctx.k_d, ctx.k_a, ctx.k_b):
        btn.down_func = None

    pins = (ctx.k_u.button, ctx.k_d.button, ctx.k_a.button, ctx.k_b.button)
    prev = [True] * 4

    offset = 0
    running = True

    while running:
        for i, pin in enumerate(pins):
            state = pin.value()
            if not state and prev[i]:
                if i == 0:  # up
                    offset = max(0, offset - 1)
                elif i == 1:  # down
                    offset = min(4, offset + 1)
                elif i == 3:  # B = quit
                    running = False
                time.sleep_ms(100)
            prev[i] = state

        # Draw
        disp.fill(0)
        y = 0
        disp.text("  乘法口诀", 0, y, 0xFFFF)
        y += 10
        disp.text("  ---------------", 0, y, 0xFFFF)
        y += 10

        for row in range(1 + offset, min(10, 10 + offset)):
            if y > 120:
                break
            line = ""
            for col in range(1, row + 1):
                line += "{}x{}={} ".format(row, col, row * col)
            disp.text(line, 6, y, 0xFFE0)
            y += 10

        disp.text("上/下 滚动  B退出", 0, 120, 0x7BEF)
        disp.show()
        time.sleep_ms(30)

    ctx.k_u.down_func = saved[0]
    ctx.k_d.down_func = saved[1]
    ctx.k_a.down_func = saved[2]
    ctx.k_b.down_func = saved[3]
