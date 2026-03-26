# Project: Moving Exp (Pygame)

## Architecture & Best Practices

### Project layout
```
main.py              — entry point: create Game instance and call run()
app/
  settings.py        — all constants (screen dimensions, colors, physics, tile/map config)
  events.py          — EventBus: lightweight synchronous event system
  camera.py          — Camera class (decoupled from entities)
  map.py             — map generation, tile collision helpers, tile drawing
  entities/          — game entity classes
    __init__.py      — re-exports Entity, EntityList, Player, Turret, Bullet, Explosion
    entity.py        — Entity base class + EntityList container
    player.py        — Player
    turret.py        — Turret
    bullet.py        — Bullet
    explosion.py     — Explosion
  collision.py       — collision detection functions (posts events via EventBus)
  hud.py             — HUD class (HP bar, turret counter)
  game.py            — Game class: thin coordinator, owns game loop and event wiring
resources/           — images, sounds, and other assets
```
Only `main.py` lives at the project root. All game code goes inside `app/`.

### Game class pattern
Wrap the game loop in a `Game` class. It coordinates subsystems (map, camera, HUD, entities, collisions).
No module-level mutable state or globals — everything lives inside Game or is passed explicitly.
Collisions post events via EventBus; Game handles them in `_on_*` methods.

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

### General rules
- Keep imports explicit — avoid `from module import *`
- Resources (images, sounds) are loaded in `__init__` methods or a dedicated loading phase, not at module level
- All entities inherit from `Entity` base class with uniform `update(dt)`, `draw(surface, camera)`, `get_rect()`
- Dependencies (game_map, target) are injected via constructor, not passed through `update()`
- Constants go in `settings.py`, not scattered across files
