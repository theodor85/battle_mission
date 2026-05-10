import pygame

from app.settings import (
    SCREEN_WIDTH, PLAYER_MAX_HP,
    DARK_GREEN, DARK_GRAY, ORANGE, RED,
)

_MV_COLOR_ACTIVE = (200, 110, 30)
_MV_COLOR_INACTIVE = (110, 110, 110)
_MV_COLOR_DESTROYED = (45, 45, 45)


class HUD:
    def __init__(self, player, turrets, enemy_tanks, mining_vehicles=None):
        self.player = player
        self.turrets = turrets
        self.enemy_tanks = enemy_tanks
        self.mining_vehicles = mining_vehicles or []
        self.hp_display = float(PLAYER_MAX_HP)
        self.tank_icon = pygame.transform.scale(
            pygame.image.load("resources/images/player/tank_up.png").convert_alpha(),
            (50, 50),
        )
        self.turret_icon = pygame.transform.scale(
            pygame.image.load("resources/images/turret/turret_enemy_down.png").convert_alpha(),
            (50, 50),
        )
        self.enemy_tank_icon = pygame.transform.scale(
            pygame.image.load("resources/images/enemy_tank/tank_enemy_down.png").convert_alpha(),
            (50, 50),
        )

    def update(self, dt):
        hp_bar_speed = 120.0
        if self.hp_display > self.player.hp:
            self.hp_display = max(float(self.player.hp),
                                  self.hp_display - hp_bar_speed * dt)

    def draw(self, surface):
        self._draw_hp_bar(surface)
        self._draw_turret_count(surface)
        self._draw_enemy_tank_count(surface)
        self._draw_mining_vehicle_count(surface)

    def _draw_hp_bar(self, surface):
        margin = 10
        icon_size = 50
        bar_width = 250
        bar_height = 25
        bar_gap = 10

        surface.blit(self.tank_icon, (margin, margin))

        bar_x = margin + icon_size + bar_gap
        bar_y = margin + (icon_size - bar_height) // 2

        hp_ratio = self.hp_display / PLAYER_MAX_HP
        fill_width = int(bar_width * hp_ratio)
        if self.hp_display <= 20:
            bar_color = RED
        elif self.hp_display <= 60:
            bar_color = ORANGE
        else:
            bar_color = DARK_GREEN
        radius = bar_height // 2
        if fill_width > 0:
            right_radius = radius if fill_width >= bar_width else 0
            pygame.draw.rect(surface, bar_color,
                             (bar_x, bar_y, fill_width, bar_height),
                             border_top_left_radius=radius,
                             border_bottom_left_radius=radius,
                             border_top_right_radius=right_radius,
                             border_bottom_right_radius=right_radius)

        pygame.draw.rect(surface, DARK_GRAY,
                         (bar_x, bar_y, bar_width, bar_height),
                         2, border_radius=radius)

    def _draw_turret_count(self, surface):
        margin = 10
        alive_count = sum(1 for t in self.turrets if t.alive)
        gap = 15
        for i in range(alive_count):
            x = SCREEN_WIDTH - 25 - margin - (i + 1) * 25 - i * gap
            surface.blit(self.turret_icon, (x, margin))

    def _draw_enemy_tank_count(self, surface):
        margin = 10
        row_y = margin + 50 + 5
        alive_count = sum(1 for t in self.enemy_tanks if t.alive)
        gap = 15
        for i in range(alive_count):
            x = SCREEN_WIDTH - 25 - margin - (i + 1) * 25 - i * gap
            surface.blit(self.enemy_tank_icon, (x, row_y))

    def _draw_mining_vehicle_count(self, surface):
        if not self.mining_vehicles:
            return
        margin = 10
        row_y = margin + 50 + 5 + 50 + 8
        icon_size = 46
        gap = 12
        for i, vehicle in enumerate(self.mining_vehicles):
            x = SCREEN_WIDTH - margin - icon_size - i * (icon_size + gap)
            y = row_y
            if vehicle.destroyed_permanently:
                color = _MV_COLOR_DESTROYED
            elif vehicle.on_map:
                color = _MV_COLOR_ACTIVE
            else:
                color = _MV_COLOR_INACTIVE
            pygame.draw.rect(surface, color, (x, y, icon_size, icon_size))
            # Simple vehicle silhouette inside icon
            inner = (x + 4, y + icon_size // 2 - 7, icon_size - 8, 14)
            lighter = tuple(min(255, c + 40) for c in color)
            pygame.draw.rect(surface, lighter, inner)
            if vehicle.destroyed_permanently:
                # Draw X
                pygame.draw.line(surface, (180, 50, 50),
                                 (x + 6, y + 6), (x + icon_size - 6, y + icon_size - 6), 3)
                pygame.draw.line(surface, (180, 50, 50),
                                 (x + icon_size - 6, y + 6), (x + 6, y + icon_size - 6), 3)
