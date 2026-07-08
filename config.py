
class Config:
    def __init__(self):
        self.rezim = "simulator"
        self.sim_type = "sinus"
        self.ads_channels = ["A1"]
        self.ads_gain = "1x (±4.096V)"
        self.rolling_window = 60
        self.bpm_low_alarm = 8
        self.bpm_high_alarm = 40
        self.signal_std_threshold_low = 0.02
        self.signal_std_threshold_high = 2.0
