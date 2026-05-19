from app.settings import (
    BASE_COLS, BASE_ROWS, TILE_SIZE,
    BUILDING_WIDTH_TILES, BUILDING_HEIGHT_TILES,
    BUILDING_GARAGE_COLOR, BUILDING_SHOP_COLOR, BUILDING_HQ_COLOR,
)
from app.map import Map
from app.entities.building import Building
from app.locations.location import Location


class BaseLocation(Location):
    """Дружественная база: маленькая локация со зданиями, без сгенерированного ландшафта."""

    def __init__(self):
        game_map = Map(profile=None, cols=BASE_COLS, rows=BASE_ROWS)

        building_row = 3
        garage_col = 2
        shop_col = garage_col + BUILDING_WIDTH_TILES + 1
        hq_col = shop_col + BUILDING_WIDTH_TILES + 1

        self.garage = Building(garage_col, building_row,
                               Building.GARAGE, BUILDING_GARAGE_COLOR, "GARAGE")
        self.shop = Building(shop_col, building_row,
                             Building.SHOP, BUILDING_SHOP_COLOR, "SHOP")
        self.hq = Building(hq_col, building_row,
                           Building.HQ, BUILDING_HQ_COLOR, "HQ")
        self.buildings = [self.garage, self.shop, self.hq]

        spawn_col = BASE_COLS // 2
        spawn_row = BASE_ROWS - 4
        spawn = (float(spawn_col * TILE_SIZE), float(spawn_row * TILE_SIZE))
        super().__init__(game_map, player_spawn=spawn, camera_follows=False)
