import math
import random
import sys

import pygame
from pygame.locals import QUIT

from app.scenes.scene import Scene
from app.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BLACK,
    MAP_COLS, MAP_ROWS, TILE_SIZE, GROUND, TILES,
    MOVING_POWER, BULLET_DAMAGE,
    MUSIC_PATH, MUSIC_VOLUME, MUSIC_FADEOUT_MS,
    GAME_OVER_DELAY, DEFAULT_LANDSCAPE, DEFAULT_DIFFICULTY,
    MISSILE_INTERVAL_MIN, MISSILE_INTERVAL_MAX,
    MISSILE_AIM_OFFSET_TILES, MISSILE_SAFE_RADIUS_TILES,
    MISSILE_DAMAGE_TIERS, MISSILE_EXPLOSION_SCALE,
    CAMERA_SHAKE_DURATION, CAMERA_SHAKE_INTENSITY,
    WORLD_WIDTH, WORLD_HEIGHT,
    MINING_VEHICLE_INITIAL_COOLDOWN_1, MINING_VEHICLE_INITIAL_COOLDOWN_2,
    MINING_VEHICLE_REDELIVERY_COOLDOWN, MINING_ROCKET_SHOOT_COOLDOWN,
    HELICOPTER_DROP_MIN_DIST_TILES, HELICOPTER_WIDTH, HELICOPTER_HEIGHT,
    MINE_DAMAGE, HQ_FADE_DURATION,
)
from app.map import Map
from app.entities import (
    Player, Turret, EnemyTank, Explosion, EntityList, Missile,
    Helicopter, MiningVehicle,
)
from app.camera import Camera
from app.events import EventBus
from app.collision import check_collisions
from app.hud import HUD


class GameScene(Scene):
    def __init__(self, screen, clock, music_on=True, landscape=None, difficulty=None,
                 player_hp=None):
        super().__init__(screen, clock)
        self._music_on = music_on
        self._landscape = landscape or DEFAULT_LANDSCAPE
        self._difficulty = difficulty or DEFAULT_DIFFICULTY

        pygame.mixer.stop()  # release channels leaked by entities from a previous run
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(MUSIC_VOLUME if music_on else 0)
        pygame.mixer.music.play(loops=-1)

        self.map = Map(profile=self._landscape)
        self.camera = Camera(world_width=self.map.world_width,
                             world_height=self.map.world_height)
        self.player = Player(self.map)
        self._place_player_on_ground()
        if player_hp is not None:
            self.player.hp = player_hp
        self.phase = 'intro'
        self.player.frozen = True
        self.player.visible = False
        self._fade_alpha = 0.0
        self._fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._fade_surface.fill(BLACK)
        self._outro_picked_up = False
        self.turrets = self._spawn_turrets()
        self.enemy_tanks = self._spawn_enemy_tanks()
        self.player_bullets = EntityList()
        self.enemy_bullets = EntityList()
        self.explosions = EntityList()
        self.missiles = EntityList()
        self._missile_timer = random.uniform(MISSILE_INTERVAL_MIN, MISSILE_INTERVAL_MAX)
        self.game_over = False
        self._game_over_timer = 0.0
        self._game_over_title = ""
        self.destroyed_tank_image = pygame.image.load(
            "resources/images/enemy_tank/tank_destroyed.png"
        ).convert_alpha()

        # Mining system
        self.mining_vehicles = [MiningVehicle(self.map), MiningVehicle(self.map)]
        self.mining_vehicles[0].delivery_cooldown = MINING_VEHICLE_INITIAL_COOLDOWN_1
        self.mining_vehicles[1].delivery_cooldown = MINING_VEHICLE_INITIAL_COOLDOWN_2
        self.helicopters = EntityList()
        self.mining_rockets = EntityList()
        self.mines = {}  # (col, row) -> sprite index
        self._mine_sprites = [
            pygame.transform.scale(
                pygame.image.load(f"resources/images/mines/mine_tile_{i}.png").convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            )
            for i in range(2)
        ]

        self.hud = HUD(self.player, self.turrets, self.enemy_tanks, self.mining_vehicles)

        self._spawn_player_delivery_helicopter()

        self.events = EventBus()
        self.events.listen("turret_destroyed", self._on_turret_destroyed)
        self.events.listen("player_hit", self._on_player_hit)
        self.events.listen("bullet_hit_rock", self._on_bullet_hit_rock)
        self.events.listen("enemy_tank_hit", self._on_enemy_tank_hit)
        self.events.listen("mining_vehicle_hit", self._on_mining_vehicle_hit)

    def _place_player_on_ground(self):
        for dr in range(MAP_ROWS // 2):
            r = MAP_ROWS // 2 + dr
            c = MAP_COLS // 2
            if TILES[self.map.tiles[r][c]]['type'] == GROUND:
                self.player.x = float(c * TILE_SIZE)
                self.player.y = float(r * TILE_SIZE)
                return

    def _spawn_turrets(self):
        center_r = MAP_ROWS // 2
        center_c = MAP_COLS // 2
        clear_radius = self._landscape.spawn_clear_radius
        candidates = []
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if TILES[self.map.tiles[r][c]]['type'] != GROUND:
                    continue
                if (abs(r - center_r) <= clear_radius
                        and abs(c - center_c) <= clear_radius):
                    continue
                candidates.append((r, c))
        count = self._difficulty.number_of_turrets
        cooldown = self._difficulty.turret_shoot_cooldown
        chosen = random.sample(candidates, min(count, len(candidates)))
        return [Turret(c * TILE_SIZE, r * TILE_SIZE, self.map, cooldown) for r, c in chosen]

    def _spawn_enemy_tanks(self):
        center_r = MAP_ROWS // 2
        center_c = MAP_COLS // 2
        clear_radius = self._landscape.spawn_clear_radius
        turret_positions = {(int(t.y // TILE_SIZE), int(t.x // TILE_SIZE))
                           for t in self.turrets}
        candidates = []
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if TILES[self.map.tiles[r][c]]['type'] != GROUND:
                    continue
                if (abs(r - center_r) <= clear_radius
                        and abs(c - center_c) <= clear_radius):
                    continue
                if (r, c) in turret_positions:
                    continue
                candidates.append((r, c))
        count = self._difficulty.number_of_enemy_tanks
        tank_power = MOVING_POWER * self._difficulty.enemy_tank_speed_factor
        tank_cooldown = self._difficulty.enemy_tank_shoot_cooldown
        chosen = random.sample(candidates, min(count, len(candidates)))
        return [EnemyTank(c * TILE_SIZE, r * TILE_SIZE, self.map, tank_power, tank_cooldown)
                for r, c in chosen]

    def _trigger_game_over(self, title):
        if self.game_over:
            return
        self.game_over = True
        self._game_over_title = title
        self._game_over_timer = 0.0
        pygame.mixer.music.fadeout(MUSIC_FADEOUT_MS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    def update(self, dt):
        self.hud.update(dt)

        for exp in self.explosions:
            exp.update(dt)
        self.explosions.prune()

        self._update_helicopters(dt)

        if self.phase == 'intro':
            self.player.update(dt)
            self.camera.update(self.player.x, self.player.y,
                               self.player.speed_x, self.player.speed_y, dt)
            return

        if self.phase == 'outro':
            self._update_outro(dt)
            return

        if self.game_over:
            self._game_over_timer += dt
            if self._game_over_timer >= GAME_OVER_DELAY:
                from app.scenes.game_over_scene import GameOverScene
                self.next_scene = GameOverScene(
                    self.screen, self.clock, self._game_over_title,
                    background=self.screen.copy(),
                    music_on=self._music_on,
                    landscape=self._landscape,
                    difficulty=self._difficulty,
                )
            return

        self.player.blockers = [t.get_rect() for t in self.enemy_tanks
                                if t.alive]
        self.player.blockers += [v.get_rect() for v in self.mining_vehicles
                                  if v.on_map and not v.destroyed_permanently]
        self.player.update(dt)
        self.camera.update(self.player.x, self.player.y,
                           self.player.speed_x, self.player.speed_y, dt)

        bullet = self.player.shoot(dt)
        if bullet is not None:
            self.player_bullets.add(bullet)

        player_center = (self.player.x + self.player.width / 2,
                         self.player.y + self.player.height / 2)
        for turret in self.turrets:
            turret.target_pos = player_center
            enemy_bullet = turret.update(dt, self.camera)
            if enemy_bullet is not None:
                self.enemy_bullets.add(enemy_bullet)

        # Build blocker rects for enemy tank physics
        player_rect = self.player.get_rect()
        for tank in self.enemy_tanks:
            if not tank.alive:
                continue
            blockers = [player_rect]
            for other in self.enemy_tanks:
                if other is not tank and other.alive:
                    blockers.append(other.get_rect())
            enemy_bullet = tank.update(
                dt, self.camera, player_center,
                self.player_bullets, blockers)
            if enemy_bullet is not None:
                self.enemy_bullets.add(enemy_bullet)

        for b in self.player_bullets:
            b.update(dt)
        for b in self.enemy_bullets:
            b.update(dt)

        # Missile spawner
        self._missile_timer -= dt
        if self._missile_timer <= 0:
            self._missile_timer = random.uniform(MISSILE_INTERVAL_MIN, MISSILE_INTERVAL_MAX)
            self._spawn_missile()

        for m in self.missiles:
            m.update(dt)
        for m in self.missiles:
            if not m.alive and m.reached_target:
                self._on_missile_impact(m.target_x, m.target_y)
        self.missiles.prune()

        # Mining system
        self._update_mining_system(dt, player_center)
        self._update_mining_rockets(dt)
        self._check_mine_collision()

        check_collisions(
            self.player, self.player_bullets, self.enemy_bullets,
            self.turrets, self.enemy_tanks, self.events,
            mining_vehicles=self.mining_vehicles,
        )

        self.player_bullets.prune()
        self.enemy_bullets.prune()

        # Проверка победы
        if (all(not t.alive for t in self.turrets)
                and all(not t.alive for t in self.enemy_tanks)):
            self._start_outro()

    def draw(self):
        self.screen.fill(BLACK)
        self.map.draw(self.screen, self.camera)

        # Draw mines before entities
        self._draw_mines()

        for turret in self.turrets:
            turret.draw(self.screen, self.camera)
        for tank in self.enemy_tanks:
            tank.draw(self.screen, self.camera)
        for vehicle in self.mining_vehicles:
            vehicle.draw(self.screen, self.camera)
        for rocket in self.mining_rockets:
            rocket.draw(self.screen, self.camera)
        for b in self.player_bullets:
            b.draw(self.screen, self.camera)
        for b in self.enemy_bullets:
            b.draw(self.screen, self.camera)
        for m in self.missiles:
            m.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        for h in self.helicopters:
            h.draw(self.screen, self.camera)
        for exp in self.explosions:
            exp.draw(self.screen, self.camera)
        self.hud.draw(self.screen)

        if self._fade_alpha > 0:
            self._fade_surface.set_alpha(int(self._fade_alpha))
            self.screen.blit(self._fade_surface, (0, 0))

        pygame.display.update()

    def _draw_mines(self):
        for (col, row), sprite_idx in self.mines.items():
            sx, sy = self.camera.apply(col * TILE_SIZE, row * TILE_SIZE)
            if -TILE_SIZE <= sx <= SCREEN_WIDTH and -TILE_SIZE <= sy <= SCREEN_HEIGHT:
                self.screen.blit(self._mine_sprites[sprite_idx], (sx, sy))

    # ── Event handlers ──────────────────────────────────────────

    def _on_turret_destroyed(self, data):
        data["turret"].destroy()
        self.explosions.add(Explosion(data["x"], data["y"]))

    def _on_player_hit(self, data):
        self.player.hp -= data["damage"]
        self.explosions.add(Explosion(data["x"], data["y"]))
        if self.player.hp <= 0:
            self.player.hp = 0
            self.player.image = self.destroyed_tank_image
            self._trigger_game_over("Game Over")

    def _on_enemy_tank_hit(self, data):
        tank = data["tank"]
        tank.hp -= BULLET_DAMAGE
        self.explosions.add(Explosion(data["x"], data["y"]))
        if tank.hp <= 0:
            tank.destroy()

    def _on_bullet_hit_rock(self, data):
        self.explosions.add(Explosion(data["x"], data["y"]))

    def _on_mining_vehicle_hit(self, data):
        vehicle = data["vehicle"]
        vehicle.hp -= BULLET_DAMAGE
        self.explosions.add(Explosion(data["x"], data["y"]))
        if vehicle.hp <= 0:
            vehicle.destroyed_permanently = True
            vehicle.state = MiningVehicle.DESTROYED
            self.explosions.add(Explosion(data["x"], data["y"]))

    def _spawn_missile(self):
        player_cx = self.player.x + self.player.width / 2
        player_cy = self.player.y + self.player.height / 2
        safe_px = MISSILE_SAFE_RADIUS_TILES * TILE_SIZE

        for t in self.turrets:
            if t.alive:
                tcx = t.x + t.width / 2
                tcy = t.y + t.height / 2
                if abs(tcx - player_cx) <= safe_px and abs(tcy - player_cy) <= safe_px:
                    return
        for t in self.enemy_tanks:
            if t.alive:
                tcx = t.x + t.width / 2
                tcy = t.y + t.height / 2
                if abs(tcx - player_cx) <= safe_px and abs(tcy - player_cy) <= safe_px:
                    return

        offset_x = random.randint(-MISSILE_AIM_OFFSET_TILES, MISSILE_AIM_OFFSET_TILES) * TILE_SIZE
        offset_y = random.randint(-MISSILE_AIM_OFFSET_TILES, MISSILE_AIM_OFFSET_TILES) * TILE_SIZE
        target_x = max(0.0, min(player_cx + offset_x, float(WORLD_WIDTH)))
        target_y = max(0.0, min(player_cy + offset_y, float(WORLD_HEIGHT)))

        edge = random.choice(('top', 'bottom', 'left', 'right'))
        if edge == 'left':
            self.missiles.add(Missile(-TILE_SIZE, target_y, target_x, target_y, 'right'))
        elif edge == 'right':
            self.missiles.add(Missile(WORLD_WIDTH + TILE_SIZE, target_y, target_x, target_y, 'left'))
        elif edge == 'top':
            self.missiles.add(Missile(target_x, -TILE_SIZE, target_x, target_y, 'down'))
        else:
            self.missiles.add(Missile(target_x, WORLD_HEIGHT + TILE_SIZE, target_x, target_y, 'up'))

    def _on_missile_impact(self, cx, cy):
        self.explosions.add(Explosion(cx, cy, scale=MISSILE_EXPLOSION_SCALE))
        self.camera.start_shake(CAMERA_SHAKE_DURATION, CAMERA_SHAKE_INTENSITY)

        player_cx = self.player.x + self.player.width / 2
        player_cy = self.player.y + self.player.height / 2
        dist = ((player_cx - cx) ** 2 + (player_cy - cy) ** 2) ** 0.5
        ring = int(dist / TILE_SIZE)
        if ring in MISSILE_DAMAGE_TIERS:
            self.player.hp -= MISSILE_DAMAGE_TIERS[ring]
            self.explosions.add(Explosion(player_cx, player_cy))
            if self.player.hp <= 0:
                self.player.hp = 0
                self.player.image = self.destroyed_tank_image
                self._trigger_game_over("Game Over")

        for turret in self.turrets:
            if not turret.alive:
                continue
            tcx = turret.x + turret.width / 2
            tcy = turret.y + turret.height / 2
            dist = ((tcx - cx) ** 2 + (tcy - cy) ** 2) ** 0.5
            ring = int(dist / TILE_SIZE)
            if ring in MISSILE_DAMAGE_TIERS:
                turret.destroy()
                self.explosions.add(Explosion(tcx, tcy))

        for tank in self.enemy_tanks:
            if not tank.alive:
                continue
            tcx = tank.x + tank.width / 2
            tcy = tank.y + tank.height / 2
            dist = ((tcx - cx) ** 2 + (tcy - cy) ** 2) ** 0.5
            ring = int(dist / TILE_SIZE)
            if ring in MISSILE_DAMAGE_TIERS:
                tank.hp -= MISSILE_DAMAGE_TIERS[ring]
                self.explosions.add(Explosion(tcx, tcy))
                if tank.hp <= 0:
                    tank.destroy()

    # ── Mining system ────────────────────────────────────────────

    def _update_mining_system(self, dt, player_center):
        player_cx, player_cy = player_center

        for vehicle in self.mining_vehicles:
            if vehicle.destroyed_permanently:
                continue

            if vehicle.state == MiningVehicle.INACTIVE:
                vehicle.delivery_cooldown -= dt
                if vehicle.delivery_cooldown <= 0 and not self._has_helicopter_for(vehicle):
                    self._spawn_delivery_helicopter(vehicle)

            elif vehicle.state == MiningVehicle.SHOOTING:
                vehicle.update(dt, player_cx, player_cy)  # keep facing player
                vehicle.shoot_timer -= dt
                if vehicle.shoot_timer <= 0 and vehicle.rockets_left > 0:
                    vehicle.shoot_timer = MINING_ROCKET_SHOOT_COOLDOWN
                    rocket = vehicle.create_rocket(player_cx, player_cy)
                    self.mining_rockets.add(rocket)
                    vehicle.rockets_left -= 1
                    if vehicle.rockets_left == 0:
                        vehicle.state = MiningVehicle.MOVING_AWAY

            elif vehicle.state == MiningVehicle.MOVING_AWAY:
                vehicle.update(dt, player_cx, player_cy)

            elif vehicle.state == MiningVehicle.WAITING_FOR_PICKUP:
                vehicle.pickup_timer -= dt
                if vehicle.pickup_timer <= 0 and not self._has_helicopter_for(vehicle):
                    self._spawn_pickup_helicopter(vehicle)

    def _update_helicopters(self, dt):
        for h in self.helicopters:
            h.update(dt, self.camera)
        self.helicopters.prune()

    def _update_mining_rockets(self, dt):
        for rocket in self.mining_rockets:
            rocket.update(dt)
        for rocket in self.mining_rockets:
            if not rocket.alive and rocket.reached_target:
                self._on_mining_rocket_landed(rocket.target_col, rocket.target_row,
                                              rocket.target_x, rocket.target_y)
        self.mining_rockets.prune()

    def _on_mining_rocket_landed(self, col, row, world_x, world_y):
        self.explosions.add(Explosion(world_x, world_y))
        if TILES[self.map.tiles[row][col]]['type'] == GROUND:
            self.mines[(col, row)] = random.randrange(len(self._mine_sprites))

    def _check_mine_collision(self):
        if not self.mines:
            return
        player_rect = self.player.get_rect()
        blast_radius = TILE_SIZE/2 * math.sqrt(2)
        triggered = []
        for (col, row) in self.mines:
            cx = col * TILE_SIZE + TILE_SIZE // 2
            cy = row * TILE_SIZE + TILE_SIZE // 2
            nearest_x = max(player_rect.left, min(cx, player_rect.right))
            nearest_y = max(player_rect.top, min(cy, player_rect.bottom))
            dx = cx - nearest_x
            dy = cy - nearest_y
            if dx * dx + dy * dy <= blast_radius * blast_radius:
                triggered.append((col, row))
        for key in triggered:
            del self.mines[key]
            cx = key[0] * TILE_SIZE + TILE_SIZE // 2
            cy = key[1] * TILE_SIZE + TILE_SIZE // 2
            self.events.post("player_hit",
                             damage=MINE_DAMAGE,
                             x=float(cx),
                             y=float(cy))

    def _has_helicopter_for(self, vehicle):
        return any(h.vehicle is vehicle and h.alive for h in self.helicopters)

    def _find_drop_tile(self, player_cx, player_cy):
        player_col = int(player_cx // TILE_SIZE)
        player_row = int(player_cy // TILE_SIZE)
        min_dist = HELICOPTER_DROP_MIN_DIST_TILES
        candidates = [
            (c, r)
            for r in range(MAP_ROWS)
            for c in range(MAP_COLS)
            if (TILES[self.map.tiles[r][c]]['type'] == GROUND
                and abs(r - player_row) + abs(c - player_col) >= min_dist)
        ]
        if not candidates:
            candidates = [(c, r)
                          for r in range(MAP_ROWS)
                          for c in range(MAP_COLS)
                          if TILES[self.map.tiles[r][c]]['type'] == GROUND]
        col, row = random.choice(candidates)
        return (col * TILE_SIZE + TILE_SIZE // 2,
                row * TILE_SIZE + TILE_SIZE // 2)

    def _farthest_edge(self, player_cx, player_cy):
        options = [
            ('left', player_cx),
            ('right', WORLD_WIDTH - player_cx),
            ('top', player_cy),
            ('bottom', WORLD_HEIGHT - player_cy),
        ]
        return max(options, key=lambda x: x[1])[0]

    def _spawn_delivery_helicopter(self, vehicle):
        player_cx = self.player.x + self.player.width / 2
        player_cy = self.player.y + self.player.height / 2
        drop_x, drop_y = self._find_drop_tile(player_cx, player_cy)
        edge = self._farthest_edge(player_cx, player_cy)

        hw = HELICOPTER_WIDTH / 2
        hh = HELICOPTER_HEIGHT / 2
        if edge == 'left':
            spawn_x, spawn_y = -hw, drop_y
            direction = 'right'
        elif edge == 'right':
            spawn_x, spawn_y = WORLD_WIDTH + hw, drop_y
            direction = 'left'
        elif edge == 'top':
            spawn_x, spawn_y = drop_x, -hh
            direction = 'down'
        else:
            spawn_x, spawn_y = drop_x, WORLD_HEIGHT + hh
            direction = 'up'

        def on_delivery():
            vehicle.place(drop_x, drop_y)

        h = Helicopter(spawn_x, spawn_y, drop_x, drop_y, direction,
                       vehicle=vehicle, on_hover_complete=on_delivery)
        self.helicopters.add(h)

    def _spawn_player_delivery_helicopter(self):
        target_x = self.player.x + self.player.width / 2
        target_y = self.player.y + self.player.height / 2
        edge = self._farthest_edge(target_x, target_y)

        hw = HELICOPTER_WIDTH / 2
        hh = HELICOPTER_HEIGHT / 2
        if edge == 'left':
            spawn_x, spawn_y = -hw, target_y
            direction = 'right'
        elif edge == 'right':
            spawn_x, spawn_y = WORLD_WIDTH + hw, target_y
            direction = 'left'
        elif edge == 'top':
            spawn_x, spawn_y = target_x, -hh
            direction = 'down'
        else:
            spawn_x, spawn_y = target_x, WORLD_HEIGHT + hh
            direction = 'up'

        def on_delivered():
            self.player.visible = True
            self.player.frozen = False
            self.phase = 'playing'

        h = Helicopter(spawn_x, spawn_y, target_x, target_y, direction,
                       vehicle=None, on_hover_complete=on_delivered)
        self.helicopters.add(h)

    def _start_outro(self):
        self.phase = 'outro'
        self.player.frozen = True
        pygame.mixer.music.fadeout(MUSIC_FADEOUT_MS)
        self._spawn_player_pickup_helicopter_outro()

    def _spawn_player_pickup_helicopter_outro(self):
        vcx = self.player.x + self.player.width / 2
        vcy = self.player.y + self.player.height / 2

        hw = HELICOPTER_WIDTH / 2
        hh = HELICOPTER_HEIGHT / 2
        options = [
            ('left', vcx, -hw, vcy, 'right'),
            ('right', WORLD_WIDTH - vcx, WORLD_WIDTH + hw, vcy, 'left'),
            ('top', vcy, vcx, -hh, 'down'),
            ('bottom', WORLD_HEIGHT - vcy, vcx, WORLD_HEIGHT + hh, 'up'),
        ]
        _, _, spawn_x, spawn_y, direction = min(options, key=lambda o: o[1])

        def on_picked_up():
            self.player.visible = False
            self._outro_picked_up = True

        h = Helicopter(spawn_x, spawn_y, vcx, vcy, direction,
                       vehicle=None, on_hover_complete=on_picked_up)
        self.helicopters.add(h)

    def _update_outro(self, dt):
        self.camera.update(self.player.x, self.player.y,
                           self.player.speed_x, self.player.speed_y, dt)
        if self._outro_picked_up:
            self._fade_alpha = min(
                255.0, self._fade_alpha + (255.0 / HQ_FADE_DURATION) * dt
            )
            if self._fade_alpha >= 255.0:
                for h in self.helicopters:
                    h._stop_audio()
                from app.scenes.game_over_scene import GameOverScene
                self.next_scene = GameOverScene(
                    self.screen, self.clock, "Victory!",
                    background=self.screen.copy(),
                    music_on=self._music_on,
                    landscape=self._landscape,
                    difficulty=self._difficulty,
                )

    def _spawn_pickup_helicopter(self, vehicle):
        vcx = vehicle.x + vehicle.width / 2
        vcy = vehicle.y + vehicle.height / 2

        hw = HELICOPTER_WIDTH / 2
        hh = HELICOPTER_HEIGHT / 2
        options = [
            ('left', vcx, -hw, vcy, 'right'),
            ('right', WORLD_WIDTH - vcx, WORLD_WIDTH + hw, vcy, 'left'),
            ('top', vcy, vcx, -hh, 'down'),
            ('bottom', WORLD_HEIGHT - vcy, vcx, WORLD_HEIGHT + hh, 'up'),
        ]
        _, _, spawn_x, spawn_y, direction = min(options, key=lambda o: o[1])

        def on_pickup():
            if vehicle.destroyed_permanently:
                return
            vehicle.state = MiningVehicle.INACTIVE
            vehicle.delivery_cooldown = MINING_VEHICLE_REDELIVERY_COOLDOWN

        h = Helicopter(spawn_x, spawn_y, vcx, vcy, direction,
                       vehicle=vehicle, on_hover_complete=on_pickup)
        self.helicopters.add(h)
