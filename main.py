import customtkinter as ctk
import json
import os
from functools import partial

# Load player and manager data
with open("players.json") as f:
    data = json.load(f)
    all_players = data["players"]
    all_managers = data["managers"]

# 4-4-2 formation with approximate field coordinates (x%, y%)
FORMATION = {
    "GK": (45, 90),
    "LB": (10, 65), "CB1": (30, 65), "CB2": (60, 65), "RB": (80, 65),
    "LM": (10, 45), "CM1": (35, 45), "CM2": (55, 45), "RM": (80, 45),
    "ST1": (35, 20), "ST2": (55, 20)
}

class TeamBuilderApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.selected_players = []
        self.selected_manager = None
        self.player_positions = {}

        self.main_window = ctk.CTk()
        self.main_window.title("FIFA Team Builder")
        self.main_window.geometry("1000x700")

        self.show_selection_window()
        self.main_window.mainloop()

    def show_selection_window(self):
        self.clear_window()

        
        random_select_btn = ctk.CTkButton(self.main_window, text="🎲 Losuj cały skład", command=self.randomly_select_players_and_manager)
        random_select_btn.pack(pady=5)
        

        load_btn = ctk.CTkButton(self.main_window, text="Wczytaj skład z pliku", command=self.open_load_squad_dialog)
        load_btn.pack(pady=10)

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.update_filter)

        search_entry = ctk.CTkEntry(self.main_window, textvariable=self.search_var, width=300)
        search_entry.pack(pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_window, width=800, height=500)
        self.scroll_frame.pack(pady=10)

        self.entries = []

        for entity in all_players + all_managers:
            frame = ctk.CTkFrame(self.scroll_frame)
            frame.pack(fill="x", pady=2)
            label = ctk.CTkLabel(frame, text=self.format_entity(entity), anchor="w")
            label.pack(side="left", fill="x", expand=True, padx=5)
            toggle = ctk.CTkButton(frame, text="[ ]", width=40)

            is_manager = "type" in entity and entity["type"] == "manager"
            toggle.configure(command=partial(self.toggle_selection, entity, toggle, is_manager))
            toggle.pack(side="right")
            self.entries.append((entity, frame, toggle))

        self.status_label = ctk.CTkLabel(self.main_window, text="Select 11 players and 1 manager")
        self.status_label.pack(pady=5)

        confirm_btn = ctk.CTkButton(self.main_window, text="Confirm Selection", command=self.confirm_selection)
        confirm_btn.pack(pady=10)

    def update_filter(self, *args):
        keyword = self.search_var.get().lower()
        for entity, frame, _ in self.entries:
            name = entity["name"].lower()
            frame.pack_forget() if keyword not in name else frame.pack(fill="x", pady=2)

    def toggle_selection(self, entity, toggle, is_manager):
        if is_manager:
            if self.selected_manager == entity:
                self.selected_manager = None
                toggle.configure(text="[ ]")
            else:
                self.selected_manager = entity
                for e, _, t in self.entries:
                    if "type" in e and e["type"] == "manager":
                        t.configure(text="[✔]" if e == entity else "[ ]")
        else:
            if entity in self.selected_players:
                self.selected_players.remove(entity)
                toggle.configure(text="[ ]")
            elif len(self.selected_players) < 11:
                self.selected_players.append(entity)
                toggle.configure(text="[✔]")

        self.status_label.configure(text=f"Selected {len(self.selected_players)} players and {1 if self.selected_manager else 0} manager")

    def confirm_selection(self):
        if len(self.selected_players) == 11 and self.selected_manager:
            self.show_pitch_assignment()
        else:
            self.status_label.configure(text="You must select exactly 11 players and 1 manager.")

    def show_pitch_assignment(self):
        random_btn = ctk.CTkButton(self.main_window, text="🎲 Wylosuj skład", command=self.assign_random_players)
        random_btn.pack(pady=5)
        self.clear_window()
        back_btn = ctk.CTkButton(self.main_window, text="← Wróć do wyboru zawodników", command=self.show_selection_window)
        back_btn.pack(pady=5)
        self.clear_window()
        ctk.CTkLabel(self.main_window, text="Assign players to formation (4-4-2)").pack(pady=10)

        self.pitch_canvas = ctk.CTkFrame(self.main_window, width=1000, height=500)
        self.pitch_canvas.pack(pady=5)

        self.position_buttons = {}

        for pos, (x_percent, y_percent) in FORMATION.items():
            x = int((x_percent / 100) * 900)
            y = int((y_percent / 100) * 500)

            btn = ctk.CTkButton(self.pitch_canvas, text=f"{pos}: [None]", width=140, height=30)
            btn.place(x=x, y=y, anchor="center")
            btn.configure(command=partial(self.assign_player, pos))
            ctk.CTkButton(self.pitch_canvas, text="Usuń", width=60, height=20, command=partial(self.remove_player_from_position, pos)).place(x=x, y=y+25, anchor="center")
            self.position_buttons[pos] = btn

        self.info_box = ctk.CTkTextbox(self.main_window, height=120)
        self.info_box.pack(pady=10, fill="x", padx=10)
        self.refresh_pitch_assignment()

    def assign_player(self, pos):
        self.assigning_position = pos
        self.clear_window()
        ctk.CTkLabel(self.main_window, text=f"Select player for {pos}").pack(pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_window, width=800, height=500)
        self.scroll_frame.pack(pady=10)

        for player in self.selected_players:
            frame = ctk.CTkFrame(self.scroll_frame)
            frame.pack(fill="x", pady=2)
            label = ctk.CTkLabel(frame, text=self.format_entity(player), anchor="w")
            label.pack(side="left", fill="x", expand=True)

            btn = ctk.CTkButton(frame, text="Assign", command=partial(self.set_player_to_position, pos, player))
            btn.pack(side="right")

    def set_player_to_position(self, pos, player):
        # Remove player from any other position
        for key, assigned_player in list(self.player_positions.items()):
            if assigned_player == player:
                del self.player_positions[key]

        self.player_positions[pos] = player
        self.show_pitch_assignment()

        name = player["name"]
        # already refreshed in refresh_pitch_assignment
        self.update_stats()
        self.save_squad()

    def update_stats(self):
        if len(self.player_positions) < len(FORMATION):
            self.info_box.delete("0.0", "end")
            self.info_box.insert("0.0", "Assign all positions to see team stats.")
            return

        ratings = []
        chemistry = 0

        for pos, player in self.player_positions.items():
            ratings.append(player["rating"])
            correct = player["position"] in pos or player["position"] == pos

            manager = self.selected_manager
            shared = 0
            if player["nationality"] == manager["nationality"]:
                shared += 1
            if player["league"] == manager["league"]:
                shared += 1
            if not correct:
                ratings[-1] -= 3
                shared -= 1

            chemistry += max(0, shared)

        avg_rating = sum(ratings) / len(ratings)
        self.info_box.delete("0.0", "end")
        self.info_box.insert("0.0", f"Average Rating: {avg_rating:.2f}\nChemistry: {chemistry}/{len(FORMATION)*2}")

    def save_squad(self):
        def save():
            name = name_var.get()
            if name:
                file_path = os.path.join("squads", f"squad_{name}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(squad, f, indent=4)
                popup.destroy()

        squad = {
            "manager": self.selected_manager,
            "players": {pos: self.player_positions[pos] for pos in self.player_positions}
        }
        os.makedirs("squads", exist_ok=True)

        popup = ctk.CTkToplevel(self.main_window)
        popup.geometry("300x150")
        popup.title("Save Squad")

        ctk.CTkLabel(popup, text="Enter squad name:").pack(pady=10)
        name_var = ctk.StringVar()
        name_entry = ctk.CTkEntry(popup, textvariable=name_var)
        name_entry.pack(pady=5)
        ctk.CTkButton(popup, text="Save", command=save).pack(pady=10)

    def format_entity(self, e):
        name = e.get("name", "Unknown")
        nationality = e.get("nationality", "N/A")
        league = e.get("league", "N/A")

        if e.get("type") == "manager":
            return f"Manager: {name} ({nationality}, {league})"
        position = e.get("position", "??")
        rating = e.get("rating", "?")
        return f"{name} | {position} | {rating} | {nationality} | {league}"

    def load_squad(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            squad = json.load(f)
        self.selected_manager = squad['manager']
        self.player_positions = squad['players']
        self.show_pitch_assignment()


    def refresh_pitch_assignment(self):
        if hasattr(self, 'pitch_canvas'):
            self.pitch_canvas.destroy()
        self.pitch_canvas = ctk.CTkFrame(self.main_window, width=1000, height=500)
        self.pitch_canvas.pack(pady=5)
        self.position_buttons = {}

        for pos, (x_percent, y_percent) in FORMATION.items():
            x = int((x_percent / 100) * 900)
            y = int((y_percent / 100) * 500)
            name = self.player_positions[pos]["name"] if pos in self.player_positions else "[None]"
            btn = ctk.CTkButton(self.pitch_canvas, text=f"{pos}: {name}", width=140, height=30)
            btn.place(x=x, y=y, anchor="center")
            btn.configure(command=partial(self.assign_player, pos))
            self.position_buttons[pos] = btn

        self.update_stats()

    def remove_player_from_position(self, pos):
        if pos in self.player_positions:
            del self.player_positions[pos]
            self.refresh_pitch_assignment()
            self.save_squad()


    def open_load_squad_dialog(self):
        popup = ctk.CTkToplevel(self.main_window)
        popup.geometry("400x300")
        popup.title("Wczytaj skład")

        file_list = os.listdir("squads") if os.path.exists("squads") else []
        listbox = ctk.CTkScrollableFrame(popup, width=360, height=200)
        listbox.pack(pady=10)

        for file in file_list:
            if file.endswith(".json"):
                btn = ctk.CTkButton(listbox, text=file, command=partial(self.load_squad, os.path.join("squads", file)))
                btn.pack(pady=2, fill="x", padx=10)

    import random

    def assign_random_players(self):
        if len(self.selected_players) < len(FORMATION):
            return
        players = self.selected_players[:]
        random.shuffle(players)
        self.player_positions = {}
        for pos in FORMATION:
            self.player_positions[pos] = players.pop()
        self.refresh_pitch_assignment()
        self.save_squad()

    def randomly_select_players_and_manager(self):
        import random
        all_only_players = [p for p in all_players if 'type' not in p or p['type'] != 'manager']
        all_only_managers = [m for m in all_managers if m.get("type") == "manager"]

        if len(all_only_players) >= 11 and all_only_managers:
            self.selected_players = random.sample(all_only_players, 11)
            self.selected_manager = random.choice(all_only_managers)
            self.status_label.configure(text=f"Selected 11 players and 1 manager (random)")
            self.show_pitch_assignment()


    def clear_window(self):
        for widget in self.main_window.winfo_children():
            widget.destroy()

if __name__ == '__main__':
    TeamBuilderApp()
