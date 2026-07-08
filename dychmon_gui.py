import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import datetime
import os
from config import Config
from meranie import Meranie
from sensors import DummySensor, ADS1115Sensor
from logger import Logger
from scipy.signal import find_peaks

class DychmonGUIv2:
    def __init__(self, master):       
        self.master = master
        self.master.title("DYCHMON v0.9.4.5+")
        self.cfg = Config()
        self.logger = Logger()

        # ADS1115 nastavenia (menu)
        self.ads_show_ch1_var = tk.BooleanVar(value=True)
        self.ads_show_ch2_var = tk.BooleanVar(value=True)
        self.ads_channel_var = tk.StringVar(value="A1")
        self.ads_channel2_var = tk.StringVar(value="A0")
        self.create_widgets()
        self.is_measuring = False
        self.after_id = None
        self.master.protocol("WM_DELETE_WINDOW", self.bezpecne_ukoncit)
                    
    def create_widgets(self):
        # MenuBar
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        nastavenia_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Nastavenia", menu=nastavenia_menu)
        self.nastavenia_menu = nastavenia_menu
        nastavenia_menu.add_command(label="Nastavenia Alarmov", command=self.open_alarm_settings)
        
        # --- ADS1115 nastavenia ---
        ads_menu = tk.Menu(nastavenia_menu, tearoff=0)
        nastavenia_menu.add_cascade(label="ADS1115", menu=ads_menu)
        self.ads_cascade_index = self.nastavenia_menu.index("end")  # index položky ADS1115 v Nastaveniach

        ads_menu.add_checkbutton(
            label="Zobraziť kanál 1",
            variable=self.ads_show_ch1_var,
            command=self.on_ads_settings_changed
        )
        ads_menu.add_checkbutton(
            label="Zobraziť kanál 2",
            variable=self.ads_show_ch2_var,
            command=self.on_ads_settings_changed
        )

        ads_menu.add_separator()

        kanal1_menu = tk.Menu(ads_menu, tearoff=0)
        ads_menu.add_cascade(label="Kanál 1", menu=kanal1_menu)
        for ch in ["A0", "A1", "A2", "A3"]:
            kanal1_menu.add_radiobutton(
                label=ch,
                variable=self.ads_channel_var,
                value=ch,
                command=self.on_ads_settings_changed
            )

        kanal2_menu = tk.Menu(ads_menu, tearoff=0)
        ads_menu.add_cascade(label="Kanál 2", menu=kanal2_menu)
        for ch in ["A0", "A1", "A2", "A3"]:
            kanal2_menu.add_radiobutton(
                label=ch,
                variable=self.ads_channel2_var,
                value=ch,
                command=self.on_ads_settings_changed
            )
                
        nastavenia_menu.add_separator()
        nastavenia_menu.add_command(label="Ukončiť program", command=self.bezpecne_ukoncit)
        
        pomoc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Pomoc", menu=pomoc_menu)
        pomoc_menu.add_command(label="O programe", command=self.o_programme)

        # Režim merania
        top_frame = tk.Frame(self.master)
        top_frame.pack()

        self.rezim_var = tk.StringVar(value="simulator")
        tk.Radiobutton(top_frame, text="Simulátor", variable=self.rezim_var, value="simulator").pack(side=tk.LEFT)
        tk.Radiobutton(top_frame, text="ADS1115", variable=self.rezim_var, value="real").pack(side=tk.LEFT)

        self.sim_combo = ttk.Combobox(top_frame, values=["sinus", "sum", "kvadraticky"])
        self.sim_combo.set("sinus")
        self.sim_combo.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(top_frame, text="Spustiť", command=self.toggle_meranie)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.export_button = tk.Button(top_frame, text="Export", command=self.exportuj, state="disabled")
        self.export_button.pack(side=tk.LEFT, padx=5)

        self.log_text = scrolledtext.ScrolledText(self.master, height=8, state="disabled")
        self.log_text.pack(fill=tk.X, padx=5, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack()

        self.bpm_label = tk.Label(self.master, text="Realtime BPM: --", font=("Arial", 10))
        self.bpm_label.pack(pady=5)

        self.signal_label = tk.Label(self.master, text="Signal Quality: --", font=("Arial", 10))
        self.signal_label.pack(pady=5)
    
    def bezpecne_ukoncit(self):
        try:
            # zabráň ďalším plánovaným after() callbackom
            self.is_measuring = False
                       
            # ak máš uložené after id, zruš ho (iba ak existuje)
            if hasattr(self, "after_id") and self.after_id:
                try:
                    self.master.after_cancel(self.after_id)
                except Exception:
                    pass
                self.after_id = None

            # ak existuje senzor, pokús sa ho zavrieť
            if hasattr(self, "sensor") and self.sensor:
                if hasattr(self.sensor, "i2c") and self.sensor.i2c:
                    try:
                        self.sensor.i2c.deinit()
                    except Exception:
                        pass

            print("DYCHMON bezpečne ukončený.")

        except Exception as e:
            print("Chyba pri ukončovaní:", e)
        try:
            plt.close(self.fig)
        except Exception:
            pass
        self.master.destroy()
    
    def toggle_meranie(self):
        if not self.is_measuring:
            self.start_button.config(text="Stop")
            self.set_ads_menu_locked(True)
            self.spusti_meranie()
        else:
            self.is_measuring = False
            self.start_button.config(text="Spustiť")
            self.export_button.config(state="normal")
            self.log("Meranie ukončené.")
            self.set_ads_menu_locked(False)
    
    def set_ads_menu_locked(self, locked: bool):
        # ak menu ešte neexistuje (teoreticky), nič nerob
        if not hasattr(self, "nastavenia_menu") or not hasattr(self, "ads_cascade_index"):
            return

        state = "disabled" if locked else "normal"
        self.nastavenia_menu.entryconfig(self.ads_cascade_index, state=state)

        # vizuálny signál – titulok okna
        base = "DYCHMON v0.9.4.5+"
        if locked:
            self.master.title(base + "  [MERANIE – nastavenia uzamknuté]")
        else:
            self.master.title(base)

    def spusti_meranie(self):
        if self.rezim_var.get() == "simulator":
            self.sensor = DummySensor(self.sim_combo.get())
            self.meranie = Meranie(self.sensor, ads_channels=["Sim"])
        else:
            ch1 = self.ads_channel_var.get()
            ch2 = self.ads_channel2_var.get()
            show1 = self.ads_show_ch1_var.get()
            show2 = self.ads_show_ch2_var.get()

            channels = []
            if show1:
                channels.append(ch1)
            if show2:
                channels.append(ch2)

            # poistka: aspoň jeden kanál musí byť zapnutý
            if not channels:
                channels = [ch1]
                self.ads_show_ch1_var.set(True)
            self.sensor = ADS1115Sensor(channels, self.cfg.ads_gain)
            self.sensor.initialize()
            self.meranie = Meranie(self.sensor, ads_channels=channels)

        self.is_measuring = True
        self.update_meranie()

    def update_meranie(self):
        if not self.is_measuring:
            return
        elapsed, hodnoty = self.meranie.zaznamenaj()
        self.redraw_plot()
        self.update_bpm()
        self.update_signal_quality()
        self.after_id = self.master.after(200, self.update_meranie)

    def redraw_plot(self):
        self.ax.clear()
        if not self.meranie.data_x:
            return
        window_x = self.meranie.data_x[-self.cfg.rolling_window:]
        window_y = self.meranie.data_y[-self.cfg.rolling_window:]

        if not isinstance(window_y[0], (list, tuple)):
            window_y = [[y] for y in window_y]

        num_channels = len(self.meranie.ads_channels) if self.rezim_var.get() == "real" else len(window_y[0])
        
        for ch_idx in range(num_channels):
            channel_y = [y[ch_idx] for y in window_y if len(y) > ch_idx]
            label = self.meranie.ads_channels[ch_idx] if (self.rezim_var.get() == "real" and self.meranie.ads_channels) else "Sim"
            # ak pre tento kanál nie sú dáta, neplotuj ho
            if not channel_y:
                continue

            # X musí mať rovnakú dĺžku ako Y
            x = window_x[-len(channel_y):]
            self.ax.plot(x, channel_y, label=label)

        self.ax.legend()
        self.ax.grid()
        self.canvas.draw()

    def update_bpm(self):
        if not self.meranie.data_x:
            return

        window_x = self.meranie.data_x[-self.cfg.rolling_window:]
        window_y = self.meranie.data_y[-self.cfg.rolling_window:]

        if not isinstance(window_y[0], (list, tuple)):
            window_y = [[y] for y in window_y]

        num_channels = len(self.meranie.ads_channels) if self.rezim_var.get() == "real" else len(window_y[0])
        bpm_values = []

        for ch_idx in range(num_channels):
            label = self.meranie.ads_channels[ch_idx] if (self.rezim_var.get() == "real" and self.meranie.ads_channels) else "Sim"            
            
            channel_y = [y[ch_idx] for y in window_y if len(y) > ch_idx]
            if len(channel_y) > 5:
                peaks, _ = find_peaks(channel_y, distance=5, prominence=0.1)
                duration = window_x[-1] - window_x[0] if window_x[-1] > window_x[0] else 1
                bpm = (len(peaks) / duration) * 60 if duration > 0 else 0

                alarm = ""
                if bpm < self.cfg.bpm_low_alarm or bpm > self.cfg.bpm_high_alarm:
                    alarm = " ⚠"
                bpm_values.append(f"{label}: {bpm:.1f} bpm{alarm}")
            else:
                bpm_values.append(f"{label}: -- bpm")

        self.bpm_label.config(text="Realtime BPM: " + ", ".join(bpm_values))

    def update_signal_quality(self):
        if not self.meranie.data_x:
            return

        window_y = self.meranie.data_y[-self.cfg.rolling_window:]
        if not isinstance(window_y[0], (list, tuple)):
            window_y = [[y] for y in window_y]

        num_channels = len(self.meranie.ads_channels) if self.rezim_var.get() == "real" else len(window_y[0])
        quality_values = []

        for ch_idx in range(num_channels):
            channel_y = [y[ch_idx] for y in window_y if len(y) > ch_idx]
            if len(channel_y) > 5:
                std = np.std(channel_y)
                if std < self.cfg.signal_std_threshold_low:
                    quality = "No Signal ⚠"
                elif std > self.cfg.signal_std_threshold_high:
                    quality = "Noisy ⚠"
                else:
                    quality = "OK"
            else:
                quality = "--"
            label = self.meranie.ads_channels[ch_idx] if (self.rezim_var.get() == "real" and self.meranie.ads_channels) else "Sim"
            quality_values.append(f"{label}: {quality}")

        self.signal_label.config(text="Signal Quality: " + ", ".join(quality_values))

    def exportuj(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(folder, f"meranie_{timestamp}.csv")
        self.meranie.uloz(filename)
        self.log(f"Export hotový: {filename}")

    def log(self, msg):
        self.logger.log(msg)
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def open_alarm_settings(self):
        win = tk.Toplevel(self.master)
        win.title("Nastavenia Alarmov")
        win.grab_set()

        tk.Label(win, text="Dolná hranica BPM:").grid(row=0, column=0, padx=5, pady=5)
        bpm_low_entry = tk.Entry(win)
        bpm_low_entry.insert(0, str(self.cfg.bpm_low_alarm))
        bpm_low_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(win, text="Horná hranica BPM:").grid(row=1, column=0, padx=5, pady=5)
        bpm_high_entry = tk.Entry(win)
        bpm_high_entry.insert(0, str(self.cfg.bpm_high_alarm))
        bpm_high_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(win, text="STD low (No Signal):").grid(row=2, column=0, padx=5, pady=5)
        std_low_entry = tk.Entry(win)
        std_low_entry.insert(0, str(self.cfg.signal_std_threshold_low))
        std_low_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(win, text="STD high (Noisy):").grid(row=3, column=0, padx=5, pady=5)
        std_high_entry = tk.Entry(win)
        std_high_entry.insert(0, str(self.cfg.signal_std_threshold_high))
        std_high_entry.grid(row=3, column=1, padx=5, pady=5)
        
        def uloz():
            try:
                self.cfg.bpm_low_alarm = float(bpm_low_entry.get())
                self.cfg.bpm_high_alarm = float(bpm_high_entry.get())
                self.cfg.signal_std_threshold_low = float(std_low_entry.get())
                self.cfg.signal_std_threshold_high = float(std_high_entry.get())
                self.log("Hodnoty alarmov aktualizované.")
                win.destroy()
            except ValueError:
                messagebox.showerror("Chyba", "Zadaj platné čísla.")

        tk.Button(win, text="Uložiť", command=uloz).grid(row=4, column=0, columnspan=2, pady=10)
        
    def on_ads_settings_changed(self):
        if getattr(self, "is_measuring", False):
            self.log("Nastavenia ADS sú počas merania uzamknuté.")
            return
        show1 = self.ads_show_ch1_var.get()
        show2 = self.ads_show_ch2_var.get()
        ch1 = self.ads_channel_var.get()
        ch2 = self.ads_channel2_var.get()

        channels = []
        if show1:
            channels.append(ch1)
        if show2:
            channels.append(ch2)

        # poistka: aspoň jeden kanál musí byť zapnutý
        if not channels:
            channels = [ch1]
            self.ads_show_ch1_var.set(True)
        
        self.log(f"ADS1115 nastavenie: channels={channels}")

        # ak práve meriame v ADS režime, prepni senzor okamžite
        if getattr(self, "is_measuring", False) and self.rezim_var.get() == "real":
            try:
                self.sensor = ADS1115Sensor(channels, self.cfg.ads_gain)
                self.sensor.initialize()

                # DÔLEŽITÉ: meranie musí čítať z nového senzora
                self.meranie.sensor = self.sensor
                self.meranie.ads_channels = channels

                # pri zmene počtu kanálov za behu vyčisti buffer
                self.meranie.data_x.clear()
                self.meranie.data_y.clear()

                self.log(f"ADS1115 prepnuté počas merania: {channels}")
            except Exception as e:
                self.log(f"Chyba pri prepnutí ADS nastavenia: {e}")

    def o_programme(self):
        messagebox.showinfo("O programe", "DYCHMON v0.9.4.5+\nMultikanálový dychový monitor")
        
# Spustenie programu
if __name__ == "__main__":
    root = tk.Tk()
    app = DychmonGUIv2(root)
    root.mainloop()

