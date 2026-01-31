import os
import time
import json
import threading
import customtkinter as ctk
from PIL import Image, ImageTk
import urllib.request
import io

# --- IMPORTY TWOICH MODUŁÓW ---
try:
    import fortnite_stats
    import unreal_tracker
except ImportError:
    class MockAPI:
        @staticmethod
        def sprawdz_staty_gracza(name): return "fake_id_999"
        @staticmethod
        def pobierz_unreal_data(id): return {"ranga": "Unreal", "miejsce": "15"}
    fortnite_stats = MockAPI()
    unreal_tracker = MockAPI()

RANK_COLORS = {
    "unreal": "#b042ff", "champion": "#ff6d00", "elite": "#c0c0c0",
    "diamond": "#00b0ff", "platinum": "#00e5ff", "gold": "#ffd600",
    "silver": "#cfd8dc", "bronze": "#cd7f32", "unranked": "#888888"
}

RANK_HIERARCHY = {
    "unreal": 100, "champion": 80, "elite": 70, "diamond 3": 63, "diamond 2": 62, "diamond 1": 61,
    "platinum 3": 53, "platinum 2": 52, "platinum 1": 51, "gold 3": 43, "gold 2": 42, "gold 1": 41,
    "silver 3": 33, "silver 2": 32, "silver 1": 31, "bronze 3": 23, "bronze 2": 22, "bronze 1": 21,
    "unranked": 0, "n/a": -1
}





class SzkieletTrackerFinal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SZKIELET TRACKER PRO V8.7")
        self.geometry("1200x850")
        ctk.set_appearance_mode("dark")

        self.log_path = os.path.expandvars(r'%LOCALAPPDATA%\FortniteGame\Saved\Logs\FortniteGame.log')
        self.BOSS_BLACKLIST = ["Cisza", "Plażowy Brutus", "Człowiek Ziutek", "None", "NONE", "Anonymous", "Player"]
        
        self.all_players_data = []
        self.private_count = 0
        self.total_scanned = 0
        self.success_count = 0
        
        self.setup_ui()

    def get_rank_color(self, ranga):
        r = str(ranga).lower()
        for rank, color in RANK_COLORS.items():
            if rank in r: return color
        return "#3b8ed0"

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#0f0f0f")
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="SZKIELET", font=("Impact", 40), text_color="#3b8ed0").pack(pady=(30, 0))
        ctk.CTkLabel(self.sidebar, text="TRACKER", font=("Impact", 40), text_color="#9bc8ec").pack(pady=(0, 20))
        
        self.btn_start = ctk.CTkButton(self.sidebar, text="🚀 URUCHOM TRACKER", command=self.start_tracking, height=45, font=("Segoe UI", 14, "bold"))
        self.btn_start.pack(pady=10, padx=20)

        self.lbl_total = ctk.CTkLabel(self.sidebar, text="🔍 SKAN: 0", font=("Segoe UI", 15, "bold"), text_color="#3b8ed0")
        self.lbl_total.pack(pady=(20, 5))
        
        self.lbl_private = ctk.CTkLabel(self.sidebar, text="🔒 PRYWATNE: 0", font=("Segoe UI", 15, "bold"), text_color="#ff4b4b")
        self.lbl_private.pack(pady=5)

        self.lbl_success = ctk.CTkLabel(self.sidebar, text="✅ POBRANE: 0", font=("Segoe UI", 15, "bold"), text_color="#2ecc71")
        self.lbl_success.pack(pady=5)

        # --- STATUS BAR ---
        self.status_bar = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color="#000000")
        self.status_bar.grid(row=1, column=1, sticky="ew")
        self.status_text = ctk.CTkLabel(self.status_bar, text="🟢 STATUS: GOTOWY", font=("Consolas", 12), text_color="#888888")
        self.status_text.pack(side="left", padx=20)

        # --- MAIN CONTAINER ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        self.grid_view = ctk.CTkScrollableFrame(self.main_container, label_text="LOBBY", label_text_color="#9bc8ec")
        self.grid_view.pack(fill="both", expand=True)
        self.grid_view.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")

        self.details_view = ctk.CTkFrame(self.main_container, fg_color="#0a0a0a", corner_radius=20, border_width=1, border_color="#333333")

    def set_status(self, text, color="#888888"):
        self.status_text.configure(text=f"📡 {text.upper()}", text_color=color)

    def show_player_details(self, p):
        self.grid_view.pack_forget()
        self.details_view.pack(fill="both", expand=True, padx=20, pady=20)
        for w in self.details_view.winfo_children(): w.destroy()

        r_color = self.get_rank_color(p['ranga'])
        
        # Przycisk powrotu
        ctk.CTkButton(self.details_view, text="❌ Zamknij", font=("Segoe UI", 13, "bold"), 
                      width=180, height=35, command=self.show_grid, fg_color="#222222", hover_color="#333333").pack(anchor="nw", padx=30, pady=10)

        # Główny kontener karty
        card_panel = ctk.CTkFrame(self.details_view, fg_color="#0f0f0f", corner_radius=25, border_width=3, border_color=r_color)
        card_panel.pack(fill="both", expand=True, padx=30, pady=15)

       

        # GIGANTYCZNY NICK (pod zdjęciem)
        ctk.CTkLabel(card_panel, text=f"👤 {p['nick']}", font=("Impact", 55), text_color=r_color).pack(pady=(5, 10))
        
        # ID (klikane do kopiowania)
        id_label = ctk.CTkLabel(card_panel, text=f"ID: {p['id']}", font=("Consolas", 14), text_color="#555555", cursor="hand2")
        id_label.pack(pady=(0, 20))
        
        def copy_id(event):
            self.clipboard_clear()
            self.clipboard_append(str(p['id']))
            self.update()
            self.set_status("ACCOUNT ID SKOPIOWANE!", r_color)
        id_label.bind("<Button-1>", copy_id)

        s_frame = ctk.CTkScrollableFrame(card_panel, fg_color="transparent")
        s_frame.pack(fill="both", expand=True, padx=50, pady=10)

        # --- DEFINICJA FUNKCJI (ZMIENIONA NAZWA) ---
        def add_stat_row(icon, label, value, val_color="#ffffff"):
            row = ctk.CTkFrame(s_frame, fg_color="transparent")
            row.pack(fill="x", pady=8)
            ctk.CTkLabel(row, text=f"{icon} {label}", font=("Segoe UI", 20, "bold"), text_color="#aaaaaa", width=250, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value), font=("Consolas", 24, "bold"), text_color=val_color).pack(side="left")

        def add_separator():
            ctk.CTkFrame(s_frame, height=3, fg_color=r_color).pack(fill="x", pady=20)

        # --- SEKCJA 1: OGÓLNE ---
        add_stat_row("🎖️", "LEVEL KARNETU:", p.get('bp_level', '217'), "#f1c40f")
        add_stat_row("⏳", "CZAS W GRZE:", f"{p.get('hours', '887')}h", "#3498db")
        
        add_separator()

        # --- SEKCJA 2: WALKA ---
        k_val = float(p.get('kd_kbm', 0))
        k_color = "#2ecc71" if k_val >= 2.0 else "#f1c40f" if k_val >= 1.0 else "#e74c3c"
        add_stat_row("⌨️", "K/D MYSZKA:", p.get('kd_kbm', '0.0'), k_color)
        add_stat_row("🎮", "K/D PAD:", p.get('kd_pad', '0.0'), "#f1c40f")
        
        add_separator()

        # --- SEKCJA 3: SKUTECZNOŚĆ ---
        wr_val = float(str(p.get('winrate', '0')).replace('%', ''))
        wr_color = "#2ecc71" if wr_val >= 10 else "#f1c40f"
        add_stat_row("📈", "WIN RATE:", f"{wr_val}%", wr_color)
        add_stat_row("👑", "WYGRANE:", p.get('wins', '0'), "#f1c40f")
        add_stat_row("🏟️", "MECZE:", p.get('matches', '0'), "#ffffff")
        
        add_separator()

        # --- SEKCJA 4: RANGA ---
        miejsce = f"#{p['miejsce']}" if str(p['miejsce']) != "N/A" else "Poza Top"
        add_stat_row("🏆", "AKTUALNA RANGA:", p['ranga'].upper(), r_color)
        add_stat_row("📍", "RANKING GLOBAL:", miejsce, r_color)
        
        # Pusty margines na dole
        ctk.CTkLabel(s_frame, text="", height=20).pack()

        
    def show_grid(self):
        self.details_view.pack_forget()
        self.grid_view.pack(fill="both", expand=True)

    def sort_and_refresh_ui(self):
        def sort_key(p):
            r_name = str(p['ranga']).lower()
            base = RANK_HIERARCHY.get(r_name, 0)
            if "unreal" in r_name:
                try: return (base, -int(p['miejsce']))
                except: return (base, -999999)
            return (base, 0)

        sorted_list = sorted(self.all_players_data, key=sort_key, reverse=True)
        for w in self.grid_view.winfo_children(): w.destroy()
        for index, p in enumerate(sorted_list):
            r_color = self.get_rank_color(p['ranga'])
            card = ctk.CTkFrame(self.grid_view, fg_color="#181818", corner_radius=12, border_width=2, border_color=r_color, cursor="hand2")
            card.grid(row=index//3, column=index%3, padx=10, pady=10, sticky="nsew")
            cb = lambda e, player=p: self.show_player_details(player)
            card.bind("<Button-1>", cb)
            n_lbl = ctk.CTkLabel(card, text=f"👤 {p['nick']}", font=("Segoe UI", 14, "bold"))
            n_lbl.pack(pady=(15, 5))
            n_lbl.bind("<Button-1>", cb)
            m_txt = f" #{p['miejsce']}" if str(p['miejsce']) != "N/A" else ""
            r_lbl = ctk.CTkLabel(card, text=f"{str(p['ranga']).upper()}{m_txt}", fg_color=r_color, corner_radius=6, font=("Segoe UI", 11, "bold"), height=30)
            r_lbl.pack(pady=(0, 15), padx=15, fill="x")
            r_lbl.bind("<Button-1>", cb)

    def start_tracking(self):
        self.btn_start.configure(state="disabled", text="⚡ AKTYWNY")
        # Fake PRO Player do testów
        fake_p = {
            "nick": "PRO_SKELETON", "id": "fake_id_123", "ranga": "Unreal", 
            "miejsce": "1", "bp_level": "420", "hours": "3500", 
            "kd_kbm": "5.40", "kd_pad": "1.10", "winrate": "24.5", "wins": "850", "matches": "3469"
        }
        self.all_players_data.append(fake_p)
        self.total_scanned += 1
        self.success_count += 1
        self.update_counters()
        self.sort_and_refresh_ui()
        
        threading.Thread(target=self.engine, daemon=True).start()

    def update_counters(self):
        self.lbl_total.configure(text=f"🔍 SKAN: {self.total_scanned}")
        self.lbl_private.configure(text=f"🔒 PRYWATNE: {self.private_count}")
        self.lbl_success.configure(text=f"✅ POBRANE: {self.success_count}")

    def engine(self):
        if not os.path.exists(self.log_path):
            self.set_status("Błąd: Brak pliku logów!", "#ff4b4b")
            return
        self.set_status("Oczekiwanie na mecz...", "#3498db")
        known_nicks = set()
        in_warmup = False
        with open(self.log_path, 'rb') as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.01)
                    continue
                row = line.decode('utf-8', errors='ignore').strip()
                if "NewPhase = EAthenaGamePhase::Warmup" in row:
                    in_warmup = True
                    self.all_players_data = [self.all_players_data[0]] # Zostaw fake gracza
                    self.private_count = 0
                    self.total_scanned = 1
                    self.success_count = 1
                    self.after(0, self.update_counters)
                    self.after(0, self.sort_and_refresh_ui)
                    self.set_status("Skanowanie lobby...", "#2ecc71")
                if in_warmup and "LogPawnBoombox" in row and "song 'None'" in row:
                    parts = row.split("'")
                    if len(parts) > 1:
                        name = parts[1]
                        if name and name not in self.BOSS_BLACKLIST and name not in known_nicks:
                            known_nicks.add(name)
                            self.total_scanned += 1
                            self.set_status(f"Analizuję: {name}", "#f1c40f")
                            acc_id = fortnite_stats.sprawdz_staty_gracza(name)
                            if not acc_id:
                                self.private_count += 1
                                self.after(0, self.update_counters)
                                continue
                            r_info = unreal_tracker.pobierz_unreal_data(acc_id)
                            self.success_count += 1
                            self.after(0, self.update_counters)
                            
                            # TUTAJ PODEPNIJ REALNE DANE ZE SWOJEGO API fortnite_stats
                            p_data = {
                                "nick": name, "id": acc_id, "ranga": r_info.get('ranga', 'N/A'),
                                "miejsce": r_info.get('miejsce', 'N/A'), "bp_level": "217", 
                                "hours": "887", "kd_kbm": "1.4", "kd_pad": "0.7",
                                "winrate": "8.5", "wins": "120", "matches": "1400"
                            }
                            self.all_players_data.append(p_data)
                            self.after(0, self.sort_and_refresh_ui)

if __name__ == "__main__":
    app = SzkieletTrackerFinal()
    app.mainloop()