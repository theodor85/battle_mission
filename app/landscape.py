from dataclasses import dataclass


@dataclass(frozen=True)
class LandscapeProfile:
    name: str
    rock_seed_chance: float
    rock_smooth_iterations: int
    rock_neighbor_threshold: int
    river_count: int
    lake_count: int
    lake_max_size: int
    spawn_clear_radius: int


STEPPE = LandscapeProfile(
    name="Steppe",
    rock_seed_chance=0.20,
    rock_smooth_iterations=5,
    rock_neighbor_threshold=4,
    river_count=1,
    lake_count=2,
    lake_max_size=20,
    spawn_clear_radius=8,
)

MOUNTAINS = LandscapeProfile(
    name="Mountains",
    rock_seed_chance=0.30,
    rock_smooth_iterations=5,
    rock_neighbor_threshold=4,
    river_count=2,
    lake_count=3,
    lake_max_size=20,
    spawn_clear_radius=3,
)

SWAMP = LandscapeProfile(
    name="Swamp",
    rock_seed_chance=0.18,
    rock_smooth_iterations=5,
    rock_neighbor_threshold=4,
    river_count=3,
    lake_count=20,
    lake_max_size=18,
    spawn_clear_radius=3,
)

LANDSCAPES = [STEPPE, MOUNTAINS, SWAMP]
