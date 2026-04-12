from dataclasses import dataclass, field
import settings


@dataclass
class Fighter:
    team: str
    unit_kind: str
    lane: int
    x: float
    hp: int
    max_hp: int
    damage: int
    speed: float
    attack_range: float
    attack_cooldown: float
    width: int = 72
    height: int = 72
    last_attack_time: float = field(default=0.0)
    anim_timer: float = field(default=0.0)
    anim_index: int = field(default=0)
    current_action: str = field(default="walk")

    @property
    def alive(self):
        return self.hp > 0

    @property
    def direction(self):
        return 1 if self.team == "cats" else -1

    @property
    def y(self):
        return settings.LANE_Y[self.lane]

    def in_range_of(self, other):
        if self.lane != other.lane:
            return False
        return abs(self.x - other.x) <= self.attack_range

    def can_attack(self, now):
        return (now - self.last_attack_time) >= self.attack_cooldown

    def attack(self, other, now):
        other.hp -= self.damage
        self.last_attack_time = now
        self.current_action = "attack"
        self.anim_index = 0
        self.anim_timer = 0.0

    def move(self, dt):
        self.x += self.direction * self.speed * dt
        self.current_action = "walk"

    def idle(self):
        self.current_action = "idle"

    def tick_animation(self, dt):
        self.anim_timer += dt
        while self.anim_timer >= settings.ANIMATION_FRAME_TIME:
            self.anim_timer -= settings.ANIMATION_FRAME_TIME
            self.anim_index = (self.anim_index + 1) % 2


def make_fighter(team, unit_kind, lane, x):
    stats = settings.UNIT_TYPES[unit_kind]
    return Fighter(
        team=team,
        unit_kind=unit_kind,
        lane=lane,
        x=x,
        hp=stats["hp"],
        max_hp=stats["hp"],
        damage=stats["damage"],
        speed=stats["speed"],
        attack_range=settings.ATTACK_RANGE,
        attack_cooldown=settings.ATTACK_COOLDOWN,
    )
