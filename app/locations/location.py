class Location:
    """Базовая локация: карта + размеры мира + точка спавна игрока + режим камеры."""

    def __init__(self, game_map, player_spawn, camera_follows):
        self.map = game_map
        self.world_width = game_map.world_width
        self.world_height = game_map.world_height
        self.player_spawn = player_spawn
        self.camera_follows = camera_follows
