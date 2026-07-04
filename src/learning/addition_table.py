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
    # Pre-compute rows: each row is "1+2=3 1+3=4 ..." for a given first number
    rows = []
    for a in range(1, 10):
        line = ""
        for b in range(1, 10):
            line += "{} ".format(a + b)
        rows.append(line)

    running = True

    while running:
        for i, pin in enumerate(pins):
            state = pin.value()
            if not state and prev[i]:
                if i == 0:  # up
                    offset = max(0, offset - 1)
                elif i == 1:  # down
                    offset = min(len(rows) - 8, offset + 1)
                elif i == 3:  # B = quit
                    running = False
                time.sleep_ms(100)
            prev[i] = state

        # Draw
        disp.fill(0)
        disp.text("  ADDITION TABLE", 0, 0, 0xFFFF)
        disp.text("  1 2 3 4 5 6 7 8 9", 6, 12, 0x7BEF)

        for r in range(8):
            idx = offset + r
            if idx >= len(rows):
                break
            label = str(idx + 1)
            label += " " if idx > 8 else "  "
            disp.text(label + rows[idx], 0, 24 + r * 12, 0xFFE0)

        disp.text("UP/DOWN scroll  B=exit", 0, 120, 0x7BEF)
        disp.show()
        time.sleep_ms(30)

    ctx.k_u.down_func = saved[0]
    ctx.k_d.down_func = saved[1]
    ctx.k_a.down_func = saved[2]
    ctx.k_b.down_func = saved[3]
