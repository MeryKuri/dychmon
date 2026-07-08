
import os
import datetime

class Meranie:
    def __init__(self, sensor, ads_channels=None):
        self.sensor = sensor
        self.ads_channels = ads_channels
        self.start_time = datetime.datetime.now()
        self.data_x = []
        self.data_y = []

    def zaznamenaj(self):
        elapsed = (datetime.datetime.now() - self.start_time).total_seconds()        
        hodnoty = self.sensor.read()   # toto je list: [v0, v1] alebo [v0]

        v0 = hodnoty[0] if isinstance(hodnoty, list) and len(hodnoty) > 0 else float(hodnoty)
        v1 = hodnoty[1] if isinstance(hodnoty, list) and len(hodnoty) > 1 else None
        
        if not isinstance(hodnoty, (list, tuple)):
            hodnoty = [hodnoty]
        self.data_x.append(elapsed)
        self.data_y.append(hodnoty)
        return elapsed, hodnoty

    def uloz(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            if self.ads_channels:
                header = "cas_s," + ",".join(self.ads_channels)
            else:
                header = "cas_s,hodnota"
            f.write(header + "\n")
            for t, values in zip(self.data_x, self.data_y):
                if not isinstance(values, (list, tuple)):
                    values = [values]
                line = f"{t}," + ",".join(f"{v:.5f}" for v in values)
                f.write(line + "\n")
