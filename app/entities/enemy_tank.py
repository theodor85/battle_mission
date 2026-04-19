import random

import pygame

from app.settings import (
    WORLD_WIDTH, WORLD_HEIGHT, MASS, DAMPING,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_TANK_HP,
)
from app.entities.entity import Entity
from app.entities.bullet import Bullet


class EnemyTank(Entity):
    def __init__(self, x, y, game_map, moving_power, shoot_cooldown):
        self.images = {
            'up': pygame.image.load("resources/images/enemy_tank/tank_enemy_up.png").convert_alpha(),
            'down': pygame.image.load("resources/images/enemy_tank/tank_enemy_down.png").convert_alpha(),
            'left': pygame.image.load("resources/images/enemy_tank/tank_enemy_left.png").convert_alpha(),
            'right': pygame.image.load("resources/images/enemy_tank/tank_enemy_right.png").convert_alpha(),
        }
        self.destroyed_image = pygame.image.load(
            "resources/images/enemy_tank/tank_destroyed.png"
        ).convert_alpha()
        self.direction = 'down'
        self.image = self.images[self.direction]
        w = self.image.get_width()
        h = self.image.get_height()

        super().__init__(x, y, w, h)

        self.game_map = game_map
        self.hp = ENEMY_TANK_HP
        self._moving_power = moving_power
        self._shoot_cooldown = shoot_cooldown
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.moving_power_x = 0.0
        self.moving_power_y = 0.0
        self.shoot_timer = random.uniform(0, shoot_cooldown)

        # Idle AI state
        self._idle_timer = 0.0
        self._idle_direction = None
        self._pick_idle_direction()

    def update(self, dt, camera, target_pos, player_bullets, blockers):
        if not self.alive:
            return None

        in_camera = self._is_in_camera(camera)

        if in_camera:
            bullet = self._update_combat(dt, target_pos, player_bullets)
        else:
            self._update_idle(dt)
            bullet = None

        self._calculate_speed(dt)
        self._apply_movement(blockers)
        self._keep_on_map()
        self._update_direction()

        return bullet

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.x, self.y))

    def destroy(self):
        self.alive = False
        self.image = self.destroyed_image

    def _is_in_camera(self, camera):
        sx, sy = camera.apply(self.x, self.y)
        return (sx + self.width > 0 and sx < SCREEN_WIDTH
                and sy + self.height > 0 and sy < SCREEN_HEIGHT)

    # ── Idle AI ─────────────────────────────────────────────────

    def _pick_idle_direction(self):
        choice = random.choice(['up', 'down', 'left', 'right', None, None])
        self._idle_direction = choice
        self._idle_timer = random.uniform(1.0, 3.0)

    def _update_idle(self, dt):
        self._idle_timer -= dt
        if self._idle_timer <= 0:
            self._pick_idle_direction()

        self.moving_power_x = 0.0
        self.moving_power_y = 0.0
        d = self._idle_direction
        if d == 'up':
            self.moving_power_y = -self._moving_power
        elif d == 'down':
            self.moving_power_y = self._moving_power
        elif d == 'left':
            self.moving_power_x = -self._moving_power
        elif d == 'right':
            self.moving_power_x = self._moving_power

    # ── Combat AI ───────────────────────────────────────────────

    def _update_combat(self, dt, target_pos, player_bullets):
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        tx, ty = target_pos
        dx = tx - cx
        dy = ty - cy
        dist = (dx * dx + dy * dy) ** 0.5

        # Determine shooting direction toward player
        if abs(dx) >= abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'
        self.image = self.images[self.direction]

        # Keep distance: ~1/4 to 1/3 of camera view
        ideal_dist = (SCREEN_WIDTH + SCREEN_HEIGHT) / 2 * 0.3
        dist_margin = 40.0
        self.moving_power_x = 0.0
        self.moving_power_y = 0.0

        if dist > ideal_dist + dist_margin:
            # Too far — approach
            if abs(dx) > self.width:
                self.moving_power_x = self._moving_power if dx > 0 else -self._moving_power
            if abs(dy) > self.height:
                self.moving_power_y = self._moving_power if dy > 0 else -self._moving_power
        elif dist < ideal_dist - dist_margin:
            # Too close — retreat
            if abs(dx) > self.width:
                self.moving_power_x = -self._moving_power if dx > 0 else self._moving_power
            if abs(dy) > self.height:
                self.moving_power_y = -self._moving_power if dy > 0 else self._moving_power

        # Evasion: dodge incoming bullets (overrides movement if danger)
        self._try_evade(player_bullets)

        # Shooting
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = self._shoot_cooldown
            return Bullet(self.x, self.y, self.direction,
                          self.width, self.height, self.game_map)
        return None

    def _try_evade(self, player_bullets):
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        danger_dist = 150.0

        for b in player_bullets:
            if not b.alive:
                continue
            bx = b.x + b.width / 2
            by = b.y + b.height / 2
            dist_x = abs(bx - cx)
            dist_y = abs(by - cy)

            # Bullet moving horizontally toward us
            if b.vx != 0 and dist_y < self.height and dist_x < danger_dist:
                if (b.vx > 0 and bx < cx) or (b.vx < 0 and bx > cx):
                    self.moving_power_y = self._moving_power if cy < by else -self._moving_power
                    return

            # Bullet moving vertically toward us
            if b.vy != 0 and dist_x < self.width and dist_y < danger_dist:
                if (b.vy > 0 and by < cy) or (b.vy < 0 and by > cy):
                    self.moving_power_x = self._moving_power if cx < bx else -self._moving_power
                    return

    # ── Physics (same as Player) ────────────────────────────────

    def _calculate_speed(self, dt):
        self.speed_x = (self.speed_x + self.moving_power_x / MASS) * DAMPING
        self.speed_y = (self.speed_y + self.moving_power_y / MASS) * DAMPING

        if abs(self.speed_x) < 0.01:
            self.speed_x = 0.0
        if abs(self.speed_y) < 0.01:
            self.speed_y = 0.0

    def _apply_movement(self, blockers):
        self.x += self.speed_x
        tank_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        blocked = self.game_map.get_blocked_rects(
            self.x, self.y, self.width, self.height)
        blocked.extend(blockers)
        if tank_rect.collidelist(blocked) != -1:
            self.x -= self.speed_x
            self.speed_x = 0.0

        self.y += self.speed_y
        tank_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        blocked = self.game_map.get_blocked_rects(
            self.x, self.y, self.width, self.height)
        blocked.extend(blockers)
        if tank_rect.collidelist(blocked) != -1:
            self.y -= self.speed_y
            self.speed_y = 0.0

    def _keep_on_map(self):
        if self.x < 0:
            self.x = 0.0
            if self.speed_x < 0:
                self.speed_x = 0.0
        if self.x + self.width > WORLD_WIDTH:
            self.x = float(WORLD_WIDTH - self.width)
            if self.speed_x > 0:
                self.speed_x = 0.0
        if self.y < 0:
            self.y = 0.0
            if self.speed_y < 0:
                self.speed_y = 0.0
        if self.y + self.height > WORLD_HEIGHT:
            self.y = float(WORLD_HEIGHT - self.height)
            if self.speed_y > 0:
                self.speed_y = 0.0

    def _update_direction(self):
        if abs(self.speed_x) < 0.01 and abs(self.speed_y) < 0.01:
            return
        if abs(self.speed_x) >= abs(self.speed_y):
            direction = 'right' if self.speed_x > 0 else 'left'
        else:
            direction = 'down' if self.speed_y > 0 else 'up'
        self.direction = direction
        self.image = self.images[direction]
