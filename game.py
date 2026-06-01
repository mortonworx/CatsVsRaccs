import random
import time
import tkinter as tk

from audio import AudioManager
import settings
from entities import make_fighter
from sprites import SpriteManager


class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title(settings.TITLE)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=settings.WINDOW_WIDTH,
            height=settings.WINDOW_HEIGHT,
            bg=settings.BACKGROUND_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.sprites = SpriteManager()
        self.audio = AudioManager()

        self.running = True
        self.last_time = time.perf_counter()

        self.state = "title"
        self.player_team = "cats"
        self.ai_team = "raccoons"
        self.selected_difficulty = "novice"
        self.selected_unit_kind = "strong"
        self.music_enabled = True

        self.reset_match()
        self.game_loop()

    def on_close(self):
        self.running = False
        self.audio.shutdown()
        self.root.destroy()

    def reset_match(self):
        difficulty = settings.DIFFICULTY_SETTINGS[self.selected_difficulty]

        self.cats = []
        self.raccoons = []

        self.cat_turf_hp = difficulty["starting_turf_hp"]
        self.raccoon_turf_hp = difficulty["starting_turf_hp"]

        self.energy = difficulty["starting_energy"]
        self.score = 0
        self.message = "Choose a side to begin."

        self.ai_spawn_timer = 0.0
        self.next_ai_spawn = random.uniform(
            difficulty["ai_spawn_min"],
            difficulty["ai_spawn_max"],
        )

        self.game_over = False
        self.winner_text = ""
        self.last_time = time.perf_counter()

    def start_game(self, team):
        self.player_team = team
        self.ai_team = "raccoons" if team == "cats" else "cats"
        self.state = "difficulty"
        self.message = "Choose difficulty: 1 Easy, 2 Novice, 3 Expert."
        self.audio.play_sound(settings.UI_SELECT_SOUND_PATH)

    def start_match(self, difficulty):
        self.selected_difficulty = difficulty
        self.state = "playing"
        self.selected_unit_kind = "strong"
        self.reset_match()
        self.message = (
            f"{self.difficulty_name(difficulty)} mode. "
            "Pick unit type with 1/2/3, then lane with Q/W/E."
        )
        self.audio.play_sound(settings.UI_SELECT_SOUND_PATH)

    def team_name(self, team):
        return "Cats" if team == "cats" else "Raccoons"

    def unit_name(self, unit_kind):
        return unit_kind.capitalize()

    def difficulty_name(self, difficulty):
        return settings.DIFFICULTY_SETTINGS[difficulty]["label"]

    def music_label(self):
        return "On" if self.music_enabled else "Off"

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.message = "Music enabled."
        else:
            self.audio.stop_music()
            self.message = "Music disabled."
        self.audio.play_sound(settings.UI_SELECT_SOUND_PATH)

    def get_team_list(self, team):
        return self.cats if team == "cats" else self.raccoons

    def spawn_unit(self, team, unit_kind, lane):
        x = settings.CAT_START_X if team == "cats" else settings.RACCOON_START_X
        fighter = make_fighter(team, unit_kind, lane, x)
        self.get_team_list(team).append(fighter)

    def spawn_player_unit(self, lane):
        cost = settings.UNIT_TYPES[self.selected_unit_kind]["cost"]
        if self.energy < cost:
            self.message = f"Not enough treats for {self.unit_name(self.selected_unit_kind)}."
            self.audio.play_sound(settings.NOT_ENOUGH_ENERGY_SOUND_PATH)
            return

        self.spawn_unit(self.player_team, self.selected_unit_kind, lane)
        self.energy -= cost
        self.message = f"Sent {self.unit_name(self.selected_unit_kind)} {self.team_name(self.player_team)} to lane {lane + 1}."
        self.audio.play_sound(settings.SPAWN_SOUND_PATH)

    def spawn_ai_unit(self):
        lane = random.randint(0, settings.LANE_COUNT - 1)
        choices = ["fast", "strong", "tough"]
        weights = [45, 35, 20]
        unit_kind = random.choices(choices, weights=weights, k=1)[0]
        self.spawn_unit(self.ai_team, unit_kind, lane)
        self.audio.play_sound(settings.SPAWN_SOUND_PATH)

    def on_key_press(self, event):
        key = event.keysym.lower()

        if key == "m":
            self.toggle_music()
            return

        if self.state == "title":
            if key == "c":
                self.start_game("cats")
            elif key == "r":
                self.start_game("raccoons")
            return

        if self.state == "difficulty":
            difficulty_map = {"1": "easy", "2": "novice", "3": "expert"}
            if key in difficulty_map:
                self.start_match(difficulty_map[key])
            elif key == "escape":
                self.state = "title"
                self.reset_match()
                self.audio.play_sound(settings.UI_SELECT_SOUND_PATH)
            return

        if key == "escape":
            self.state = "title"
            self.reset_match()
            self.audio.play_sound(settings.UI_SELECT_SOUND_PATH)
            return

        if key == "r" and self.game_over:
            self.start_game(self.player_team)
            return

        if self.state != "playing" or self.game_over:
            return

        if key == "1":
            self.selected_unit_kind = "strong"
            self.message = "Selected Strong unit. Choose lane with Q/W/E."
            self.audio.play_sound(settings.UI_SELECT_SOUND_PATH)
            return
        if key == "2":
            self.selected_unit_kind = "fast"
            self.message = "Selected Fast unit. Choose lane with Q/W/E."
            self.audio.play_sound(settings.UI_SELECT_SOUND_PATH)
            return
        if key == "3":
            self.selected_unit_kind = "tough"
            self.message = "Selected Tough unit. Choose lane with Q/W/E."
            self.audio.play_sound(settings.UI_SELECT_SOUND_PATH)
            return

        lane_map = {"q": 0, "w": 1, "e": 2}
        if key in lane_map:
            self.spawn_player_unit(lane_map[key])

    def game_loop(self):
        now = time.perf_counter()
        dt = min(now - self.last_time, 0.05)
        self.last_time = now

        if self.running:
            self.sync_music()
            self.update(dt, now)
            self.draw()

        self.root.after(settings.FRAME_MS, self.game_loop)

    def update(self, dt, now):
        if self.state != "playing" or self.game_over:
            return

        self.energy = min(
            settings.ENERGY_MAX,
            self.energy
            + settings.DIFFICULTY_SETTINGS[self.selected_difficulty]["energy_regen_per_second"] * dt
        )

        self.ai_spawn_timer += dt
        if self.ai_spawn_timer >= self.next_ai_spawn:
            self.spawn_ai_unit()
            self.ai_spawn_timer = 0.0
            difficulty = settings.DIFFICULTY_SETTINGS[self.selected_difficulty]
            self.next_ai_spawn = random.uniform(
                difficulty["ai_spawn_min"],
                difficulty["ai_spawn_max"],
            )

        self.update_team(self.cats, self.raccoons, now, dt)
        self.update_team(self.raccoons, self.cats, now, dt)

        self.cleanup_units()
        self.check_goals()
        self.check_winner()

    def update_team(self, attackers, defenders, now, dt):
        for fighter in attackers:
            if not fighter.alive:
                continue

            target = self.find_target(fighter, defenders)

            if target and fighter.in_range_of(target):
                if fighter.can_attack(now):
                    fighter.attack(target, now)
                    self.audio.play_sound(settings.ATTACK_SOUND_PATH)
                    self.audio.play_sound(settings.HIT_SOUND_PATH)
                else:
                    fighter.idle()
            elif target:
                fighter.move(dt)
            else:
                fighter.move(dt)

            fighter.tick_animation(dt)

    def find_target(self, fighter, enemies):
        same_lane = [
            enemy for enemy in enemies
            if enemy.alive and enemy.lane == fighter.lane
        ]
        if not same_lane:
            return None

        if fighter.team == "cats":
            ahead = [e for e in same_lane if e.x >= fighter.x]
            if not ahead:
                return None
            return min(ahead, key=lambda e: e.x)

        ahead = [e for e in same_lane if e.x <= fighter.x]
        if not ahead:
            return None
        return max(ahead, key=lambda e: e.x)

    def cleanup_units(self):
        defeated_raccoons = sum(1 for r in self.raccoons if not r.alive)
        defeated_cats = sum(1 for c in self.cats if not c.alive)

        self.cats = [c for c in self.cats if c.alive]
        self.raccoons = [r for r in self.raccoons if r.alive]

        if self.player_team == "cats" and defeated_raccoons > 0:
            self.score += defeated_raccoons * 10
        elif self.player_team == "raccoons" and defeated_cats > 0:
            self.score += defeated_cats * 10

    def check_goals(self):
        remaining_cats = []
        for cat in self.cats:
            if cat.x >= settings.RIGHT_TURF_X - settings.GOAL_PADDING:
                self.raccoon_turf_hp -= 1
                self.audio.play_sound(settings.BREAKTHROUGH_SOUND_PATH)
                if self.player_team == "cats":
                    self.score += 25
                    self.message = "Your cats pushed into raccoon turf!"
                else:
                    self.message = "Cats pushed into raccoon turf!"
            else:
                remaining_cats.append(cat)
        self.cats = remaining_cats

        remaining_raccoons = []
        for raccoon in self.raccoons:
            if raccoon.x <= settings.LEFT_TURF_X + settings.GOAL_PADDING:
                self.cat_turf_hp -= 1
                self.audio.play_sound(settings.BREAKTHROUGH_SOUND_PATH)
                if self.player_team == "raccoons":
                    self.score += 25
                    self.message = "Your raccoons pushed into cat turf!"
                else:
                    self.message = "Raccoons pushed into cat turf!"
            else:
                remaining_raccoons.append(raccoon)
        self.raccoons = remaining_raccoons

    def check_winner(self):
        if self.game_over:
            return

        if self.cat_turf_hp <= 0:
            self.game_over = True
            self.winner_text = "You defended raccoon turf!" if self.player_team == "raccoons" else "Raccoons defended their turf!"
            self.message = "Press R to replay or Esc for title."
            if self.player_team == "raccoons":
                self.audio.play_sound(settings.WIN_SOUND_PATH)
            else:
                self.audio.play_sound(settings.LOSE_SOUND_PATH)
        elif self.raccoon_turf_hp <= 0:
            self.game_over = True
            self.winner_text = "You defended cat turf!" if self.player_team == "cats" else "Cats defended their turf!"
            self.message = "Press R to replay or Esc for title."
            if self.player_team == "cats":
                self.audio.play_sound(settings.WIN_SOUND_PATH)
            else:
                self.audio.play_sound(settings.LOSE_SOUND_PATH)

    def sync_music(self):
        if not self.music_enabled:
            self.audio.stop_music()
            return

        if self.state in {"title", "difficulty"}:
            self.audio.play_music("title", settings.TITLE_THEME_PATH)
            return

        if self.state == "playing":
            if self.selected_difficulty == "expert":
                self.audio.play_music("expert", settings.EXPERT_THEME_PATH)
            else:
                self.audio.play_music("battle", settings.BATTLE_THEME_PATH)

    def draw(self):
        self.canvas.delete("all")

        if self.state == "title":
            self.draw_title_screen()
            return

        if self.state == "difficulty":
            self.draw_difficulty_screen()
            return

        self.draw_background()
        self.draw_hud()
        self.draw_units()

        if self.game_over:
            self.draw_game_over()

    def draw_title_screen(self):
        self.canvas.create_rectangle(0, 0, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, fill="#b9e3a6", outline="")
        self.canvas.create_text(settings.WINDOW_WIDTH // 2, 110, text="Cats vs Raccoons", font=("Arial", 30, "bold"), fill="#222")
        self.canvas.create_text(settings.WINDOW_WIDTH // 2, 160, text="Turf Defenders", font=("Arial", 18, "italic"), fill="#333")
        self.canvas.create_text(settings.WINDOW_WIDTH // 2, 250, text="Press C to Play as Cats", font=("Arial", 22, "bold"), fill="#222")
        self.canvas.create_text(settings.WINDOW_WIDTH // 2, 300, text="Press R to Play as Raccoons", font=("Arial", 22, "bold"), fill="#222")
        self.canvas.create_text(settings.WINDOW_WIDTH // 2, 380, text="Strong = 1, Fast = 2, Tough = 3", font=("Arial", 16), fill="#222")
        self.canvas.create_text(settings.WINDOW_WIDTH // 2, 410, text="Use Q / W / E for top / middle / bottom lane", font=("Arial", 16), fill="#222")
        self.canvas.create_text(settings.WINDOW_WIDTH // 2, 445, text=f"Press M to toggle music ({self.music_label()})", font=("Arial", 15), fill="#222")

    def draw_difficulty_screen(self):
        self.canvas.create_rectangle(0, 0, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, fill="#b9e3a6", outline="")
        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, 130,
            text=f"You chose {self.team_name(self.player_team)}",
            font=("Arial", 28, "bold"),
            fill="#222",
        )
        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, 190,
            text="Choose Difficulty",
            font=("Arial", 24, "bold"),
            fill="#222",
        )
        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, 270,
            text="1 = Easy",
            font=("Arial", 22, "bold"),
            fill="#222",
        )
        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, 320,
            text="2 = Novice",
            font=("Arial", 22, "bold"),
            fill="#222",
        )
        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, 370,
            text="3 = Expert",
            font=("Arial", 22, "bold"),
            fill="#222",
        )
        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, 450,
            text=f"Esc = back to team select   |   M = music {self.music_label()}",
            font=("Arial", 16),
            fill="#333",
        )

    def draw_background(self):
        self.canvas.create_rectangle(0, 0, settings.LEFT_TURF_X, settings.WINDOW_HEIGHT, fill="#8dcf8f", outline="")
        self.canvas.create_rectangle(settings.RIGHT_TURF_X, 0, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, fill="#d2c085", outline="")

        self.canvas.create_text(60, 35, text="CAT TURF", font=("Arial", 16, "bold"), fill=settings.TEXT_COLOR)
        self.canvas.create_text(settings.WINDOW_WIDTH - 60, 35, text="RACCOON TURF", font=("Arial", 16, "bold"), fill=settings.TEXT_COLOR)

        for y in settings.LANE_Y:
            self.canvas.create_rectangle(
                settings.LEFT_TURF_X, y - 40,
                settings.RIGHT_TURF_X, y + 40,
                fill=settings.LANE_COLOR, outline=""
            )
            self.canvas.create_line(
                settings.LEFT_TURF_X, y + 40,
                settings.RIGHT_TURF_X, y + 40,
                fill="#6f965f", width=2
            )

    def draw_hud(self):
        unit_stats = settings.UNIT_TYPES[self.selected_unit_kind]

        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, 25,
            text=f"Score: {self.score}",
            font=("Arial", 18, "bold"),
            fill=settings.TEXT_COLOR
        )

        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, 55,
            text=(
                f"You are: {self.team_name(self.player_team)}"
                f"   |   Difficulty: {self.difficulty_name(self.selected_difficulty)}"
                f"   |   Music: {self.music_label()}"
                f"   |   Energy: {int(self.energy)}/{settings.ENERGY_MAX}"
                f"   |   Selected: {self.unit_name(self.selected_unit_kind)}"
                f"   |   Cost: {unit_stats['cost']}"
            ),
            font=("Arial", 13),
            fill=settings.TEXT_COLOR
        )

        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, 82,
            text=(
                f"Strong(1): cost 50 hp 52 dmg 14 spd 52"
                f"   |   Fast(2): cost 30 hp 28 dmg 8 spd 88"
                f"   |   Tough(3): cost 75 hp 82 dmg 10 spd 42"
            ),
            font=("Arial", 11),
            fill=settings.TEXT_COLOR
        )

        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, 108,
            text="1/2/3 = unit type, Q/W/E = lane, M = music, Esc = title",
            font=("Arial", 12),
            fill=settings.TEXT_COLOR
        )

        self.canvas.create_text(
            settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 16,
            text=self.message,
            font=("Arial", 12, "italic"),
            fill=settings.TEXT_COLOR
        )

        max_turf_hp = settings.DIFFICULTY_SETTINGS[self.selected_difficulty]["starting_turf_hp"]
        self.draw_health_bar(20, 52, self.cat_turf_hp, max_turf_hp, "Cats")
        self.draw_health_bar(settings.WINDOW_WIDTH - 210, 52, self.raccoon_turf_hp, max_turf_hp, "Raccoons")

    def draw_health_bar(self, x, y, value, max_value, label):
        width = 160
        height = 18
        fill_width = max(0, int(width * (value / max_value)))

        self.canvas.create_text(x + width // 2, y - 14, text=f"{label} Turf: {value}/{max_value}", font=("Arial", 10, "bold"), fill=settings.TEXT_COLOR)
        self.canvas.create_rectangle(x, y, x + width, y + height, fill="#ddd", outline="#333")
        self.canvas.create_rectangle(x, y, x + fill_width, y + height, fill="#4caf50", outline="")

    def draw_units(self):
        for fighter in self.cats + self.raccoons:
            self.draw_fighter(fighter)

    def draw_fighter(self, fighter):
        action = fighter.current_action
        frames = self.sprites.get_frames(fighter.team, fighter.unit_kind, action)
        frame = frames[fighter.anim_index % len(frames)]

        self.canvas.create_image(fighter.x, fighter.y + 26, image=frame, anchor="s")
        self.canvas.create_rectangle(
            fighter.x - 20, fighter.y - 45,
            fighter.x + 20, fighter.y - 39,
            fill="#ddd", outline=""
        )

        fill_w = int(40 * (fighter.hp / fighter.max_hp))
        self.canvas.create_rectangle(
            fighter.x - 20, fighter.y - 45,
            fighter.x - 20 + fill_w, fighter.y - 39,
            fill="#4caf50", outline=""
        )

    def draw_game_over(self):
        self.canvas.create_rectangle(230, 190, 870, 400, fill="white", outline="#333", width=3)
        self.canvas.create_text(550, 240, text="Game Over", font=("Arial", 28, "bold"), fill="#222")
        self.canvas.create_text(550, 285, text=self.winner_text, font=("Arial", 20, "bold"), fill="#222")
        self.canvas.create_text(550, 325, text=f"Final Score: {self.score}", font=("Arial", 18), fill="#222")
        self.canvas.create_text(550, 360, text="Press R to replay or Esc for title", font=("Arial", 16), fill="#222")
