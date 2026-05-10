# Project: Battle Mission (Pygame)

## Architecture & Best Practices

### Project layout
```
main.py              — entry point: create Game instance and call run()
app/
  settings.py        — all constants (screen dimensions, colors, physics, tile/map config)
  events.py          — EventBus: lightweight synchronous event system
  camera.py          — Camera class (decoupled from entities)
  map.py             — map generation, tile collision helpers, tile drawing
  landscape.py       — LandscapeProfile dataclass + presets (STEPPE, MOUNTAINS, SWAMP)
  collision.py       — collision detection functions (posts events via EventBus)
  hud.py             — HUD class (HP bar, turret/tank/mining-vehicle counters)
  game.py            — Game class: thin coordinator, owns game loop and scene management
  entities/          — game entity classes
    __init__.py      — re-exports all entity classes
    entity.py        — Entity base class + EntityList container
    player.py        — Player
    turret.py        — Turret
    enemy_tank.py    — EnemyTank
    bullet.py        — Bullet
    explosion.py     — Explosion
    missile.py       — Missile (spawns from map edge, flies toward player)
    helicopter.py    — Helicopter (delivers/evacuates mining vehicle)
    mining_vehicle.py — MiningVehicle (fires mining rockets, waits for evac)
    mining_rocket.py — MiningRocket (flies to tile, creates mine on landing)
  scenes/            — scene system (state machine)
    __init__.py      — re-exports Scene, TitleScene, GameScene, GameOverScene
    scene.py         — Scene ABC: handle_events(), update(dt), draw(), next_scene
    title_scene.py   — TitleScene: main menu
    game_scene.py    — GameScene: gameplay logic, entity management, collisions
    game_over_scene.py — GameOverScene: victory/defeat screen
resources/           — game assets
  images/
    player/          — player tank sprites
    enemy_tank/      — enemy tank sprites + destroyed
    turret/          — turret sprites + destroyed
    bullet/          — shell sprite
    effects/         — explosion spritesheet
    ui/              — title screen, game over, victory images
  music/             — background music
  concepts/          — concept art (not used in code)
```
Only `main.py` lives at the project root. All game code goes inside `app/`.

### Scene system
The game uses a scene state machine. `Game` owns the loop and delegates to the active `Scene`.
Each scene implements `handle_events()`, `update(dt)`, `draw()`. Transition happens by setting `next_scene`.
Gameplay logic (entities, collisions, HUD) lives in `GameScene`, not in `Game`.

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

### Mining system
`GameScene` owns the full mining lifecycle:
- `self.mining_vehicles` — plain list of 2 `MiningVehicle` instances (never pruned; state tracks lifecycle)
- `self.helicopters` — `EntityList` of active helicopters (delivery and pickup)
- `self.mining_rockets` — `EntityList` of in-flight mining rockets
- `self.mines` — `set` of `(col, row)` tile coordinates with placed mines

`MiningVehicle` states: `INACTIVE → SHOOTING → MOVING_AWAY → WAITING_FOR_PICKUP → INACTIVE` (cycle) or `DESTROYED` (permanent).
`Helicopter` states: `FLYING_IN → HOVERING → FLYING_OUT`. Mode passed via `on_hover_complete` callback.

Delivery helicopter spawns from the edge **farthest** from the player; pickup helicopter spawns from the edge **closest** to the vehicle, aligned on the same vertical or horizontal.

Mines block only `GROUND` tiles. Player driving over a mine loses `MINE_DAMAGE` HP; mine disappears. Mining vehicles are destroyable by player bullets but do not count toward the victory condition.

### General rules
- Keep imports explicit — avoid `from module import *`
- Resources (images, sounds) are loaded in `__init__` methods or a dedicated loading phase, not at module level
- All entities inherit from `Entity` base class with uniform `update(dt)`, `draw(surface, camera)`, `get_rect()`
- Dependencies (game_map, target) are injected via constructor, not passed through `update()`
- Constants go in `settings.py`, not scattered across files
- `MiningVehicle` uses a plain list (not `EntityList`) because all 2 instances must persist for HUD display even after destruction
