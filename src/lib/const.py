SCREEN_WIDTH, SCREEN_HEIGHT = 160, 128

# pins
PIN_BTN_A     = 34
PIN_BTN_B     = 12
PIN_BTN_UP    = 2
PIN_BTN_DOWN  = 13
PIN_BTN_LEFT  = 27
PIN_BTN_RIGHT = 35

# adc
PIN_LIGHT_SENSOR = 36
PIN_TEMP_SENSOR  = 39
# pwm
PIN_SPEAKER      = 14

PIN_TFT_SCK  = 18
PIN_TFT_RES  = 19
PIN_TFT_MOSI = 23
PIN_TFT_CS   = 5
PIN_TFT_DC   = 4

PIN_SD_SCK  = 18  # reuse PIN_TFT_SCK
PIN_SD_MISO = 19  # reuse PIN_TFT_RES 
PIN_SD_MOSI = 23  # reuse PIN_TFT_MOSI
PIN_SD_CS   = 22

# interface 5 GVTR
PIN_UART0_TX = 1
PIN_UART0_RX = 3

# interface 6 GVDC
PIN_I2C_SDA = 21
PIN_I2C_SCL = 15

# interface 1
PIN_BOTTOM_1 = 33
# interface 2
PIN_BOTTOM_2 = 32
# interface 3
PIN_BOTTOM_3 = 26
# interface 4
PIN_BOTTOM_4 = 25

KEY_MAP = {
    "a":      PIN_BTN_A,
    "b":      PIN_BTN_B,
    "up":     PIN_BTN_UP,
    "down":   PIN_BTN_DOWN,
    "left":   PIN_BTN_LEFT,
    "right":  PIN_BTN_RIGHT,
}

# Color definitions
COLOR_BLACK   = 0x0000
COLOR_BLUE    = 0x001F
COLOR_RED     = 0xF800
COLOR_GREEN   = 0x07E0
COLOR_CYAN    = 0x07FF
COLOR_MAGENTA = 0xF81F
COLOR_YELLOW  = 0xFFE0
COLOR_WHITE   = 0xFFFF

FONT = "/lib/text_lite_16px_2312.v3.bmf"
