from dataclasses import dataclass


@dataclass(frozen=True)
class DifficultyProfile:
    name: str
    number_of_turrets: int
    number_of_enemy_tanks: int
    turret_shoot_cooldown: float
    enemy_tank_shoot_cooldown: float
    enemy_tank_speed_factor: float  # множитель к MOVING_POWER


EASY = DifficultyProfile(
    name="Easy",
    number_of_turrets=5,
    number_of_enemy_tanks=1,
    turret_shoot_cooldown=2.0,
    enemy_tank_shoot_cooldown=2.0,
    enemy_tank_speed_factor=0.7,
)

MEDIUM = DifficultyProfile(
    name="Medium",
    number_of_turrets=7,
    number_of_enemy_tanks=2,
    turret_shoot_cooldown=2.0,
    enemy_tank_shoot_cooldown=1.0,
    enemy_tank_speed_factor=1.0,
)

HARD = DifficultyProfile(
    name="Hard",
    number_of_turrets=8,
    number_of_enemy_tanks=4,
    turret_shoot_cooldown=1.0,
    enemy_tank_shoot_cooldown=1.0,
    enemy_tank_speed_factor=1.3,
)

DIFFICULTIES = [EASY, MEDIUM, HARD]
