import const
import machine
import st7735_buf
import time, math
import lib.easydisplay as easydisplay

class TemperatureSensor():
    R1 = 10000      # 热敏电阻串联的固定阻值
    B = 3950        # B值
    T0 = 298.15     # 参考温度 25度
    R0 = 10000      # 参考温度时热敏电阻阻值

    def __init__(self, adc_pin=const.PIN_TEMP_SENSOR):
        self.pin = machine.ADC(machine.Pin(adc_pin))
        self.pin.atten(machine.ADC.ATTN_11DB) # 0-3.6V量程

    def value(self):
        adc_value = self.pin.read()
        voltage = adc_value * (3.3 / 4095)
        resistance = TemperatureSensor.R1 * voltage / (3.3 - voltage)
        temperature = 1 / (math.log(resistance / TemperatureSensor.R0) / TemperatureSensor.B + 1 / TemperatureSensor.T0) - 273.15
        return round(temperature, 1)

class Speaker():
    def __init__(self, pwm_pin=const.PIN_SPEAKER):
        self.pin = machine.PWM(machine.Pin(pwm_pin))
        self.pin.duty(0)

    def beep(self, freq, duration_in_ms):
        self.pin.freq(freq)
        self.pin.duty(512)
        time.sleep_ms(duration_in_ms)
        self.pin.duty(0)

class LightSensor():
    def __init__(self, adc_pin=const.PIN_LIGHT_SENSOR):
        self.pin = machine.ADC(machine.Pin(adc_pin))
        self.pin.atten(machine.ADC.ATTN_11DB) # 0-3.6V量程

    def value(self):
        return self.pin.read()

# ST7735
def new_easydisplay(color=const.COLOR_WHITE, show=True, clear=True, font=const.FONT):
    """
    create easydisplay instance
    """
    print('--- font', font)
    spi = machine.SPI(2, baudrate=20000000, polarity=0, phase=0, sck=machine.Pin(const.PIN_TFT_SCK), mosi=machine.Pin(const.PIN_TFT_MOSI))

    dp = st7735_buf.ST7735(width=const.SCREEN_WIDTH, height=const.SCREEN_HEIGHT, 
                           spi=spi, cs=const.PIN_TFT_CS, dc=const.PIN_TFT_DC, res=const.PIN_TFT_RES, 
                           rotate=1, bl=None, invert=False, rgb=False)

    ed = easydisplay.EasyDisplay(display=dp, color_type="RGB565", font=font, show=show, color=color, clear=clear)

    return ed
