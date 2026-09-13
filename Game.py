import pygame
import random
import math
import sys
import io
import wave
import struct


# =========================================================
# 1. PYGAME INITIALIZATION
# =========================================================

pygame.mixer.pre_init(
    44100,
    -16,
    1,
    512
)

pygame.init()


# =========================================================
# 2. FULLSCREEN
# =========================================================

fullscreen = True

screen = pygame.display.set_mode(
    (0, 0),
    pygame.FULLSCREEN
)

pygame.display.set_caption("SPACE DEFENDER")

clock = pygame.time.Clock()

FPS = 60

WIDTH, HEIGHT = screen.get_size()


# =========================================================
# 3. COLORS
# =========================================================

BLACK = (3, 5, 18)
WHITE = (255, 255, 255)

BLUE = (40, 120, 255)
LIGHT_BLUE = (100, 220, 255)

CYAN = (0, 230, 255)

RED = (255, 50, 70)
DARK_RED = (120, 10, 30)

PURPLE = (150, 60, 255)
PINK = (255, 50, 190)

YELLOW = (255, 230, 70)
ORANGE = (255, 130, 30)

GREEN = (50, 255, 150)


# =========================================================
# 4. FONTS
# =========================================================

font_small = pygame.font.Font(None, 30)
font_medium = pygame.font.Font(None, 45)
font_large = pygame.font.Font(None, 70)
font_title = pygame.font.Font(None, 95)


# =========================================================
# 5. SOUND SYSTEM
# =========================================================

# This creates sounds automatically.
# No external sound files are required.


def create_sound(frequency, duration, volume=0.5):

    sample_rate = 44100

    total_samples = int(
        sample_rate * duration
    )

    data = bytearray()

    for i in range(total_samples):

        time = i / sample_rate

        # Smooth fade
        fade_in = min(
            1,
            time / 0.02
        )

        fade_out = min(
            1,
            (duration - time) / 0.05
        )

        envelope = min(
            fade_in,
            fade_out
        )

        value = int(
            32767
            * volume
            * envelope
            * math.sin(
                2 * math.pi * frequency * time
            )
        )

        data.extend(
            struct.pack(
                "<h",
                value
            )
        )

    return pygame.mixer.Sound(
        buffer=bytes(data)
    )


# =========================================================
# 6. CREATE SPECIAL SFX
# =========================================================

laser_sound = create_sound(
    900,
    0.08,
    0.30
)

enemy_sound = create_sound(
    180,
    0.15,
    0.50
)

death_sound = create_sound(
    90,
    0.8,
    0.70
)

buff_sound = create_sound(
    700,
    0.25,
    0.50
)

gameover_sound = create_sound(
    60,
    1.0,
    0.60
)


# =========================================================
# 7. BACKGROUND MUSIC
# =========================================================

def create_background_music():

    sample_rate = 44100

    # Space-style melody
    notes = [
        220,
        261,
        330,
        392,
        330,
        261,
        220,
        196,

        220,
        293,
        349,
        440,
        349,
        293,
        220,
        196
    ]

    note_duration = 0.35

    data = bytearray()

    for frequency in notes:

        samples = int(
            sample_rate * note_duration
        )

        for i in range(samples):

            t = i / sample_rate

            fade = min(
                1,
                (note_duration - t) / 0.08
            )

            # Two harmonic waves
            value = (
                math.sin(
                    2 * math.pi * frequency * t
                )
                * 0.35
            )

            value += (
                math.sin(
                    2 * math.pi * frequency * 2 * t
                )
                * 0.10
            )

            sample = int(
                32767
                * value
                * fade
                * 0.22
            )

            data.extend(
                struct.pack(
                    "<h",
                    sample
                )
            )

    return pygame.mixer.Sound(
        buffer=bytes(data)
    )


background_music = create_background_music()

background_music.set_volume(0.25)

music_channel = background_music.play(
    loops=-1
)


# =========================================================
# 8. PLAYER
# =========================================================

PLAYER_WIDTH = 75
PLAYER_HEIGHT = 80

player_x = WIDTH // 2 - PLAYER_WIDTH // 2

player_y = HEIGHT - 150

player_speed = 8

player_lives = 3


# =========================================================
# 9. SCORE
# =========================================================

score = 0

NORMAL_SCORE = 2

BUFF_SCORE = 10


# =========================================================
# 10. GAME STATE
# =========================================================

game_state = "menu"


# =========================================================
# 11. LASER
# =========================================================

lasers = []

laser_speed = 18

normal_shoot_delay = 180

buff_shoot_delay = 45

laser_cooldown = 0


# =========================================================
# 12. ENEMY
# =========================================================

enemies = []

enemy_spawn_timer = 0

enemy_spawn_delay = 850


# =========================================================
# 13. BUFF
# =========================================================

buff_active = False

buff_timer = 0

buff_duration = 5000

buff_x = 0

buff_y = 0

buff_vx = 0

buff_vy = 0

buff_speed = 1.5

buff_spawn_timer = 5000


# =========================================================
# 14. STARS
# =========================================================

stars = []

for i in range(200):

    stars.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "speed": random.uniform(0.5, 3),
        "size": random.randint(1, 3)
    })


# =========================================================
# 15. NEBULA
# =========================================================

nebula = []

for i in range(50):

    nebula.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "radius": random.randint(20, 80)
    })


# =========================================================
# 16. CENTER TEXT
# =========================================================

def center_text(
    text,
    font,
    color,
    y
):

    image = font.render(
        text,
        True,
        color
    )

    x = (
        WIDTH // 2
        - image.get_width() // 2
    )

    screen.blit(
        image,
        (x, int(y))
    )


# =========================================================
# 17. BACKGROUND
# =========================================================

def draw_background():

    screen.fill(BLACK)

    nebula_surface = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    for cloud in nebula:

        pygame.draw.circle(
            nebula_surface,
            (70, 30, 150, 25),
            (
                cloud["x"],
                cloud["y"]
            ),
            cloud["radius"]
        )

    screen.blit(
        nebula_surface,
        (0, 0)
    )

    for star in stars:

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(star["x"]),
                int(star["y"])
            ),
            star["size"]
        )


# =========================================================
# 18. MOVE STARS
# =========================================================

def move_background():

    for star in stars:

        star["y"] += star["speed"]

        if star["y"] > HEIGHT:

            star["y"] = 0

            star["x"] = random.randint(
                0,
                WIDTH
            )


# =========================================================
# 19. PLAYER SPACECRAFT
# =========================================================

def draw_player():

    x = player_x
    y = player_y

    # -----------------------------------------------------
    # POWER-UP GLOW
    # -----------------------------------------------------

    if buff_active:

        glow = pygame.Surface(
            (180, 180),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow,
            (0, 255, 255, 45),
            (90, 90),
            70
        )

        pygame.draw.circle(
            glow,
            (255, 0, 255, 35),
            (90, 90),
            50
        )

        screen.blit(
            glow,
            (
                x - 52,
                y - 50
            )
        )

    # -----------------------------------------------------
    # ENGINE
    # -----------------------------------------------------

    flame_length = random.randint(
        20,
        35
    )

    flame_color = (
        PINK
        if buff_active
        else ORANGE
    )

    pygame.draw.polygon(
        screen,
        flame_color,
        [
            (x + 20, y + 58),
            (
                x + 37,
                y + 58 + flame_length
            ),
            (x + 54, y + 58)
        ]
    )

    pygame.draw.polygon(
        screen,
        YELLOW,
        [
            (x + 28, y + 58),
            (
                x + 37,
                y + 50 + flame_length
            ),
            (x + 46, y + 58)
        ]
    )

    # -----------------------------------------------------
    # BODY
    # -----------------------------------------------------

    body_color = (
        PURPLE
        if buff_active
        else BLUE
    )

    pygame.draw.polygon(
        screen,
        body_color,
        [
            (x + 37, y),
            (x + 5, y + 62),
            (x + 20, y + 75),
            (x + 37, y + 55),
            (x + 54, y + 75),
            (x + 69, y + 62)
        ]
    )

    # -----------------------------------------------------
    # CENTER
    # -----------------------------------------------------

    center_color = (
        PINK
        if buff_active
        else LIGHT_BLUE
    )

    pygame.draw.polygon(
        screen,
        center_color,
        [
            (x + 37, y + 10),
            (x + 23, y + 50),
            (x + 37, y + 43),
            (x + 51, y + 50)
        ]
    )

    # -----------------------------------------------------
    # COCKPIT
    # -----------------------------------------------------

    pygame.draw.ellipse(
        screen,
        (10, 25, 70),
        (
            x + 26,
            y + 18,
            22,
            27
        )
    )

    pygame.draw.ellipse(
        screen,
        (
            YELLOW
            if buff_active
            else CYAN
        ),
        (
            x + 30,
            y + 21,
            14,
            19
        )
    )

    # -----------------------------------------------------
    # WINGS
    # -----------------------------------------------------

    wing_color = (
        PINK
        if buff_active
        else PURPLE
    )

    pygame.draw.polygon(
        screen,
        wing_color,
        [
            (x + 20, y + 45),
            (x - 8, y + 68),
            (x + 17, y + 65)
        ]
    )

    pygame.draw.polygon(
        screen,
        wing_color,
        [
            (x + 54, y + 45),
            (x + 82, y + 68),
            (x + 57, y + 65)
        ]
    )


# =========================================================
# 20. FIRE LASER
# =========================================================

def fire_laser():

    laser_x = (
        player_x
        + PLAYER_WIDTH // 2
    )

    laser_y = player_y - 10

    lasers.append({
        "x": laser_x,
        "y": laser_y
    })

    # Laser sound
    laser_sound.play()


# =========================================================
# 21. DRAW LASER
# =========================================================

def draw_laser(laser):

    x = int(laser["x"])

    y = int(laser["y"])

    if buff_active:

        glow = pygame.Surface(
            (70, 80),
            pygame.SRCALPHA
        )

        pygame.draw.ellipse(
            glow,
            (255, 0, 255, 70),
            (5, 0, 60, 75)
        )

        screen.blit(
            glow,
            (
                x - 35,
                y - 10
            )
        )

        pygame.draw.rect(
            screen,
            PINK,
            (
                x - 7,
                y,
                14,
                45
            )
        )

        pygame.draw.rect(
            screen,
            WHITE,
            (
                x - 3,
                y,
                6,
                45
            )
        )

    else:

        glow = pygame.Surface(
            (50, 65),
            pygame.SRCALPHA
        )

        pygame.draw.ellipse(
            glow,
            (0, 220, 255, 60),
            (5, 0, 40, 60)
        )

        screen.blit(
            glow,
            (
                x - 25,
                y - 5
            )
        )

        pygame.draw.rect(
            screen,
            CYAN,
            (
                x - 5,
                y,
                10,
                38
            )
        )

        pygame.draw.rect(
            screen,
            WHITE,
            (
                x - 2,
                y,
                4,
                38
            )
        )


# =========================================================
# 22. CREATE ENEMY
# =========================================================

def create_enemy():

    size = random.randint(
        38,
        52
    )

    x = random.randint(
        20,
        WIDTH - size - 20
    )

    y = -size

    enemies.append({
        "x": x,
        "y": y,
        "size": size,
        "speed": random.uniform(
            2.0,
            3.2
        )
    })


# =========================================================
# 23. DRAW ENEMY
# =========================================================

def draw_enemy(enemy):

    x = enemy["x"]

    y = enemy["y"]

    size = enemy["size"]

    center_x = int(
        x + size / 2
    )

    center_y = int(
        y + size / 2
    )

    # Glow
    glow = pygame.Surface(
        (size * 2, size * 2),
        pygame.SRCALPHA
    )

    pygame.draw.circle(
        glow,
        (255, 0, 40, 40),
        (
            size,
            size
        ),
        size
    )

    screen.blit(
        glow,
        (
            x - size / 2,
            y - size / 2
        )
    )

    # Body
    pygame.draw.polygon(
        screen,
        RED,
        [
            (
                center_x,
                int(y)
            ),
            (
                int(x),
                int(y + size - 10)
            ),
            (
                center_x,
                int(y + size - 20)
            ),
            (
                int(x + size),
                int(y + size - 10)
            )
        ]
    )

    # Core
    pygame.draw.circle(
        screen,
        DARK_RED,
        (
            center_x,
            center_y
        ),
        size // 4
    )

    pygame.draw.circle(
        screen,
        ORANGE,
        (
            center_x,
            center_y
        ),
        size // 7
    )

    # Wings
    pygame.draw.polygon(
        screen,
        PURPLE,
        [
            (
                int(x + size * 0.3),
                center_y
            ),
            (
                int(x - 8),
                int(y + size - 5)
            ),
            (
                int(x + size * 0.4),
                int(y + size - 15)
            )
        ]
    )

    pygame.draw.polygon(
        screen,
        PURPLE,
        [
            (
                int(x + size * 0.7),
                center_y
            ),
            (
                int(x + size + 8),
                int(y + size - 5)
            ),
            (
                int(x + size * 0.6),
                int(y + size - 15)
            )
        ]
    )


# =========================================================
# 24. CREATE BUFF
# =========================================================

def create_buff():

    global buff_x
    global buff_y
    global buff_vx
    global buff_vy

    # Spawn from top
    buff_x = random.randint(
        80,
        WIDTH - 80
    )

    buff_y = -40

    # Player position
    target_x = (
        player_x
        + PLAYER_WIDTH // 2
    )

    target_y = (
        player_y
        + PLAYER_HEIGHT // 2
    )

    # Direction
    dx = target_x - buff_x

    dy = target_y - buff_y

    distance = math.sqrt(
        dx * dx + dy * dy
    )

    if distance == 0:

        distance = 1

    buff_vx = (
        dx / distance
    ) * buff_speed

    buff_vy = (
        dy / distance
    ) * buff_speed


# =========================================================
# 25. DRAW BUFF
# =========================================================

def draw_buff():

    x = int(buff_x)

    y = int(buff_y)

    pulse = int(
        5
        + 5
        * math.sin(
            pygame.time.get_ticks()
            * 0.01
        )
    )

    glow = pygame.Surface(
        (120, 120),
        pygame.SRCALPHA
    )

    pygame.draw.circle(
        glow,
        (0, 255, 255, 65),
        (60, 60),
        35 + pulse
    )

    pygame.draw.circle(
        glow,
        (255, 0, 255, 45),
        (60, 60),
        25 + pulse
    )

    screen.blit(
        glow,
        (
            x - 60,
            y - 60
        )
    )

    pygame.draw.circle(
        screen,
        CYAN,
        (x, y),
        25
    )

    pygame.draw.circle(
        screen,
        PURPLE,
        (x, y),
        20
    )

    # Lightning
    pygame.draw.polygon(
        screen,
        YELLOW,
        [
            (x + 5, y - 18),
            (x - 8, y + 2),
            (x, y + 2),
            (x - 5, y + 18),
            (x + 12, y - 5),
            (x + 3, y - 5)
        ]
    )


# =========================================================
# 26. RESET GAME
# =========================================================

def reset_game():

    global player_x
    global player_y
    global player_lives

    global score

    global lasers
    global enemies

    global laser_cooldown

    global buff_active
    global buff_timer

    global buff_x
    global buff_y

    global buff_vx
    global buff_vy

    global buff_spawn_timer

    player_x = (
        WIDTH // 2
        - PLAYER_WIDTH // 2
    )

    player_y = HEIGHT - 150

    player_lives = 3

    score = 0

    lasers = []

    enemies = []

    laser_cooldown = 0

    buff_active = False

    buff_timer = 0

    buff_x = 0
    buff_y = 0

    buff_vx = 0
    buff_vy = 0

    buff_spawn_timer = random.randint(
        5000,
        9000
    )


# =========================================================
# 27. MENU
# =========================================================

def draw_menu():

    draw_background()

    center_text(
        "SPACE DEFENDER",
        font_title,
        CYAN,
        HEIGHT * 0.20
    )

    center_text(
        "FUTURISTIC SPACE BATTLE",
        font_medium,
        WHITE,
        HEIGHT * 0.35
    )

    center_text(
        "PRESS ENTER TO START",
        font_medium,
        GREEN,
        HEIGHT * 0.48
    )

    center_text(
        "W A S D / ARROW KEYS = MOVE",
        font_small,
        WHITE,
        HEIGHT * 0.60
    )

    center_text(
        "SPACE = FIRE LASER",
        font_small,
        WHITE,
        HEIGHT * 0.65
    )

    center_text(
        "F11 = FULLSCREEN / WINDOW",
        font_small,
        WHITE,
        HEIGHT * 0.70
    )

    center_text(
        "ESC = EXIT",
        font_small,
        WHITE,
        HEIGHT * 0.75
    )


# =========================================================
# 28. GAME OVER
# =========================================================

def draw_game_over():

    draw_background()

    center_text(
        "MISSION FAILED",
        font_title,
        RED,
        HEIGHT * 0.25
    )

    center_text(
        f"SCORE: {score}",
        font_large,
        WHITE,
        HEIGHT * 0.43
    )

    center_text(
        "PRESS ENTER TO RESTART",
        font_medium,
        GREEN,
        HEIGHT * 0.58
    )

    center_text(
        "ESC = EXIT",
        font_small,
        WHITE,
        HEIGHT * 0.68
    )


# =========================================================
# 29. GAME SCREEN
# =========================================================

def draw_game():

    draw_background()

    # Player
    draw_player()

    # Buff
    if (
        not buff_active
        and buff_spawn_timer <= 0
        and buff_vx != 0
    ):

        draw_buff()

    # Lasers
    for laser in lasers:

        draw_laser(laser)

    # Enemies
    for enemy in enemies:

        draw_enemy(enemy)

    # Score
    score_image = font_medium.render(
        f"SCORE: {score}",
        True,
        WHITE
    )

    screen.blit(
        score_image,
        (25, 25)
    )

    # Lives
    lives_image = font_medium.render(
        f"LIVES: {player_lives}",
        True,
        GREEN
    )

    screen.blit(
        lives_image,
        (25, 70)
    )

    # Buff status
    if buff_active:

        seconds = math.ceil(
            buff_timer / 1000
        )

        power_image = font_medium.render(
            f"POWER-UP: {seconds}s",
            True,
            PINK
        )

        screen.blit(
            power_image,
            (
                WIDTH - 310,
                25
            )
        )

        points_image = font_small.render(
            "KILL = 10 POINTS",
            True,
            YELLOW
        )

        screen.blit(
            points_image,
            (
                WIDTH - 270,
                70
            )
        )


# =========================================================
# 30. FULLSCREEN TOGGLE
# =========================================================

def toggle_fullscreen():

    global fullscreen
    global screen
    global WIDTH
    global HEIGHT

    fullscreen = not fullscreen

    if fullscreen:

        screen = pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN
        )

    else:

        screen = pygame.display.set_mode(
            (1000, 700)
        )

    WIDTH, HEIGHT = screen.get_size()


# =========================================================
# 31. MAIN LOOP
# =========================================================

running = True


while running:

    dt = clock.tick(FPS)

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        # -------------------------------------------------
        # CLOSE WINDOW
        # -------------------------------------------------

        if event.type == pygame.QUIT:

            running = False

        # -------------------------------------------------
        # KEYBOARD
        # -------------------------------------------------

        if event.type == pygame.KEYDOWN:

            # F11
            if event.key == pygame.K_F11:

                toggle_fullscreen()

            # ESC
            if event.key == pygame.K_ESCAPE:

                running = False

            # -------------------------------------------------
            # MENU
            # -------------------------------------------------

            if game_state == "menu":

                if event.key == pygame.K_RETURN:

                    reset_game()

                    game_state = "playing"

            # -------------------------------------------------
            # GAME OVER
            # -------------------------------------------------

            elif game_state == "game_over":

                if event.key == pygame.K_RETURN:

                    reset_game()

                    game_state = "playing"


    # =====================================================
    # PLAYING
    # =====================================================

    if game_state == "playing":

        keys = pygame.key.get_pressed()

        # -------------------------------------------------
        # MOVEMENT
        # -------------------------------------------------

        if (
            keys[pygame.K_LEFT]
            or keys[pygame.K_a]
        ):

            player_x -= player_speed

        if (
            keys[pygame.K_RIGHT]
            or keys[pygame.K_d]
        ):

            player_x += player_speed

        if (
            keys[pygame.K_UP]
            or keys[pygame.K_w]
        ):

            player_y -= player_speed

        if (
            keys[pygame.K_DOWN]
            or keys[pygame.K_s]
        ):

            player_y += player_speed

        # Keep player inside screen

        player_x = max(
            0,
            min(
                WIDTH - PLAYER_WIDTH,
                player_x
            )
        )

        player_y = max(
            80,
            min(
                HEIGHT - PLAYER_HEIGHT - 20,
                player_y
            )
        )

        # -------------------------------------------------
        # LASER COOLDOWN
        # -------------------------------------------------

        if laser_cooldown > 0:

            laser_cooldown -= dt

        # -------------------------------------------------
        # HOLD SPACE TO SHOOT
        # -------------------------------------------------

        if keys[pygame.K_SPACE]:

            if laser_cooldown <= 0:

                fire_laser()

                if buff_active:

                    laser_cooldown = (
                        buff_shoot_delay
                    )

                else:

                    laser_cooldown = (
                        normal_shoot_delay
                    )

        # =================================================
        # MOVE LASERS
        # =================================================

        for laser in lasers[:]:

            laser["y"] -= laser_speed

            if laser["y"] < -60:

                lasers.remove(laser)

        # =================================================
        # ENEMY SPAWN
        # =================================================

        enemy_spawn_timer += dt

        if enemy_spawn_timer >= enemy_spawn_delay:

            create_enemy()

            enemy_spawn_timer = 0

        # =================================================
        # MOVE ENEMIES
        # =================================================

        for enemy in enemies[:]:

            enemy["y"] += enemy["speed"]

            # Missed enemy = NO DAMAGE

            if enemy["y"] > HEIGHT + 100:

                enemies.remove(enemy)

        # =================================================
        # BUFF TIMER
        # =================================================

        if not buff_active:

            if buff_spawn_timer > 0:

                buff_spawn_timer -= dt

        # =================================================
        # CREATE BUFF
        # =================================================

        if (
            not buff_active
            and buff_spawn_timer <= 0
            and buff_vx == 0
            and buff_vy == 0
        ):

            create_buff()

        # =================================================
        # MOVE BUFF
        # =================================================

        if (
            not buff_active
            and buff_spawn_timer <= 0
            and buff_vx != 0
        ):

            buff_x += buff_vx

            buff_y += buff_vy

        # =================================================
        # PLAYER RECT
        # =================================================

        player_rect = pygame.Rect(
            int(player_x + 10),
            int(player_y + 10),
            PLAYER_WIDTH - 20,
            PLAYER_HEIGHT - 15
        )

        # =================================================
        # BUFF COLLISION
        # =================================================

        if (
            not buff_active
            and buff_spawn_timer <= 0
            and buff_vx != 0
        ):

            buff_rect = pygame.Rect(
                int(buff_x - 25),
                int(buff_y - 25),
                50,
                50
            )

            if player_rect.colliderect(
                buff_rect
            ):

                # Activate buff
                buff_active = True

                # EXACTLY 5 SECONDS
                buff_timer = buff_duration

                # Stop movement
                buff_vx = 0
                buff_vy = 0

                # Buff sound
                buff_sound.play()

        # =================================================
        # BUFF ACTIVE TIMER
        # =================================================

        if buff_active:

            buff_timer -= dt

            if buff_timer <= 0:

                buff_active = False

                buff_timer = 0

                buff_x = 0
                buff_y = 0

                buff_vx = 0
                buff_vy = 0

                # Next buff
                buff_spawn_timer = random.randint(
                    6000,
                    12000
                )

        # =================================================
        # BUFF MISSED
        # =================================================

        if (
            not buff_active
            and buff_spawn_timer <= 0
            and buff_vx != 0
        ):

            if (
                buff_x < -100
                or buff_x > WIDTH + 100
                or buff_y > HEIGHT + 100
            ):

                buff_x = 0
                buff_y = 0

                buff_vx = 0
                buff_vy = 0

                buff_spawn_timer = random.randint(
                    5000,
                    9000
                )

        # =================================================
        # ENEMY HITS PLAYER
        # =================================================

        for enemy in enemies[:]:

            enemy_rect = pygame.Rect(
                int(enemy["x"]),
                int(enemy["y"]),
                enemy["size"],
                enemy["size"]
            )

            if player_rect.colliderect(
                enemy_rect
            ):

                enemies.remove(enemy)

                player_lives -= 1

                # If player dies
                if player_lives <= 0:

                    death_sound.play()

                    gameover_sound.play()

                    game_state = "game_over"

        # =================================================
        # LASER HITS ENEMY
        # =================================================

        for laser in lasers[:]:

            laser_rect = pygame.Rect(
                int(laser["x"] - 5),
                int(laser["y"]),
                10,
                40
            )

            for enemy in enemies[:]:

                enemy_rect = pygame.Rect(
                    int(enemy["x"]),
                    int(enemy["y"]),
                    enemy["size"],
                    enemy["size"]
                )

                if laser_rect.colliderect(
                    enemy_rect
                ):

                    # Remove laser
                    if laser in lasers:

                        lasers.remove(laser)

                    # Remove enemy
                    if enemy in enemies:

                        enemies.remove(enemy)

                    # Score
                    if buff_active:

                        score += BUFF_SCORE

                    else:

                        score += NORMAL_SCORE

                    # Enemy destroy sound
                    enemy_sound.play()

                    break

    # =====================================================
    # DRAW
    # =====================================================

    if game_state == "menu":

        draw_menu()

    elif game_state == "playing":

        draw_game()

    elif game_state == "game_over":

        draw_game_over()

    # =====================================================
    # MOVE BACKGROUND
    # =====================================================

    move_background()

    # =====================================================
    # UPDATE SCREEN
    # =====================================================

    pygame.display.flip()


# =========================================================
# EXIT
# =========================================================

pygame.quit()

sys.exit()