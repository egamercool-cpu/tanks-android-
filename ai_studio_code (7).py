import pygame
import math
import random
import array

# --- ИНИЦИАЛИЗАЦИЯ ---
pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
except:
    pass

info = pygame.display.Info()
REAL_W, REAL_H = info.current_w, info.current_h

GAME_W = 426
GAME_H = 240

SCREEN = pygame.display.set_mode((REAL_W, REAL_H), pygame.FULLSCREEN)
DISPLAY = pygame.Surface((GAME_W, GAME_H))
CLOCK = pygame.time.Clock()

SCALE = min(REAL_W / GAME_W, REAL_H / GAME_H)
OFFSET_X = (REAL_W - GAME_W * SCALE) / 2
OFFSET_Y = (REAL_H - GAME_H * SCALE) / 2

# --- НАСТРОЙКИ ---
SETTINGS = {"SOUND": True, "VIBRATION": True, "PARTICLES": True}

# --- ЗВУКИ ---
def generate_sound(freq_start, freq_end, duration, volume=0.5):
    if not pygame.mixer.get_init(): return None
    n_samples = int(44100 * duration)
    buf = array.array('h')
    for i in range(n_samples):
        t = i / n_samples
        freq = freq_start + (freq_end - freq_start) * t
        phase = (i * freq / 44100) * 2 * math.pi
        sample = 32767 * volume if math.sin(phase) > 0 else -32767 * volume
        sample *= (1 - t)
        buf.append(int(sample))
    return pygame.mixer.Sound(buffer=buf)

try:
    SND_SHOOT = generate_sound(800, 400, 0.1, 0.3)
    SND_EXPLODE = generate_sound(100, 50, 0.3, 0.5)
    SND_HIT = generate_sound(400, 200, 0.1, 0.4)
    SND_POWERUP = generate_sound(600, 1200, 0.3, 0.4)
except:
    SND_SHOOT = None

def play_sound(snd):
    if SETTINGS["SOUND"] and snd:
        try: snd.play()
        except: pass

# --- ЦВЕТА ---
C_BG = (10, 10, 15)
C_GRID = (20, 20, 30)
C_PLAYER_BODY = (180, 140, 0)
C_PLAYER_TURRET = (255, 200, 0)
C_CORE_OUTER = (40, 80, 200)
C_FIRE = (255, 100, 0)
C_UI_BG = (40, 40, 50)
C_WHITE = (255, 255, 255)
C_RED = (255, 80, 80)
C_GREEN = (80, 255, 80)
C_SPIDER = (20, 20, 20)
C_GHOST = (220, 230, 255)
C_DRAGON = (140, 20, 20)
C_ARCHER = (34, 139, 34)
C_GOLEM = (105, 105, 105)
C_LICH = (75, 0, 130)

FONT = pygame.font.SysFont("monospace", 10, bold=True)
FONT_BIG = pygame.font.SysFont("monospace", 20, bold=True)

# --- РИСОВАНИЕ ---

def draw_tank(s, x, y, aim_vec, recoil, flash):
    c = (255, 255, 255) if flash else C_PLAYER_BODY
    cx, cy = x + 8, y + 8
    
    # Гусеницы
    offset = (pygame.time.get_ticks() // 50) % 4
    pygame.draw.rect(s, (80, 80, 80), (x+1, y+1, 14, 14))
    for i in range(0, 16, 4):
        pos = (i + offset) % 14
        pygame.draw.rect(s, (20,20,20), (x+2, y+1+pos, 2, 1))
        pygame.draw.rect(s, (20,20,20), (x+14, y+1+pos, 2, 1))
    
    # Корпус
    pygame.draw.rect(s, c, (x+4, y+2, 8, 12))
    
    # Башня
    angle = math.atan2(aim_vec[1], aim_vec[0])
    gun_len = 10 if recoil < 2 else 7
    tip_x = cx + math.cos(angle) * gun_len
    tip_y = cy + math.sin(angle) * gun_len
    
    pygame.draw.line(s, (150, 150, 150), (cx, cy), (tip_x, tip_y), 4)
    turret_col = (255,255,255) if flash else C_PLAYER_TURRET
    pygame.draw.circle(s, turret_col, (cx, cy), 5)
    pygame.draw.circle(s, (200, 100, 0), (cx, cy), 2)
    
    if recoil > 3:
        fx = cx + math.cos(angle) * 14
        fy = cy + math.sin(angle) * 14
        pygame.draw.circle(s, (255, 255, 100), (fx, fy), random.randint(3, 5))

def draw_spider(s, x, y, flash):
    c = (255, 255, 255) if flash else C_SPIDER
    cx, cy = x+8, y+8
    t = pygame.time.get_ticks() * 0.02
    for i in range(4):
        ox = math.sin(t + i) * 3
        oy = math.cos(t + i) * 3
        pygame.draw.line(s, (80,80,80), (cx, cy), (x-4+ox, y+(i*4)+oy), 1)
        pygame.draw.line(s, (80,80,80), (cx, cy), (x+20-ox, y+(i*4)+oy), 1)
    pygame.draw.circle(s, c, (cx, cy), 6)
    if not flash:
        pygame.draw.circle(s, (255,0,0), (cx-2, cy-2), 1)
        pygame.draw.circle(s, (255,0,0), (cx+2, cy-2), 1)

def draw_ghost(s, x, y, flash):
    c = (255, 255, 255) if flash else C_GHOST
    y_off = math.sin(pygame.time.get_ticks() * 0.005) * 2
    pygame.draw.circle(s, c, (x+8, y+6+y_off), 7)
    pygame.draw.rect(s, c, (x+1, y+6+y_off, 14, 8))
    for i in range(0, 15, 3):
        h_var = math.sin(pygame.time.get_ticks()*0.02 + i)*2
        pygame.draw.line(s, c, (x+1+i, y+13+y_off), (x+1+i, y+16+y_off+h_var), 2)
    if not flash:
        pygame.draw.rect(s, (50,50,150), (x+4, y+5+y_off, 2, 3))
        pygame.draw.rect(s, (50,50,150), (x+10, y+5+y_off, 2, 3))

def draw_dragon(s, x, y, flash):
    c = (255, 255, 255) if flash else C_DRAGON
    wing_c = (200, 200, 200) if flash else (100, 10, 10)
    t = pygame.time.get_ticks() * 0.01
    w_flap = math.sin(t) * 8
    pygame.draw.polygon(s, wing_c, [(x+12, y+10), (x-4, y+4+w_flap), (x+2, y+20)])
    pygame.draw.polygon(s, wing_c, [(x+12, y+10), (x+28, y+4+w_flap), (x+22, y+20)])
    pygame.draw.circle(s, c, (x+12, y+12), 8)
    pygame.draw.circle(s, c, (x+12, y+20), 5)
    pygame.draw.line(s, c, (x+12, y+20), (x+12+math.sin(t)*5, y+28), 3)
    head_y = y + 4 + math.sin(t*2)*2
    pygame.draw.rect(s, c, (x+9, head_y, 6, 8))

def draw_archer(s, x, y, flash, angle_to_player, phase):
    c = (255, 255, 255) if flash else C_ARCHER
    if phase == 2 and not flash: c = (100, 0, 0)
    cx, cy = x+10, y+10
    pygame.draw.circle(s, c, (cx, cy), 9)
    pygame.draw.circle(s, (20, 100, 20), (cx, cy-2), 6)
    bow_dist = 8
    lx = cx + math.cos(angle_to_player) * bow_dist
    ly = cy + math.sin(angle_to_player) * bow_dist
    perp = angle_to_player + math.pi/2
    p1x = lx + math.cos(perp) * 8; p1y = ly + math.sin(perp) * 8
    p2x = lx - math.cos(perp) * 8; p2y = ly - math.sin(perp) * 8
    pygame.draw.line(s, (139, 69, 19), (p1x, p1y), (p2x, p2y), 2)
    pygame.draw.line(s, (200, 200, 200), (p1x, p1y), (cx, cy), 1)
    pygame.draw.line(s, (200, 200, 200), (p2x, p2y), (cx, cy), 1)

def draw_golem(s, x, y, flash, phase):
    c = (255, 255, 255) if flash else C_GOLEM
    pygame.draw.rect(s, c, (x, y, 32, 28), border_radius=5)
    crack_col = (255, 100, 0) if phase == 2 else (50, 50, 50)
    if not flash:
        pygame.draw.line(s, crack_col, (x+5, y+5), (x+10, y+15), 1)
        pygame.draw.line(s, crack_col, (x+25, y+20), (x+20, y+10), 1)
    eye_c = (255, 50, 50) if not flash else (255, 200, 200)
    pygame.draw.rect(s, eye_c, (x+8, y+8, 4, 2))
    pygame.draw.rect(s, eye_c, (x+20, y+8, 4, 2))

def draw_lich(s, x, y, flash, phase):
    c = (255, 255, 255) if flash else C_LICH
    cx, cy = x+12, y+12
    if phase == 2 and not flash:
        pygame.draw.circle(s, (0, 255, 0), (cx, cy), 16, 1)
    pygame.draw.polygon(s, c, [(x+4, y), (x+20, y), (x+24, y+24), (x, y+24)])
    pygame.draw.circle(s, (220, 220, 220), (cx, cy-4), 6)
    eye_col = (0, 255, 0) if phase == 2 else (200, 0, 200)
    pygame.draw.rect(s, eye_col, (cx-3, cy-5, 2, 2))
    pygame.draw.rect(s, eye_col, (cx+1, cy-5, 2, 2))
    pygame.draw.line(s, (100, 50, 0), (x, y+4), (x, y+20), 2)
    pygame.draw.circle(s, eye_col, (x, y+4), 3)

# --- ЧАСТИЦЫ ---
particles = []
def add_particles(x, y, color, count=5):
    if not SETTINGS["PARTICLES"]: return
    for _ in range(count):
        vx = random.uniform(-2, 2)
        vy = random.uniform(-2, 2)
        life = random.randint(10, 30)
        particles.append([x, y, vx, vy, life, color, random.randint(1, 3)])

def update_draw_particles(s):
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 1
        if p[4] <= 0:
            particles.remove(p)
        else:
            pygame.draw.rect(s, p[5], (p[0], p[1], p[6], p[6]))

# --- СУЩНОСТИ ---

class Hazard:
    def __init__(self, x, y, damage):
        self.x = x; self.y = y; self.damage = damage
        self.timer = 60; self.exploded = False; self.radius = 25
    def update(self, player):
        if self.exploded: return False
        self.timer -= 1
        if self.timer <= 0:
            self.exploded = True
            play_sound(SND_EXPLODE)
            add_particles(self.x, self.y, C_FIRE, 15)
            if math.hypot(player.x - self.x, player.y - self.y) < self.radius: return True
        return False
    def draw(self, s):
        progress = 1 - (self.timer / 60)
        radius = int(self.radius * progress)
        pygame.draw.circle(s, (50, 0, 0), (int(self.x), int(self.y)), self.radius, 1)
        pygame.draw.circle(s, (255, 50, 0), (int(self.x), int(self.y)), radius, 1)

class Entity:
    def __init__(self, x, y, type, boss_tier=0):
        self.x = x; self.y = y; self.type = type
        self.flash = 0; self.vx = 0; self.vy = 0
        
        # Обычные
        if type == 'spider': self.w=16; self.h=16; self.hp=2; self.speed=0.6; self.score=1
        elif type == 'ghost': self.w=16; self.h=16; self.hp=3; self.speed=0.4; self.score=2
        elif type == 'dragon': self.w=24; self.h=24; self.hp=6; self.speed=0.25; self.score=3; self.reload=100
        
        # БОССЫ
        elif type == 'archer':
            self.w=20; self.h=20; self.max_hp=500 + (boss_tier*100); self.hp=self.max_hp; self.speed=0.8; self.score=500
            self.reload=80; self.phase=1; self.melee_cd=0; self.special_cd=200
        elif type == 'golem':
            self.w=32; self.h=28; self.max_hp=500 + (boss_tier*100); self.hp=self.max_hp; self.speed=0.25; self.score=500
            self.reload=150; self.phase=1
        elif type == 'lich':
            self.w=24; self.h=24; self.max_hp=500 + (boss_tier*100); self.hp=self.max_hp; self.speed=0.4; self.score=500
            self.reload=120; self.phase=1; self.summon_cd=300

    def get_rect(self): return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, s, px, py):
        if self.flash > 0: self.flash -= 1
        is_flash = self.flash > 0
        if self.type == 'spider': draw_spider(s, self.x, self.y, is_flash)
        elif self.type == 'ghost': draw_ghost(s, self.x, self.y, is_flash)
        elif self.type == 'dragon': draw_dragon(s, self.x, self.y, is_flash)
        elif self.type == 'archer':
            angle = math.atan2(py - self.y, px - self.x)
            draw_archer(s, self.x, self.y, is_flash, angle, self.phase)
        elif self.type == 'golem': draw_golem(s, self.x, self.y, is_flash, self.phase)
        elif self.type == 'lich': draw_lich(s, self.x, self.y, is_flash, self.phase)

def draw_btn(s, rect, text):
    pygame.draw.rect(s, C_UI_BG, rect, border_radius=4)
    pygame.draw.rect(s, C_WHITE, rect, 1, border_radius=4)
    t = FONT.render(text, True, C_WHITE)
    s.blit(t, (rect.centerx-t.get_width()//2, rect.centery-t.get_height()//2))

# --- MAIN ---
def main():
    touches = {}
    state = "MENU"
    
    px, py = GAME_W//2, GAME_H//2
    p_hp = 100; p_dmg = 1; p_speed = 1.3; p_reload = 20
    p_timer = 0; p_recoil = 0; p_aim = (1, 0)
    
    bullets = []; enemies = []; balls = []; arrows = []; hazards = []
    
    wave = 1; to_spawn = 0; wave_kills = 0; spawn_cd = 0; core_hp = 10
    boss_count = 0
    
    # UI
    btn_start = pygame.Rect(GAME_W//2 - 100, GAME_H//2, 80, 25)
    btn_settings = pygame.Rect(GAME_W//2 + 20, GAME_H//2, 80, 25)
    
    btn_snd = pygame.Rect(GAME_W//2 - 60, 80, 120, 20)
    btn_vib = pygame.Rect(GAME_W//2 - 60, 110, 120, 20)
    btn_back = pygame.Rect(GAME_W//2 - 60, 150, 120, 20)
    c1_rect = pygame.Rect(GAME_W//2 - 110, 60, 100, 120)
    c2_rect = pygame.Rect(GAME_W//2 + 10, 60, 100, 120)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            
            if e.type == pygame.FINGERDOWN:
                x, y = e.x * REAL_W, e.y * REAL_H
                fid = e.finger_id
                mx = (x - OFFSET_X) / SCALE; my = (y - OFFSET_Y) / SCALE
                
                if state == "GAME":
                    ttype = 'move' if x < REAL_W/2 else 'shoot'
                    if not any(t['type'] == ttype for t in touches.values()):
                        touches[fid] = {'type': ttype, 'start':(x,y), 'cur':(x,y), 'vec':(0,0)}
                
                elif state == "MENU":
                    if btn_start.collidepoint(mx, my):
                        px,py = GAME_W//2, GAME_H//2
                        bullets.clear(); enemies.clear(); balls.clear(); particles.clear(); arrows.clear(); hazards.clear()
                        wave = 1; core_hp = 10; to_spawn = 6; wave_kills = 0; boss_count = 0
                        p_aim = (1,0)
                        state = "GAME"
                        play_sound(SND_POWERUP)
                    elif btn_settings.collidepoint(mx, my):
                        state = "SETTINGS"

                elif state == "SETTINGS":
                    if btn_snd.collidepoint(mx,my): SETTINGS["SOUND"] = not SETTINGS["SOUND"]
                    elif btn_vib.collidepoint(mx,my): SETTINGS["VIBRATION"] = not SETTINGS["VIBRATION"]
                    elif btn_back.collidepoint(mx,my): state = "MENU"

                elif state == "UPGRADE":
                    chosen = False
                    if c1_rect.collidepoint(mx,my): p_dmg += 1; chosen = True
                    elif c2_rect.collidepoint(mx,my): p_reload = max(8, p_reload - 3); chosen = True
                    if chosen:
                        play_sound(SND_POWERUP)
                        wave += 1
                        if wave % 5 == 0: to_spawn = 1
                        else: to_spawn = 6 + wave
                        wave_kills = 0; touches.clear()
                        state = "GAME"
                elif state == "GAMEOVER": state = "MENU"

            elif e.type == pygame.FINGERMOTION:
                if e.finger_id in touches:
                    t = touches[e.finger_id]
                    t['cur'] = (e.x*REAL_W, e.y*REAL_H)
                    dx = t['cur'][0] - t['start'][0]; dy = t['cur'][1] - t['start'][1]
                    dist = math.hypot(dx, dy)
                    if dist > 10:
                        scale = 1 if dist <= 80 else 80/dist
                        t['vec'] = (dx*scale/80, dy*scale/80)
                    else: t['vec'] = (0,0)

            elif e.type == pygame.FINGERUP:
                if e.finger_id in touches: del touches[e.finger_id]

        # --- LOGIC ---
        if state == "GAME":
            mv = (0,0); sv = (0,0)
            for t in touches.values():
                if t['type']=='move': mv = t['vec']
                if t['type']=='shoot': sv = t['vec']
            if sv != (0,0): p_aim = sv
            
            if p_hp < 100: p_hp += 0.05
            
            px += mv[0] * p_speed; py += mv[1] * p_speed
            px = max(0, min(GAME_W-16, px)); py = max(0, min(GAME_H-16, py))
            
            if p_recoil > 0: p_recoil -= 1
            if p_timer > 0: p_timer -= 1
            elif sv != (0,0):
                play_sound(SND_SHOOT)
                bullets.append([px+8, py+8, p_aim[0]*4, p_aim[1]*4, 80])
                p_timer = p_reload; p_recoil = 5
            
            # SPAWN
            if to_spawn > 0:
                spawn_cd -= 1
                if spawn_cd <= 0:
                    spawn_cd = 80
                    to_spawn -= 1
                    side = random.randint(0,3)
                    if side==0: ex,ey = random.randint(0,GAME_W), -30
                    elif side==1: ex,ey = random.randint(0,GAME_W), GAME_H+30
                    elif side==2: ex,ey = -30, random.randint(0,GAME_H)
                    else: ex,ey = GAME_W+30, random.randint(0,GAME_H)
                    
                    if wave % 5 == 0:
                        boss_index = (wave // 5) - 1
                        boss_type_idx = boss_index % 3
                        if boss_type_idx == 0: et = 'archer'
                        elif boss_type_idx == 1: et = 'golem'
                        else: et = 'lich'
                        enemies.append(Entity(ex, ey, et, boss_index))
                    else:
                        r = random.random()
                        if r<0.33: et='spider'
                        elif r<0.66: et='ghost'
                        else: et='dragon'
                        enemies.append(Entity(ex, ey, et))

            elif len(enemies) == 0:
                hazards.clear()
                state = "UPGRADE"; touches.clear()
            
            for h in hazards[:]:
                hit = h.update(pygame.Rect(px, py, 16, 16))
                if hit:
                    p_hp -= 20
                    play_sound(SND_HIT)
                    dx = px - h.x; dy = py - h.y
                    dist = math.hypot(dx, dy)
                    if dist > 0: px += (dx/dist)*20; py += (dy/dist)*20
                if h.exploded and h.timer < -20: hazards.remove(h)

            for b in bullets[:]:
                b[0] += b[2]
                b[1] += b[3]
                b[4] -= 1
                if b[4] <= 0:
                    bullets.remove(b)

            for a in arrows[:]:
                a[0] += a[2]
                a[1] += a[3]
                a[4] -= 1
                if pygame.Rect(px, py, 16, 16).collidepoint(a[0], a[1]):
                    add_particles(px+8, py+8, C_RED, 3)
                    arrows.remove(a)
                elif a[4] <= 0:
                    arrows.remove(a)

            cx, cy = GAME_W//2, GAME_H//2
            boss_exists = False; boss_hp_percent = 0
            
            for e in enemies[:]:
                if e.type in ['archer', 'golem', 'lich']: 
                    boss_exists = True; boss_hp_percent = e.hp / e.max_hp

                dx, dy = cx - e.x, cy - e.y
                dist_core = math.hypot(dx, dy)
                if dist_core==0: dist_core=1
                nx, ny = dx/dist_core, dy/dist_core
                
                dx_p, dy_p = px - e.x, py - e.y
                dist_p = math.hypot(dx_p, dy_p)
                if dist_p == 0: dist_p = 1
                nx_p, ny_p = dx_p/dist_p, dy_p/dist_p

                if e.type == 'spider': e.x+=nx*e.speed; e.y+=ny*e.speed
                elif e.type == 'ghost':
                    if dist_core<70: e.x+=-ny*e.speed; e.y+=nx*e.speed
                    else: e.x+=nx*e.speed; e.y+=ny*e.speed
                elif e.type == 'dragon':
                    if dist_core<110:
                        e.reload-=1
                        if e.reload<=0: e.reload=200; balls.append([e.x+12, e.y+12, nx*0.9, ny*0.9])
                    else: e.x+=nx*e.speed; e.y+=ny*e.speed
                
                # --- BOSS AI ---
                elif e.type == 'archer':
                    if e.hp <= e.max_hp * 0.5: e.phase = 2
                    if e.melee_cd > 0: e.melee_cd -= 1
                    if dist_p < 40 and e.melee_cd <= 0:
                        if dist_p > 0: px += nx_p * 40; py += ny_p * 40
                        e.melee_cd = 100
                        add_particles(px, py, C_WHITE, 5)
                    
                    if dist_p < 100: e.x -= nx_p * e.speed; e.y -= ny_p * e.speed
                    elif dist_p > 150: e.x += nx_p * e.speed; e.y += ny_p * e.speed
                    
                    e.reload -= 1
                    if e.reload <= 0:
                        arrows.append([e.x+10, e.y+10, nx_p*3, ny_p*3, 100])
                        e.reload = 60 if e.phase == 1 else 40
                    
                    if e.phase == 2:
                        e.special_cd -= 1
                        if e.special_cd <= 0:
                            e.special_cd = 180
                            for _ in range(3):
                                hx = px + random.randint(-40, 40); hy = py + random.randint(-40, 40)
                                hazards.append(Hazard(hx, hy, 1))

                elif e.type == 'golem':
                    if e.hp <= e.max_hp * 0.5: e.phase = 2
                    e.x += nx_p * e.speed; e.y += ny_p * e.speed
                    e.reload -= 1
                    if e.reload <= 0:
                        e.reload = 200
                        if e.phase == 1:
                            balls.append([e.x+16, e.y+14, nx_p*1.5, ny_p*1.5, True])
                        else:
                            for i in range(8):
                                ang = i * (math.pi/4)
                                balls.append([e.x+16, e.y+14, math.cos(ang)*2, math.sin(ang)*2, True])

                elif e.type == 'lich':
                    if e.hp <= e.max_hp * 0.5: e.phase = 2
                    if dist_p < 80: e.x -= nx_p * e.speed; e.y -= ny_p * e.speed
                    else: e.x += nx_p * e.speed; e.y += ny_p * e.speed
                    
                    e.reload -= 1
                    if e.reload <= 0:
                        e.reload = 120
                        if e.phase == 2: balls.append([e.x+12, e.y+12, nx_p, ny_p])
                        else: balls.append([e.x+12, e.y+12, nx_p*2, ny_p*2])
                    
                    e.summon_cd -= 1
                    if e.summon_cd <= 0:
                        e.summon_cd = 300
                        summon_type = 'spider' if e.phase == 1 else 'ghost'
                        enemies.append(Entity(e.x + random.randint(-20,20), e.y + random.randint(-20,20), summon_type))

                er = e.get_rect()
                for b in bullets[:]:
                    if er.collidepoint(b[0], b[1]):
                        e.hp -= p_dmg; e.flash = 5; b[4] = 0
                        play_sound(SND_HIT)
                        if e.hp <= 0:
                            play_sound(SND_EXPLODE)
                            add_particles(e.x+e.w//2, e.y+e.h//2, (200,50,50))
                            enemies.remove(e); wave_kills += 1
                            if e.type in ['archer', 'golem', 'lich']: hazards.clear()
                        break
                
                if dist_core < 12:
                    core_hp -= 1
                    if e in enemies: enemies.remove(e); wave_kills+=1
                    if core_hp <= 0: state = "GAMEOVER"

            pr = pygame.Rect(px, py, 16, 16)
            for b in balls[:]:
                b[0] += b[2]; b[1] += b[3]
                size = 6 if len(b) > 4 else 4
                br = pygame.Rect(b[0]-size//2, b[1]-size//2, size, size)
                if pr.colliderect(br): balls.remove(b)
                elif math.hypot(b[0]-cx, b[1]-cy) < 10:
                    core_hp -= 1; balls.remove(b)
                    if core_hp <= 0: state = "GAMEOVER"

        # --- DRAW ---
        DISPLAY.fill(C_BG)
        for i in range(0, GAME_W, 20): pygame.draw.line(DISPLAY, C_GRID, (i,0), (i,GAME_H))
        for i in range(0, GAME_H, 20): pygame.draw.line(DISPLAY, C_GRID, (0,i), (GAME_W,i))
        cx, cy = GAME_W//2, GAME_H//2
        if state == "GAME":
            for h in hazards: h.draw(DISPLAY)
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 50
            col_in = (100, 200 - pulse, 255)
            pygame.draw.rect(DISPLAY, C_CORE_OUTER, (cx-8, cy-8, 16, 16))
            pygame.draw.rect(DISPLAY, col_in, (cx-4, cy-4, 8, 8))
            pygame.draw.rect(DISPLAY, C_WHITE, (cx-8, cy-8, 16, 16), 1)
            for b in balls: 
                col = (150, 150, 150) if len(b) > 4 else C_FIRE
                sz = 4 if len(b) > 4 else 2
                pygame.draw.circle(DISPLAY, col, (int(b[0]), int(b[1])), sz)
            for a in arrows: pygame.draw.line(DISPLAY, (200, 200, 200), (a[0], a[1]), (a[0]-a[2]*2, a[1]-a[3]*2), 1)
            update_draw_particles(DISPLAY)
            for e in enemies: e.draw(DISPLAY, px, py)
            draw_tank(DISPLAY, px, py, p_aim, p_recoil, False)
            for b in bullets: pygame.draw.rect(DISPLAY, (255,255,100), (b[0], b[1], 2, 2))
            
            bw = 150; bh = 6; bx = (GAME_W - bw) // 2; by = 5
            pygame.draw.rect(DISPLAY, (30,30,30), (bx, by, bw, bh))
            max_k = 1 if wave % 5 == 0 else (6 + wave)
            if wave_kills > 0:
                fill = min(1.0, wave_kills / max_k)
                pygame.draw.rect(DISPLAY, (255, 200, 0), (bx, by, int(bw*fill), bh))
            pygame.draw.rect(DISPLAY, C_WHITE, (bx, by, bw, bh), 1)
            t = FONT.render(f"HP:{core_hp} WV:{wave}", False, C_WHITE)
            DISPLAY.blit(t, (5, 5))

            if boss_exists:
                bbar_w = 200; bbar_h = 8; bbar_x = (GAME_W - bbar_w)//2; bbar_y = GAME_H - 15
                pygame.draw.rect(DISPLAY, (50,0,0), (bbar_x, bbar_y, bbar_w, bbar_h))
                pygame.draw.rect(DISPLAY, (200,0,0), (bbar_x, bbar_y, int(bbar_w * boss_hp_percent), bbar_h))
                pygame.draw.rect(DISPLAY, C_WHITE, (bbar_x, bbar_y, bbar_w, bbar_h), 1)
                bt = FONT.render("BOSS", False, C_WHITE)
                DISPLAY.blit(bt, (bbar_x + bbar_w//2 - bt.get_width()//2, bbar_y - 8))

        elif state == "MENU":
            t = FONT_BIG.render("PIXEL TANK DEFENSE", False, C_PLAYER_TURRET)
            DISPLAY.blit(t, (cx-t.get_width()//2, cy-30))
            draw_btn(DISPLAY, btn_start, "START GAME")
            draw_btn(DISPLAY, btn_settings, "SETTINGS")

        elif state == "SETTINGS":
            t = FONT_BIG.render("SETTINGS", False, C_WHITE)
            DISPLAY.blit(t, (cx-t.get_width()//2, 20))
            draw_btn(DISPLAY, btn_snd, f"SOUND: {'ON' if SETTINGS['SOUND'] else 'OFF'}")
            draw_btn(DISPLAY, btn_vib, f"VIBRA: {'ON' if SETTINGS['VIBRATION'] else 'OFF'}")
            draw_btn(DISPLAY, btn_back, "BACK")

        elif state == "UPGRADE":
            t = FONT_BIG.render("WAVE CLEARED", False, C_WHITE)
            DISPLAY.blit(t, (cx-t.get_width()//2, 20))
            pygame.draw.rect(DISPLAY, C_UI_BG, c1_rect); pygame.draw.rect(DISPLAY, C_RED, c1_rect, 2)
            t_dmg = FONT.render("DAMAGE +", False, C_RED)
            DISPLAY.blit(t_dmg, (c1_rect.centerx-t_dmg.get_width()//2, c1_rect.centery))
            pygame.draw.rect(DISPLAY, C_UI_BG, c2_rect); pygame.draw.rect(DISPLAY, C_GREEN, c2_rect, 2)
            t_spd = FONT.render("FIRE RATE +", False, C_GREEN)
            DISPLAY.blit(t_spd, (c2_rect.centerx-t_spd.get_width()//2, c2_rect.centery))

        elif state == "GAMEOVER":
            t = FONT_BIG.render("GAME OVER", False, C_RED)
            DISPLAY.blit(t, (cx-t.get_width()//2, cy))

        sc = pygame.transform.scale(DISPLAY, (int(GAME_W*SCALE), int(GAME_H*SCALE)))
        SCREEN.fill((0,0,0))
        SCREEN.blit(sc, (OFFSET_X, OFFSET_Y))
        if state == "GAME":
            for t in touches.values():
                sx, sy = t['start']; c = t['cur']
                pygame.draw.circle(SCREEN, (255,255,255), (int(sx), int(sy)), 60, 1)
                pygame.draw.circle(SCREEN, (255,255,255), (int(c[0]), int(c[1])), 30, 1)

        pygame.display.flip()
        CLOCK.tick(60)

if __name__ == "__main__":
    main()