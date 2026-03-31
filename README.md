# Battle Mission

Pygame-эксперимент: вид сверху, тайловая карта, сущности, HUD.

## Требования

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — менеджер пакетов и окружений
- Python 3.12.12 (uv установит автоматически)

## Развёртывание для разработки

### Linux

```bash
# Клонировать репозиторий
git clone git@github.com:theodor85/battle_mission.git
cd battle_mission

# Создать виртуальное окружение и установить зависимости
uv sync

# Запустить игру
uv run main.py
```

### Windows

```powershell
# Клонировать репозиторий
git clone git@github.com:theodor85/battle_mission.git
cd battle_mission

# Создать виртуальное окружение и установить зависимости
uv sync

# Запустить игру
uv run main.py
```

> uv автоматически скачает нужную версию Python, если она не установлена в системе.

## Структура проекта

```
main.py          — точка входа
app/
  game.py        — игровой цикл
  settings.py    — константы
  camera.py      — камера
  map.py         — карта и тайлы
  hud.py         — HUD (HP, счётчики)
  collision.py   — обнаружение столкновений
  events.py      — EventBus
  entities/      — игровые сущности (Player, Turret, Bullet, Explosion)
  scenes/        — сцены (TitleScene и др.)
resources/       — изображения, звуки
```
