import pygame
import math
import random

pygame.init()

FRAME_SIZE = 64
NUM_FRAMES = 9

FALLOFF = 1.0

SHEET_WIDTH = FRAME_SIZE * NUM_FRAMES
SHEET_HEIGHT = FRAME_SIZE

sheet = pygame.Surface((SHEET_WIDTH, SHEET_HEIGHT), pygame.SRCALPHA)
random.seed(99)

def soft_circle(surf, color, center, radius, falloff=FALLOFF):
    """Smooth radial gradient circle with alpha blending."""
    if radius < 1:
        return
    r, g, b = color[:3]
    base_a = color[3] if len(color) > 3 else 255
    size = radius * 2 + 2
    temp = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for d in range(radius, 0, -1):
        t = 1.0 - (d / radius) ** falloff
        a = int(base_a * t)
        pygame.draw.circle(temp, (r, g, b, min(255, a)), (c, c), d)
    surf.blit(temp, (center[0] - c, center[1] - c))

def add_glow(surf, center, radius, color, intensity=1.0):
    """Additive-style glow by layering soft circles."""
    r, g, b = color[:3]
    for i in range(3):
        scale = 1.0 + i * 0.5
        alpha = int(80 * intensity / (i + 1))
        if alpha > 0:
            soft_circle(surf, (r, g, b, alpha), center, int(radius * scale), 1.5)

# Pre-calculate debris particles
debris = []
for i in range(20):
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(12, 40)
    size = random.uniform(1.2, 3.5)
    life_start = random.uniform(0.05, 0.25)
    life_end = random.uniform(0.6, 1.0)
    color_r = random.randint(200, 255)
    color_g = random.randint(80, 220)
    debris.append({
        'angle': angle, 'speed': speed, 'size': size,
        'start': life_start, 'end': life_end,
        'cr': color_r, 'cg': color_g
    })

# Smoke puffs
smoke_puffs = []
for i in range(10):
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(6, 18)
    size = random.uniform(8, 16)
    start = random.uniform(0.15, 0.4)
    smoke_puffs.append({
        'angle': angle, 'speed': speed, 'size': size, 'start': start
    })

for f in range(NUM_FRAMES):
    surf = pygame.Surface((FRAME_SIZE, FRAME_SIZE), pygame.SRCALPHA)
    cx, cy = FRAME_SIZE // 2, FRAME_SIZE // 2
    t = f / (NUM_FRAMES - 1)  # 0..1

    # ── LAYER 1: SMOKE (background) ──
    if t > 0.2:
        smoke_progress = (t - 0.2) / 0.8
        for sp in smoke_puffs:
            if t < sp['start']:
                continue
            st = (t - sp['start']) / (1.0 - sp['start'])
            dist = sp['speed'] * st
            sx = cx + math.cos(sp['angle']) * dist
            sy = cy + math.sin(sp['angle']) * dist - st * 5
            r = int(sp['size'] * (0.4 + st * 0.7))
            gray = int(50 + st * 50)
            alpha = int(130 * max(0, 1 - st ** 0.6))
            if alpha > 3 and r > 1:
                soft_circle(surf, (gray, gray, gray + 8, alpha),
                           (int(sx), int(sy)), r, 0.9)

    # ── LAYER 2: MAIN FIREBALL ──
    if t < 0.12:
        # Flash birth
        p = t / 0.12
        r = int(4 + p * 10)
        soft_circle(surf, (255, 255, 220, 255), (cx, cy), r, 0.5)
        add_glow(surf, (cx, cy), r + 4, (255, 220, 100), 1.0)
        # Initial ray burst
        for i in range(6):
            ang = i * math.pi / 3 + 0.4
            length = r + 4 + p * 8
            for d in range(0, int(length), 1):
                alpha = int(200 * (1 - d / length))
                px = cx + math.cos(ang) * d
                py = cy + math.sin(ang) * d
                pygame.draw.circle(surf, (255, 240, 140, alpha), (int(px), int(py)), 1)

    elif t < 0.35:
        # Expanding fireball
        p = (t - 0.12) / 0.23
        expand = 0.5 + 0.5 * math.sin(p * math.pi * 0.5)
        base_r = int(10 + expand * 16)

        # Deep red outer
        soft_circle(surf, (180, 40, 10, int(100 + 60 * (1 - p))),
                   (cx, cy), base_r + 5, 1.3)
        # Orange middle
        soft_circle(surf, (255, 130, 25, int(190 * (1 - p * 0.2))),
                   (cx, cy), base_r, 1.0)
        # Yellow inner
        soft_circle(surf, (255, 210, 60, int(220 * (1 - p * 0.3))),
                   (cx, cy), int(base_r * 0.6), 0.8)
        # White-hot core
        core = int(base_r * 0.25 * (1 - p * 0.5))
        if core > 1:
            soft_circle(surf, (255, 255, 230, int(255 * (1 - p * 0.3))),
                       (cx, cy), core, 0.4)
        add_glow(surf, (cx, cy), base_r, (255, 160, 40), 0.8 * (1 - p * 0.3))

        # Organic flame tendrils
        for i in range(7):
            ang = (i / 7) * 2 * math.pi + p * 0.8
            dist = base_r * (0.6 + 0.5 * random.uniform(0.5, 1.0))
            fx = cx + math.cos(ang) * dist
            fy = cy + math.sin(ang) * dist
            fr = random.randint(3, 6)
            soft_circle(surf, (255, 150 + random.randint(0, 60), 25,
                              int(160 * (1 - p * 0.3))),
                       (int(fx), int(fy)), fr, 0.7)

    elif t < 0.6:
        # Fire breaking apart
        p = (t - 0.35) / 0.25
        
        # Shrinking central fire
        cr = int(12 * (1 - p * 0.8))
        if cr > 2:
            soft_circle(surf, (200, 80, 20, int(140 * (1 - p))),
                       (cx, cy), cr + 3, 1.2)
            soft_circle(surf, (255, 160, 40, int(160 * (1 - p))),
                       (cx, cy), cr, 0.9)
        
        # Breaking fire blobs
        num_blobs = 5
        for i in range(num_blobs):
            ang = (i / num_blobs) * 2 * math.pi + 0.6
            dist = 8 + p * 16
            bx = cx + math.cos(ang) * dist
            by = cy + math.sin(ang) * dist
            br = int(5 * (1 - p * 0.5))
            alpha = int(180 * (1 - p * 0.6))
            if br > 1:
                soft_circle(surf, (255, 130 + random.randint(0, 50), 25, alpha),
                           (int(bx), int(by)), br, 0.7)
                # hot center
                soft_circle(surf, (255, 220, 100, int(alpha * 0.6)),
                           (int(bx), int(by)), max(1, br // 2), 0.5)

    else:
        # Fading embers only
        p = (t - 0.6) / 0.4
        # Tiny residual glow at center
        if p < 0.5:
            soft_circle(surf, (160, 60, 15, int(60 * (1 - p * 2))),
                       (cx, cy), int(5 * (1 - p)), 1.0)

    # ── LAYER 3: FLYING DEBRIS/EMBERS ──
    for db in debris:
        if t < db['start'] or t > db['end']:
            continue
        p = (t - db['start']) / (db['end'] - db['start'])
        dist = db['speed'] * p
        dx = cx + math.cos(db['angle']) * dist
        dy = cy + math.sin(db['angle']) * dist - p * 3
        
        if not (1 < dx < FRAME_SIZE - 1 and 1 < dy < FRAME_SIZE - 1):
            continue
        
        alpha = int(255 * (1 - p ** 0.7))
        size = max(1, int(db['size'] * (1 - p * 0.5)))
        
        # Ember with glow
        soft_circle(surf, (db['cr'], db['cg'], 15, int(alpha * 0.4)),
                   (int(dx), int(dy)), size + 2, 1.0)
        pygame.draw.circle(surf, (db['cr'], min(db['cg'] + 40, 255), 30, alpha),
                          (int(dx), int(dy)), max(1, size))

    sheet.blit(surf, (f * FRAME_SIZE, 0))

# Save spritesheet
pygame.image.save(sheet, "/home/claude/explosion_spritesheet.png")

# === PREVIEW (scaled 2x with checker bg) ===
SC = 2
fw = FRAME_SIZE * SC
pw = fw * NUM_FRAMES
ph = fw + 44
preview = pygame.Surface((pw, ph))
preview.fill((16, 16, 22))

for f in range(NUM_FRAMES):
    # Checker background
    for y in range(0, fw, 10):
        for x in range(0, fw, 10):
            shade = 26 if (x // 10 + y // 10) % 2 == 0 else 36
            pygame.draw.rect(preview, (shade, shade, shade + 3),
                           (f * fw + x, y, 10, 10))
    frame = sheet.subsurface((f * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE))
    scaled = pygame.transform.smoothscale(frame, (fw, fw))
    preview.blit(scaled, (f * fw, 0))
    pygame.draw.rect(preview, (50, 50, 70), (f * fw, 0, fw, fw), 1)

font = pygame.font.SysFont("monospace", 13)
for i in range(NUM_FRAMES):
    label = font.render(f"{i + 1}", True, (140, 140, 170))
    preview.blit(label, (i * fw + fw // 2 - label.get_width() // 2, fw + 4))

info = font.render(f"EXPLOSION  {FRAME_SIZE}x{FRAME_SIZE}  {NUM_FRAMES} frames  transparent bg",
                   True, (100, 100, 140))
preview.blit(info, (pw // 2 - info.get_width() // 2, fw + 22))
pygame.image.save(preview, "/home/claude/explosion_preview.png")

print(f"Sheet: {SHEET_WIDTH}x{SHEET_HEIGHT}, {NUM_FRAMES} frames @ {FRAME_SIZE}x{FRAME_SIZE}")
