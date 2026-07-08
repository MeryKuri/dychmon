
import time
import numpy as np
import platform

if platform.system() != "Windows":
    import board
    import busio
    from adafruit_ads1x15.analog_in import AnalogIn
    from adafruit_ads1x15.ads1115 import ADS1115
else:
    ADS1115 = None
    board = None
    busio = None
    AnalogIn = None
    
class DummySensor:
    def __init__(self, sim_type="sinus"):
        self.start_time = time.time()
        self.sim_type = sim_type

    def read(self):
        elapsed = time.time() - self.start_time
        if self.sim_type == "sinus":
            return np.sin(elapsed * 2 * np.pi * 0.25)
        elif self.sim_type == "sum":
            return np.random.normal(0, 0.3)
        elif self.sim_type == "kvadraticky":
            return (elapsed % 4) - 2
        else:
            return 0.0

class ADS1115Sensor:
    CHANNEL_MAP = {"A0": 0, "A1": 1, "A2": 2, "A3": 3}
    GAIN_MAP = {"2/3x (±6.144V)": 2/3, "1x (±4.096V)": 1, "2x (±2.048V)": 2,
        "4x (±1.024V)": 4, "8x (±0.512V)": 8, "16x (±0.256V)": 16}

    def __init__(self, channels=["A1"], gain="1x (±4.096V)"):
        self.i2c = None
        self.ads = None
        self.channels = channels
        if isinstance(self.channels, str):
            self.channels = [self.channels]
        self.gain_str = gain
        self.analog_channels = []

    def initialize(self):
        if ADS1115 is None:
            raise NotImplementedError("ADS1115 nie je podporovaný na Windows. Použi DummySensor.")
        
        if self.ads is not None and self.analog_channels:
            return
        
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS1115(self.i2c)
        self.ads.gain = self.GAIN_MAP[self.gain_str]
        self.analog_channels = [
            AnalogIn(self.ads, self.CHANNEL_MAP[ch]) for ch in self.channels
        ]
    def read(self):
        if not self.analog_channels:
            self.initialize()
        return [ch.voltage for ch in self.analog_channels]
    def close(self):
        try:
            if self.i2c:
                self.i2c.deinit()
        except Exception:
            pass
        self.i2c = None
        self.ads = None
        self.analog_channels = []
