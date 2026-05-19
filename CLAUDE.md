# Project: Battle Mission (Pygame)

## Architecture & Best Practices

### Project layout
```
main.py              — entry point: create Game instance and call run()
app/
  settings.py        — all constants (screen, colors, physics, tile/map/base/building config)
  events.py          — EventBus: lightweight synchronous event system
  camera.py          — Camera class (decoupled from entities; supports custom world dims and fixed/follow modes)
  map.py             — Map class: parameterized cols/rows, optional terrain generation, tile collision helpers
  landscape.py       — LandscapeProfile dataclass + presets (STEPPE, MOUNTAINS, SWAMP)
  difficulty.py      — DifficultyProfile dataclass + presets (EASY, NORMAL, HARD)
  collision.py       — collision detection functions (posts events via EventBus)
  hud.py             — HUD class (HP bar, turret/tank/mining-vehicle counters; empty lists hide counters)
  sounds.py          — shared sound helpers
  game.py            — Game class: thin coordinator, owns game loop and scene management
  entities/          — game entity classes
    __init__.py      — re-exports all entity classes
    entity.py        — Entity base class + EntityList container
    player.py        — Player (boundaries read from injected map's world_width/height)
    turret.py        — Turret
    enemy_tank.py    — EnemyTank
    bullet.py        — Bullet
    explosion.py     — Explosion
    missile.py       — Missile (spawns from map edge, flies toward player)
    helicopter.py    — Helicopter (delivers/evacuates mining vehicle)
    mining_vehicle.py — MiningVehicle (fires mining rockets, waits for evac)
    mining_rocket.py — MiningRocket (flies to tile, creates mine on landing)
    building.py      — Building (garage / shop / HQ; HQ has door + interior trigger)
  locations/         — location system (world configuration)
    __init__.py      — re-exports Location, MissionLocation, BaseLocation
    location.py      — Location base: holds map, world dims, player_spawn, camera_follows
    mission_location.py — MissionLocation: random 50×50 map for a chosen landscape/difficulty
    base_location.py — BaseLocation: small flat 24×20 map with garage, shop, HQ
  scenes/            — scene system (state machine)
    __init__.py      — re-exports Scene, TitleScene, GameScene, GameOverScene, BaseScene
    scene.py         — Scene ABC: handle_events(), update(dt), draw(), next_scene
    title_scene.py   — TitleScene: main menu
    game_scene.py    — GameScene: mission gameplay (entities, collisions, mining, missiles)
    game_over_scene.py — GameOverScene: victory → BaseScene; defeat → fresh GameScene
    base_scene.py    — BaseScene: friendly base, fixed camera, fade-out on HQ entry
resources/           — game assets
  images/
    player/          — player tank sprites
    enemy_tank/      — enemy tank sprites + destroyed
    turret/          — turret sprites + destroyed
    bullet/          — shell sprite
    effects/         — explosion spritesheet
    mines/           — mine tile textures
    mining_vehicle/  — mining vehicle sprites + HUD icons
    textures/        — terrain tile textures (grass, rock, water)
    ui/              — title screen, game over, victory images
  music/             — background music
  sounds/            — shoot and other SFX
  concepts/          — concept art (not used in code)
utils/               — offline helpers (e.g., explosion spritesheet generator)
```
Only `main.py` lives at the project root. All game code goes inside `app/`.

### Scene system
The game uses a scene state machine. `Game` owns the loop and delegates to the active `Scene`.
Each scene implements `handle_events()`, `update(dt)`, `draw()`. Transition happens by setting `next_scene`.
Gameplay logic (entities, collisions, HUD) lives in the active scene, not in `Game`.

Scene flow:
```
TitleScene ──Start──► GameScene (mission)
                         │ victory ──► GameOverScene ──Enter──► BaseScene
                         │                                       │
                         │ defeat  ──► GameOverScene ──Enter──► GameScene (fresh)
                         │                                       │
                         └◄─── drive into HQ, fade ──────────────┘
```

When transitioning from `BaseScene` to a new mission, a random landscape is chosen but the originally selected difficulty is preserved. Player HP is restored to max on entering the base.

### Location system
A `Location` encapsulates the world where action happens: its map, world dimensions, player spawn point, and camera mode. There are two types:

- `MissionLocation(landscape, difficulty)` — random 50×50 map with terrain generation, scrolling camera.
- `BaseLocation()` — small 24×20 flat map (camera-sized, no scrolling), holds three `Building` instances: `garage`, `shop`, `hq`.

`Map(profile=None, cols=None, rows=None)` skips terrain generation when `profile is None` (used by the base). Map exposes `cols`, `rows`, `world_width`, `world_height`. `Camera(world_width, world_height, follow=True)` supports a fixed mode (`follow=False`) where the camera stays at (0,0) but shake still works.

### Buildings and HQ entry
`Building` is an `Entity` with `kind` ∈ {`garage`, `shop`, `hq`}. Garage and shop are solid blockers (single rect). HQ is composed of multiple wall rects with a bottom-center door gap and an `interior_rect`. Building exposes:
- `get_blocker_rects()` — list of `pygame.Rect` used by Player's collision logic
- `player_fully_inside(player_rect)` — True only when the player rect is fully contained in `interior_rect` (HQ only)

`BaseScene` polls `location.hq.player_fully_inside(...)` each frame. When true, it starts a fade-out (black overlay alpha 0→255 over `HQ_FADE_DURATION`) and then transitions to a new `GameScene` with a randomly chosen landscape, the same difficulty, and `player_hp=PLAYER_MAX_HP`.

### Game class pattern
`Game` is a thin coordinator: initializes pygame, runs the main loop, and switches scenes.
No module-level mutable state or globals — everything lives inside Game/Scene or is passed explicitly.
Collisions post events via EventBus; `GameScene` handles them in `_on_*` methods.

### Game loop structure
The game loop must follow three clear phases:
```
handle_events()  — process input and pygame events
update(dt)       — update game logic (physics, movement, camera)
draw()           — render everything to screen
```
Keep each phase in its own method. Do not mix input handling with rendering.

### Delta time
Pass `dt` (seconds since last frame) into `update()` and use it for all movement/physics calculations.
This makes the game frame-rate independent.
```python
dt = clock.tick(FPS) / 1000.0
```

### Mining system (mission only)
`GameScene` owns the full mining lifecycle:
- `self.mining_vehicles` — plain list of 2 `MiningVehicle` instances (never pruned; state tracks lifecycle)
- `self.helicopters` — `EntityList` of active helicopters (delivery and pickup)
- `self.mining_rockets` — `EntityList` of in-flight mining rockets
- `self.mines` — `dict` mapping `(col, row)` tile coordinates to sprite index

`MiningVehicle` states: `INACTIVE → SHOOTING → MOVING_AWAY → WAITING_FOR_PICKUP → INACTIVE` (cycle) or `DESTROYED` (permanent).
`Helicopter` states: `FLYING_IN → HOVERING → FLYING_OUT`. Mode passed via `on_hover_complete` callback.

Delivery helicopter spawns from the edge **farthest** from the player; pickup helicopter spawns from the edge **closest** to the vehicle, aligned on the same vertical or horizontal.

Mines block only `GROUND` tiles. Player driving over a mine loses `MINE_DAMAGE` HP; mine disappears. Mining vehicles are destroyable by player bullets but do not count toward the victory condition.

The mining system, missiles, and enemy spawning are **mission-only**. `BaseScene` is purely traversal — no shooting, no enemies, no missiles, HUD shows only the HP bar.

### General rules
- Keep imports explicit — avoid `from module import *`
- Resources (images, sounds) are loaded in `__init__` methods or a dedicated loading phase, not at module level
- All entities inherit from `Entity` base class with uniform `update(dt)`, `draw(surface, camera)`, `get_rect()`
- Dependencies (game_map, target) are injected via constructor, not passed through `update()`
- Constants go in `settings.py`, not scattered across files
- `MiningVehicle` uses a plain list (not `EntityList`) because all 2 instances must persist for HUD display even after destruction
- World boundaries are read from the injected `Map` instance (`game_map.world_width/height`), not from settings, so entities work in any location size
