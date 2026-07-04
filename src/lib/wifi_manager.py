import network
import time
import machine

WIFI_CONFIG_FILE = "wifi_config.txt"


class WifiManager:
    def __init__(self):
        self.sta = network.WLAN(network.STA_IF)

    def is_connected(self):
        return self.sta.active() and self.sta.isconnected()

    def is_active(self):
        return self.sta.active()

    def get_ip(self):
        if self.is_connected():
            return self.sta.ifconfig()[0]
        return "0.0.0.0"

    def get_ssid(self):
        if self.is_connected():
            try:
                return self.sta.config("essid")
            except:
                pass
        return ""

    def turn_on(self):
        if self.is_connected():
            return True

        self.sta.active(True)
        time.sleep_ms(200)

        ssid, pwd = self._load_config()
        if ssid:
            self.sta.connect(ssid, pwd)
            for _ in range(100):
                if self.sta.isconnected():
                    return True
                time.sleep_ms(100)

        return self.sta.isconnected()

    def turn_off(self):
        self.sta.active(False)

    def start_smartconfig(self, timeout_s=30):
        if self.is_connected():
            return True

        self.sta.active(True)
        time.sleep_ms(200)

        try:
            self.sta.smartconfig()
        except AttributeError:
            return False

        for _ in range(timeout_s * 10):
            if self.sta.isconnected():
                try:
                    ssid = self.sta.config("essid")
                    self._save_config(ssid, "")
                except:
                    pass
                return True
            time.sleep_ms(100)

        try:
            self.sta.smartconfig_stop()
        except:
            pass
        return False

    def sync_time(self, tz_offset=8):
        import ntptime
        try:
            ntptime.settime()
            rtc = machine.RTC()
            tm = time.mktime(time.localtime()) + tz_offset * 3600
            t = time.localtime(tm)
            rtc.datetime((t[0], t[1], t[2], t[6], t[3], t[4], t[5], 0))
            return True
        except:
            return False

    def _load_config(self):
        try:
            with open(WIFI_CONFIG_FILE, "r") as f:
                ssid = f.readline().strip()
                pwd = f.readline().strip()
                return ssid, pwd
        except:
            return None, None

    def _save_config(self, ssid, password):
        try:
            with open(WIFI_CONFIG_FILE, "w") as f:
                f.write(ssid + "\n")
                f.write(password + "\n")
        except:
            pass
