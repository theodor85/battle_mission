from app.settings import BULLET_DAMAGE


def check_collisions(player, player_bullets, enemy_bullets, turrets, events):
    _bullets_vs_turrets(player_bullets, turrets, events)
    _bullets_vs_player(enemy_bullets, player, events)
    _bullets_vs_rocks(player_bullets, enemy_bullets, events)


def _bullets_vs_turrets(bullets, turrets, events):
    for turret in turrets:
        if not turret.alive:
            continue
        trect = turret.get_rect()
        for b in bullets:
            if not b.alive:
                continue
            if trect.colliderect(b.get_rect()):
                b.alive = False
                events.post("turret_destroyed",
                            turret=turret,
                            x=turret.x + turret.width / 2,
                            y=turret.y + turret.height / 2)


def _bullets_vs_player(bullets, player, events):
    prect = player.get_rect()
    for b in bullets:
        if not b.alive:
            continue
        if prect.colliderect(b.get_rect()):
            b.alive = False
            events.post("player_hit",
                        damage=BULLET_DAMAGE,
                        x=b.x + b.width / 2,
                        y=b.y + b.height / 2)


def _bullets_vs_rocks(player_bullets, enemy_bullets, events):
    for b in list(player_bullets) + list(enemy_bullets):
        if not b.alive and b.hit_pos is not None:
            events.post("bullet_hit_rock",
                        x=b.hit_pos[0] + b.width / 2,
                        y=b.hit_pos[1] + b.height / 2)
