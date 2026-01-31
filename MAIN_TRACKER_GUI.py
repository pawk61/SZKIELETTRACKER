import os
import time
import threading
import queue
import customtkinter as ctk
import requests
from dotenv import load_dotenv

# --- KONFIGURACJA ---
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, "api.env"))
API_KEY = "c372c472-eefb-46aa-ab69-d4739690c0f8" 

try:
    import fortnite_stats
    import unreal_tracker
except ImportError:
    print("🚨 Nie znaleziono modułów!")

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
        self.title("SZKIELET TRACKER PRO V10.0")
        self.geometry("1200x850")
        ctk.set_appearance_mode("dark")

        self.log_path = os.path.expandvars(r'%LOCALAPPDATA%\FortniteGame\Saved\Logs\FortniteGame.log')
        self.BOSS_BLACKLIST = ["Cisza", "Plażowy Brutus", "Człowiek Ziutek", "None", "NONE", "Anonymous", "Player"]
        
        self.all_players_data = []
        self.known_nicks = set()
        self.private_count = 0
        self.total_scanned = 0
        self.success_count = 0
        
        self.player_queue = queue.Queue()
        threading.Thread(target=self.queue_worker, daemon=True).start()
        
        self.setup_ui()
        threading.Thread(target=self.simulate_on_start, daemon=True).start()

    def get_rank_color(self, ranga):
        r = str(ranga).lower()
        for rank, color in RANK_COLORS.items():
            if rank in r: return color
        return "#3b8ed0"

    def pobierz_staty_naprawione(self, nick):
        url = "https://fortnite-api.com/v2/stats/br/v2"
        headers = {"Authorization": API_KEY}
        params = {"name": nick.strip(), "timeWindow": "lifetime"}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                json_data = resp.json()
                d = json_data['data']
                overall = d.get('stats', {}).get('all', {}).get('overall', {})
                
                raw_date = overall.get('lastModified', 'N/A')
                clean_date = "N/A"
                if raw_date != 'N/A':
                    try:
                        date_part = raw_date.split('T')[0]
                        time_part = raw_date.split('T')[1][:5]
                        clean_date = f"{date_part} {time_part}"
                    except: clean_date = raw_date

                def get_kd(input_type):
                    dev = d.get('stats', {}).get(input_type, {})
                    if not dev: return 0.0
                    try:
                        s = dev.get('solo', {}).get('kd', 0)
                        du = dev.get('duo', {}).get('kd', 0)
                        sq = dev.get('squad', {}).get('kd', 0)
                        return round((s + du + sq) / 3, 2)
                    except: return 0.0

                return {
                    "id": d.get('account', {}).get('id'),
                    "bp_level": d.get('battlePass', {}).get('level', 0),
                    "wins": overall.get('wins', 0),
                    "winrate": overall.get('winRate', 0),
                    "hours": round(overall.get('minutesPlayed', 0) / 60, 1),
                    "kd_kbm": get_kd('keyboardMouse'),
                    "kd_pad": get_kd('gamepad'),
                    "last_modified": clean_date
                }
        except: pass
        return None

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0f0f0f")
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.pack_propagate(False)
        
        ctk.CTkLabel(self.sidebar, text="SZKIELET", font=("Impact", 40), text_color="#3b8ed0").pack(pady=(30, 0))
        ctk.CTkLabel(self.sidebar, text="TRACKER", font=("Impact", 40), text_color="#9bc8ec").pack(pady=(0, 20))
        
        search_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        search_header.pack(pady=(10, 0), padx=20, fill="x")
        ctk.CTkLabel(search_header, text="🔍 PODGLĄD:", font=("Segoe UI", 12, "bold"), text_color="#aaaaaa").pack(side="left")
        self.search_error_lbl = ctk.CTkLabel(search_header, text="", font=("Segoe UI", 10), text_color="#ff4b4b")
        self.search_error_lbl.pack(side="right")

        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Nick...", height=35)
        self.search_entry.pack(pady=5, padx=20, fill="x")
        self.search_entry.bind("<Return>", lambda e: self.search_and_open())
        
        self.btn_search = ctk.CTkButton(self.sidebar, text="WYSZUKAJ", command=self.search_and_open, height=35, fg_color="#3b8ed0")
        self.btn_search.pack(pady=5, padx=20, fill="x")

        ctk.CTkFrame(self.sidebar, height=2, fg_color="#222222").pack(pady=20, padx=20, fill="x")
        self.btn_start = ctk.CTkButton(self.sidebar, text="🚀 URUCHOM TRACKER", command=self.start_tracking, height=45, font=("Segoe UI", 14, "bold"))
        self.btn_start.pack(pady=10, padx=20)
        
        self.lbl_total = ctk.CTkLabel(self.sidebar, text="🔍 SKAN: 0", font=("Segoe UI", 15, "bold"), text_color="#3b8ed0")
        self.lbl_total.pack(pady=(20, 5))
        self.lbl_private = ctk.CTkLabel(self.sidebar, text="🔒 PRYWATNE: 0", font=("Segoe UI", 15, "bold"), text_color="#ff4b4b")
        self.lbl_private.pack(pady=5)
        self.lbl_success = ctk.CTkLabel(self.sidebar, text="✅ POBRANE: 0", font=("Segoe UI", 15, "bold"), text_color="#2ecc71")
        self.lbl_success.pack(pady=5)

        # --- OSTATNIA AKTUALIZACJA NA DOLE SIDEBARA ---
        self.api_time_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.api_time_frame.pack(side="bottom", pady=20)
        ctk.CTkLabel(self.api_time_frame, text="OSTATNIE DANE Z API:", font=("Segoe UI", 10, "bold"), text_color="#555555").pack()
        self.lbl_api_time = ctk.CTkLabel(self.api_time_frame, text="BRAK DANYCH", font=("Consolas", 11), text_color="#888888")
        self.lbl_api_time.pack(pady=2)

        # --- MAIN ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        self.grid_view = ctk.CTkScrollableFrame(self.main_container, label_text="LOBBY LIVE", label_text_color="#9bc8ec")
        self.grid_view.pack(fill="both", expand=True)
        self.grid_view.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")
        
        self.details_view = ctk.CTkFrame(self.main_container, fg_color="#0a0a0a", corner_radius=20, border_width=1, border_color="#333333")

        self.status_bar = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color="#000000")
        self.status_bar.grid(row=1, column=1, sticky="ew")
        self.status_text = ctk.CTkLabel(self.status_bar, text="🟢 STATUS: GOTOWY", font=("Consolas", 12), text_color="#12AD46")
        self.status_text.pack(side="left", padx=20)

    def copy_to_clipboard(self, text, label):
        self.clipboard_clear()
        self.clipboard_append(text)
        original_text = label.cget("text")
        label.configure(text="COPIED!", text_color="#2ecc71")
        self.after(1000, lambda: label.configure(text=original_text, text_color="#555555"))

    def show_player_details(self, p):
        self.grid_view.pack_forget()
        self.details_view.pack(fill="both", expand=True, padx=20, pady=20)
        for w in self.details_view.winfo_children(): w.destroy()
        
        r_color = self.get_rank_color(p['ranga'])
        ctk.CTkButton(self.details_view, text="❌ ZAMKNIJ", command=self.show_grid, fg_color="#222222").pack(anchor="nw", padx=30, pady=10)
        
        card = ctk.CTkFrame(self.details_view, fg_color="#0f0f0f", corner_radius=25, border_width=3, border_color=r_color)
        card.pack(fill="both", expand=True, padx=30, pady=15)
        
        ctk.CTkLabel(card, text=f"👤 {p['nick']}", font=("Impact", 55), text_color=r_color).pack(pady=(20, 0))
        
        id_lbl = ctk.CTkLabel(card, text=f"ID: {p['id']}", font=("Consolas", 11), text_color="#555555", cursor="hand2")
        id_lbl.pack(pady=(0, 10))
        id_lbl.bind("<Button-1>", lambda e: self.copy_to_clipboard(p['id'], id_lbl))

        s_frame = ctk.CTkScrollableFrame(card, fg_color="transparent")
        s_frame.pack(fill="both", expand=True, padx=50, pady=10)
        
        def add_category_line(color):
            """Grubszy pasek oddzielający sekcje (kolor rangi)"""
            line = ctk.CTkFrame(s_frame, height=3, fg_color=color)
            line.pack(fill="x", pady=(15, 5), padx=10)

        def add_info_line():
            """Cienki, szary pasek między informacjami"""
            line = ctk.CTkFrame(s_frame, height=1, fg_color="#333333")
            line.pack(fill="x", pady=(2, 2), padx=30)

        def add_stat(icon, label, value, color="#ffffff"):
            row = ctk.CTkFrame(s_frame, fg_color="transparent")
            row.pack(fill="x", pady=6)
            # Ikona i tekst wyrównane do stałych szerokości
            ctk.CTkLabel(row, text=icon, font=("Segoe UI", 20), width=40, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 18, "bold"), text_color="#aaaaaa", width=200, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value), font=("Consolas", 22, "bold"), text_color=color).pack(side="left")

        # Przygotowanie danych rangi
        ranga_full = p['ranga'].upper()
        if "UNREAL" in ranga_full and str(p.get('miejsce', 'N/A')) != "N/A":
            ranga_display = f"{ranga_full} #{p['miejsce']}"
        else:
            ranga_display = ranga_full

        # --- SEKCJA 1: OGÓLNE ---
        add_category_line(r_color)
        add_stat("🎖️", "LEVEL KARNETU:", p.get('bp_level', '0'), "#f1c40f")
        add_info_line()
        add_stat("⏳", "CZAS W GRZE:", f"{p.get('hours', '0')}h", "#3498db")

        # --- SEKCJA 2: PERFORMANCE (Myszka/Pad) ---
        add_category_line(r_color)
        add_stat("⌨️", "K/D MYSZKA:", p.get('kd_kbm', '0.0'), "#2ecc71")
        add_info_line()
        add_stat("🎮", "K/D PAD:", p.get('kd_pad', '0.0'), "#f1c40f")

        # --- SEKCJA 3: WINRATE ---
        add_category_line(r_color)
        add_stat("👑", "WYGRANE:", p.get('wins', '0'), "#f1c40f")
        add_info_line()
        add_stat("📈", "WIN RATE:", f"{p.get('winrate', '0')}%", "#2ecc71")

        # --- SEKCJA 4: RANGA ---
        add_category_line(r_color)
        add_stat("🏆", "RANGA:", ranga_display, r_color)
        add_category_line(r_color)
        
        
        

    def show_grid(self):
        self.details_view.pack_forget()
        self.grid_view.pack(fill="both", expand=True)

    def set_status(self, text, color="#888888"):
        self.status_text.configure(text=f"📡 {text.upper()}", text_color=color)

    def set_search_error(self, text):
        self.search_error_lbl.configure(text=text)
        self.after(4000, lambda: self.search_error_lbl.configure(text=""))

    def search_and_open(self):
        nick = self.search_entry.get().strip()
        if not nick: return
        self.set_search_error("⌛ ...")
        
        def task():
            acc_data = self.pobierz_staty_naprawione(nick)
            if acc_data:
                r_info = unreal_tracker.pobierz_unreal_data(acc_data['id'])
                p_data = {
                    "nick": nick, "id": acc_data['id'], "ranga": r_info.get('ranga', 'Unranked'),
                    "miejsce": r_info.get('miejsce', 'N/A'), "bp_level": acc_data.get('bp_level', '0'),
                    "hours": acc_data.get('hours', '0'), "kd_kbm": acc_data.get('kd_kbm', '0.0'),
                    "kd_pad": acc_data.get('kd_pad', '0.0'), "winrate": acc_data.get('winrate', '0'),
                    "wins": acc_data.get('wins', '0'), "last_modified": acc_data.get('last_modified', 'N/A')
                }
                self.after(0, self.update_api_sidebar_time, p_data['last_modified'])
                self.after(0, self.show_player_details, p_data)
                self.after(0, lambda: self.search_entry.delete(0, 'end'))
                self.after(0, lambda: self.set_search_error("✅ OK"))
            else:
                self.after(0, lambda: self.set_search_error("❌ BŁĄD"))

        threading.Thread(target=task, daemon=True).start()

    def update_api_sidebar_time(self, t):
        self.lbl_api_time.configure(text=str(t), text_color="#3b8ed0")

    def sort_and_refresh_ui(self):
        sorted_list = sorted(self.all_players_data, key=lambda p: RANK_HIERARCHY.get(str(p['ranga']).lower(), 0), reverse=True)
        for w in self.grid_view.winfo_children(): w.destroy()
        for index, p in enumerate(sorted_list):
            r_color = self.get_rank_color(p['ranga'])
            card = ctk.CTkFrame(self.grid_view, fg_color="#181818", corner_radius=12, border_width=2, border_color=r_color)
            card.grid(row=index//3, column=index%3, padx=10, pady=10, sticky="nsew")
            
            lbl_nick = ctk.CTkLabel(card, text=f"👤 {p['nick']}", font=("Segoe UI", 14, "bold"))
            lbl_nick.pack(pady=(15, 5))
            
            m_txt = f" #{p['miejsce']}" if str(p['miejsce']) != "N/A" else ""
            lbl_rank = ctk.CTkLabel(card, text=f"{p['ranga'].upper()}{m_txt}", fg_color=r_color, corner_radius=6, font=("Segoe UI", 11, "bold"), height=30)
            lbl_rank.pack(pady=(0, 15), padx=15, fill="x")

            on_click = lambda e, player=p: self.show_player_details(player)
            card.bind("<Button-1>", on_click)
            lbl_nick.bind("<Button-1>", on_click)
            lbl_rank.bind("<Button-1>", on_click)

    def update_counters(self):
        self.lbl_total.configure(text=f"🔍 SKAN: {self.total_scanned}")
        self.lbl_private.configure(text=f"🔒 PRYWATNE: {self.private_count}")
        self.lbl_success.configure(text=f"✅ POBRANE: {self.success_count}")

    def queue_worker(self):
        while True:
            try:
                # Pobieramy nick z kolejki
                name = self.player_queue.get(timeout=1) 
                self.process_player_core(name)
                self.player_queue.task_done()
                
                # Po każdym przetworzonym graczu sprawdzamy, czy to koniec skanowania lobby
                if self.player_queue.empty() and self.total_scanned >= 20:
                    self.after(0, lambda: self.set_status("Zakończono skanowanie lobby", "#2ecc71"))
                
            except queue.Empty:
                # Jeśli kolejka jest pusta przez sekundę, a mamy już dużą grupę graczy
                if self.total_scanned >= 20 and "Skanowanie" in self.status_text.cget("text"):
                    self.after(0, lambda: self.set_status("Zakończono skanowanie lobby", "#2ecc71"))
                continue
            
            time.sleep(0.05) 

    def process_player_core(self, name):
        self.after(0, self.set_status, f"Skanowanie: {name}", "#9bc8ec")
        acc_data = self.pobierz_staty_naprawione(name)
        self.total_scanned += 1
        if not acc_data:
            self.private_count += 1
            self.after(0, self.update_counters)
            return
        
        r_info = unreal_tracker.pobierz_unreal_data(acc_data['id'])
        p_data = {
            "nick": name, "id": acc_data['id'], "ranga": r_info.get('ranga', 'Unranked'),
            "miejsce": r_info.get('miejsce', 'N/A'), "bp_level": acc_data.get('bp_level', '0'),
            "hours": acc_data.get('hours', '0'), "kd_kbm": acc_data.get('kd_kbm', '0.0'),
            "kd_pad": acc_data.get('kd_pad', '0.0'), "winrate": acc_data.get('winrate', '0'),
            "wins": acc_data.get('wins', '0'), "last_modified": acc_data.get('last_modified', 'N/A')
        }
        self.all_players_data.append(p_data)
        self.success_count += 1
        self.after(0, self.update_api_sidebar_time, p_data['last_modified'])
        self.after(0, self.update_counters)
        self.after(0, self.sort_and_refresh_ui)

    def simulate_on_start(self):
        time.sleep(1)
        self.after(0, self.set_status, "Oczekiwanie na grę...", "#3b8ed0")

    def start_tracking(self):
        self.btn_start.configure(state="disabled", text="⚡ TRACKING AKTYWNY")
        threading.Thread(target=self.engine, daemon=True).start()

    def engine(self):
        if not os.path.exists(self.log_path): return
        known_nicks = set()
        in_warmup = False
        with open(self.log_path, 'rb') as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                row = line.decode('utf-8', errors='ignore').strip()
                if "NewPhase = EAthenaGamePhase::Warmup" in row:
                    in_warmup = True
                    with self.player_queue.mutex:
                        self.player_queue.queue.clear()
                    self.all_players_data = []
                    known_nicks = set()
                    self.total_scanned = 0
                    self.success_count = 0
                    self.private_count = 0
                    self.after(0, self.update_counters)
                    self.after(0, self.sort_and_refresh_ui)
                    self.after(0, self.set_status, "Znaleziono wyspę startową", "#2ecc71")

                if in_warmup and "LogPawnBoombox" in row and "song 'None'" in row:
                    parts = row.split("'")
                    if len(parts) > 1:
                        name = parts[1]
                        if name and name not in self.BOSS_BLACKLIST and name not in known_nicks:
                            known_nicks.add(name)
                            self.player_queue.put(name)

if __name__ == "__main__":
    app = SzkieletTrackerFinal()
    app.mainloop()