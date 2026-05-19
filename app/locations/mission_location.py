from app.settings import MAP_COLS, MAP_ROWS, TILE_SIZE, GROUND
from app.map import Map
from app.locations.location import Location


class MissionLocation(Location):
    """Боевая локация: случайная карта 50x50 по выбранному пейзажу."""

    def __init__(self, landscape, difficulty):
        self.landscape = landscape
        self.difficulty = difficulty
        game_map = Map(profile=landscape, cols=MAP_COLS, rows=MAP_ROWS)
        spawn = self._find_spawn(game_map)
        super().__init__(game_map, player_spawn=spawn, camera_follows=True)

    @staticmethod
    def _find_spawn(game_map):
        cx = game_map.cols // 2
        for dr in range(game_map.rows // 2):
            r = game_map.rows // 2 + dr
            if game_map.tiles[r][cx] == GROUND:
                return (float(cx * TILE_SIZE), float(r * TILE_SIZE))
        return (float(cx * TILE_SIZE), float((game_map.rows // 2) * TILE_SIZE))
