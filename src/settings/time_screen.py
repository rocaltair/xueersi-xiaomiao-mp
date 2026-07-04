import time
from lib.wifi_manager import WifiManager


def run(ctx):
    ed = ctx.ed
    disp = ctx.ed.display
    wm = WifiManager()

    pins = (ctx.k_b.button, ctx.k_a.button)
    prev = [True] * 2

    sync_msg = ""
    sync_timer = 0
    running = True

    while running:
        for i, pin in enumerate(pins):
            state = pin.value()
            if not state and prev[i]:
                if i == 0:  # B = quit
                    running = False
                elif i == 1:  # A = sync NTP
                    if wm.is_connected():
                        sync_msg = "同步中..."
                        sync_timer = time.ticks_ms()
                        ed.text("同步中...", 4, 80, 0xFFE0, show=False)
                        disp.show()
                        ok = wm.sync_time()
                        sync_msg = "同步成功!" if ok else "同步失败"
                        sync_timer = time.ticks_ms()
                    else:
                        sync_msg = "WiFi 未连接!"
                        sync_timer = time.ticks_ms()
                time.sleep_ms(100)
            prev[i] = state

        disp.fill(0)

        disp.text("Date / Time", 4, 0, 0xFFE0)

        t = time.localtime()
        year, month, day, hour, minute, second, weekday, _ = t

        date_str = "{:04d}-{:02d}-{:02d}".format(year, month, day)
        disp.text(date_str, 4, 16, 0xFFFF)

        time_str = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
        disp.text(time_str, 4, 30, 0x07FF)

        if wm.is_connected():
            disp.text("WiFi: OK  " + wm.get_ip(), 4, 50, 0x07E0)
        else:
            disp.text("WiFi: OFF", 4, 50, 0xF800)

        if sync_msg:
            elapsed = time.ticks_diff(time.ticks_ms(), sync_timer)
            if elapsed < 3000:
                ed.text(sync_msg, 4, 66, 0xFFE0, show=False)
            else:
                sync_msg = ""

        ed.text("A: NTP同步  B: 返回", 4, 108, 0x7BEF, show=False)
        disp.show()

        time.sleep_ms(200)
