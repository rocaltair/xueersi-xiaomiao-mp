import time
import network
import socket
from lib.wifi_manager import WifiManager


def run(ctx):
    ed = ctx.ed
    disp = ctx.ed.display
    wm = WifiManager()

    if wm.is_connected():
        _show_connected(ed, disp, wm)
        _wait_for_b(ctx)
        return

    _show_scanning(ed, disp)
    networks = _scan_networks()

    disp.fill(0)
    ed.text("启动热点中...", 4, 50, 0xFFFF, show=False)
    disp.show()

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="智能学习机", authmode=network.AUTH_OPEN)

    for _ in range(50):
        if ap.active():
            break
        time.sleep_ms(100)

    ap_ip = ap.ifconfig()[0]

    disp.fill(0)
    ed.text("WiFi 配置", 4, 0, 0xFFE0, show=False)
    disp.hline(0, 18, 160, 0xFFE0)

    ed.text("1. 手机连接热点:", 4, 24, 0xFFFF, show=False)
    ed.text("\"智能学习机\"", 12, 42, 0x07FF, show=False)

    ed.text("2. 浏览器打开:", 4, 66, 0xFFFF, show=False)
    ed.text("http://" + ap_ip, 12, 84, 0x07FF, show=False)

    ed.text("按 B 取消", 4, 110, 0x7BEF, show=False)
    disp.show()

    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.settimeout(1)

    connected = False
    prev_b = True

    while True:
        state = ctx.k_b.button.value()
        if not state and prev_b:
            break
        prev_b = state

        try:
            conn, addr = s.accept()
        except OSError:
            time.sleep_ms(100)
            continue

        try:
            req = conn.recv(1024).decode()
            if req.startswith("POST"):
                ssid, pwd = _parse_post(req, conn)
                if ssid:
                    wm._save_config(ssid, pwd)
                    _show_connecting(ed, disp, ssid)
                    connected = _try_connect(wm)
                    if connected:
                        _send_response(conn, _result_page(True, wm.get_ip()))
                    else:
                        _send_response(conn, _result_page(False, ""))
                    conn.close()
                    if connected:
                        break
            else:
                _send_response(conn, _config_page(networks))
        except Exception:
            pass
        finally:
            conn.close()

    s.close()
    ap.active(False)

    if connected:
        _show_connected(ed, disp, wm)
    else:
        disp.fill(0)
        ed.text("已取消", 4, 50, 0x7BEF, show=False)
        disp.show()

    _wait_for_b(ctx)


def _scan_networks():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    try:
        nets = sta.scan()
        nets.sort(key=lambda x: x[3], reverse=True)  # by RSSI
        return nets
    except:
        return []
    finally:
        sta.active(False)


def _try_connect(wm):
    wm.turn_off()
    time.sleep_ms(500)
    return wm.turn_on()


def _parse_post(req, conn):
    body = req.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in req else ""

    cl = 0
    for line in req.split("\r\n"):
        if line.lower().startswith("content-length:"):
            cl = int(line.split(":")[1].strip())
            break

    while len(body) < cl:
        body += conn.recv(1024).decode()

    params = {}
    for pair in body.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            params[_urldecode(k)] = _urldecode(v)

    return params.get("ssid", "").strip(), params.get("password", "").strip()


def _urldecode(s):
    s = s.replace("+", " ")
    out = bytearray(len(s))
    n = 0
    i = 0
    while i < len(s):
        if s[i] == "%" and i + 2 < len(s):
            try:
                out[n] = int(s[i + 1:i + 3], 16)
                i += 3
                n += 1
            except:
                out[n] = ord(s[i])
                i += 1
                n += 1
        else:
            out[n] = ord(s[i])
            i += 1
            n += 1
    return str(out[:n], "utf-8")


def _send_response(conn, html):
    body = html.encode("utf-8")
    conn.send("HTTP/1.1 200 OK\r\n")
    conn.send("Content-Type: text/html; charset=utf-8\r\n")
    conn.send("Content-Length: {}\r\n".format(len(body)))
    conn.send("Connection: close\r\n")
    conn.send("\r\n")
    conn.write(body)


def _config_page(networks):
    html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WiFi 配置</title>
<style>
body{font-family:sans-serif;margin:20px;max-width:400px}
h2{color:#333}
label{display:block;margin:12px 0 4px}
input,select{width:100%;padding:10px;font-size:16px;box-sizing:border-box}
input[type=submit]{background:#07E0;color:#000;border:none;padding:12px;font-size:18px;margin-top:16px;border-radius:6px}
.error{color:red;margin:8px 0}
</style></head><body>
<h2>智能学习机 - WiFi 配置</h2>
<form method="POST">"""

    visible = [(n[0].decode(), n[3]) for n in networks if n[0]]
    if visible:
        html += '<label>选择 WiFi 网络:</label><select name="ssid">'
        seen = set()
        for ssid, rssi in visible:
            if ssid and ssid not in seen:
                seen.add(ssid)
                html += '<option value="{0}">{0}</option>'.format(ssid)
        html += "</select><br>"
    else:
        html += '<label>WiFi 名称:</label><input name="ssid" placeholder="请输入 WiFi 名称"><br>'

    html += """<label>密码:</label><input type="password" name="password" placeholder="请输入 WiFi 密码">
<input type="submit" value="连接">
</form></body></html>"""
    return html


def _result_page(success, ip):
    if success:
        return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>连接成功</title><style>
body{font-family:sans-serif;margin:20px;text-align:center}
h2{color:#07E0}
</style></head><body>
<h2>连接成功!</h2>
<p>IP: {}</p>
<p>设备已连接，此页面可关闭。</p>
</body></html>""".format(ip)

    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>连接失败</title><style>
body{font-family:sans-serif;margin:20px;text-align:center}
h2{color:#F800}
</style></head><body>
<h2>连接失败</h2>
<p>请检查 WiFi 名称和密码是否正确</p>
</body></html>"""


def _show_scanning(ed, disp):
    disp.fill(0)
    ed.text("扫描网络中...", 4, 50, 0xFFFF, show=False)
    disp.show()


def _show_connecting(ed, disp, ssid):
    disp.fill(0)
    ed.text("正在连接...", 4, 20, 0xFFE0, show=False)
    ed.text(ssid, 4, 40, 0xFFFF, show=False)
    ed.text("请稍候", 4, 60, 0x7BEF, show=False)
    disp.show()


def _show_connected(ed, disp, wm):
    disp.fill(0)
    ed.text("WiFi 连接成功!", 4, 10, 0x07E0, show=False)
    disp.text("IP: " + wm.get_ip(), 4, 32, 0xFFFF)
    ssid = wm.get_ssid()
    if ssid:
        disp.text("SSID: " + ssid, 4, 44, 0xFFFF)
    ed.text("按 B 返回", 4, 100, 0x7BEF, show=False)
    disp.show()


def _wait_for_b(ctx):
    prev = True
    for _ in range(500):
        state = ctx.k_b.button.value()
        if not state and prev:
            break
        prev = state
        time.sleep_ms(20)
