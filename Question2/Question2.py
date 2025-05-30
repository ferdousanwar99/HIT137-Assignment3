import pygame
import random
import os

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60
PLAYER_SPEED = 5
JUMP_STRENGTH = 20
GRAVITY = 1
PROJECTILE_SPEED = 10
ENEMY_SPEED = 2
ENEMY2_SPEED = 3
ENEMY3_SPEED = 4
BOSS_BULLET_SPEED = 7
COLLECTIBLE_SIZE = 30  # Slightly bigger for mushroom image
DAMAGE = 5  # damage to player per enemy collision
DOUBLE_JUMP_MULTIPLIER = 2
DOUBLE_TAP_TIME = 300  # milliseconds allowed between taps

GROUND_HEIGHT = 70  # height of the ground image in pixels

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Set display mode before loading images requiring convert/convert_alpha
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Side-Scrolling Game")

# Load menu background image with error handling and alpha support
try:
    menu_background = pygame.image.load("load.png").convert_alpha()
    menu_background = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    print("Menu background loaded successfully.")
except pygame.error as e:
    print(f"Failed to load menu background: {e}")
    menu_background = None

# Load end screen background image with error handling and alpha support
try:
    end_background = pygame.image.load("background.png").convert_alpha()
    end_background = pygame.transform.scale(end_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    print("End screen background loaded successfully.")
except pygame.error as e:
    print(f"Failed to load end screen background: {e}")
    end_background = None

# Load sound effects with error handling
try:
    jump_sound = pygame.mixer.Sound("jump.wav")
except pygame.error:
    jump_sound = None
try:
    hit_sound = pygame.mixer.Sound("hit.wav")
except pygame.error:
    hit_sound = None

try:
    pygame.mixer.music.load("mario.wav")
except pygame.error:
    pass

# Load cloud image
try:
    cloud_image = pygame.image.load("cloud.png").convert_alpha()
    cloud_image = pygame.transform.scale(cloud_image, (150, 100))  # Resize as needed
except pygame.error:
    cloud_image = pygame.Surface((150, 100))
    cloud_image.fill((200, 200, 255))  # Light blue placeholder

# Load ground image with error handling
try:
    ground_image = pygame.image.load("ground.png").convert_alpha()
    # Scale ground image width to screen width, height to GROUND_HEIGHT
    ground_image = pygame.transform.scale(ground_image, (SCREEN_WIDTH, GROUND_HEIGHT))
except pygame.error:
    ground_image = pygame.Surface((SCREEN_WIDTH, GROUND_HEIGHT))
    ground_image.fill((139, 69, 19))  # Brown color placeholder

# Cloud Class for moving clouds
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = cloud_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 500)
        self.rect.y = random.randint(20, 150)
        self.speed = random.uniform(0.5, 1.5)  # Slow cloud speeds for natural effect

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            # Respawn on right with random height and random speed again for variety
            self.rect.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 500)
            self.rect.y = random.randint(20, 150)
            self.speed = random.uniform(0.5, 1.5)


# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(os.path.join("player.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
        except pygame.error:
            self.image = pygame.Surface((50, 50))
            self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.rect.height  # Start on top of ground
        self.speed = PLAYER_SPEED
        self.jump_strength = JUMP_STRENGTH
        self.health = 100
        self.max_health = 100
        self.lives = 50
        self.is_jumping = False
        self.velocity_y = 0
        self.last_space_press_time = 0  # track timing of spacebar presses

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.is_jumping:
            self.velocity_y += GRAVITY
            self.rect.y += self.velocity_y
            ground_y = SCREEN_HEIGHT - GROUND_HEIGHT - self.rect.height
            if self.rect.y >= ground_y:
                self.rect.y = ground_y
                self.is_jumping = False

    def jump(self, double_height=False):
        if not self.is_jumping:
            multiplier = DOUBLE_JUMP_MULTIPLIER if double_height else 1
            self.is_jumping = True
            self.velocity_y = -self.jump_strength * multiplier
            if jump_sound:
                jump_sound.play()  # Play jump sound

    def take_damage(self, damage):
        self.health -= damage
        if hit_sound:
            hit_sound.play()  # Play hit sound on damage
        if self.health <= 0:
            self.lives -= 1
            self.health = self.max_health
            self.rect.x = 50
            self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.rect.height

# Projectile Class with Fireball Image
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, super_fire=False):
        super().__init__()
        self.super_fire = super_fire
        try:
            if super_fire:
                self.image = pygame.image.load(os.path.join("superfireball.png")).convert_alpha()
            else:
                self.image = pygame.image.load(os.path.join("fireball.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (20, 20))
        except pygame.error:
            self.image = pygame.Surface((10, 5))
            self.image.fill((255, 69, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = PROJECTILE_SPEED 

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > SCREEN_WIDTH:
            self.kill()

# Enemy Classes
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(os.path.join("enemy.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
        except pygame.error:
            self.image = pygame.Surface((50, 50))
            self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.rect.height
        self.speed = ENEMY_SPEED
        self.health = 50

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < 0:
            self.kill()

class Enemy2(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(os.path.join("enemy2.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
        except pygame.error:
            self.image = pygame.Surface((60, 60))
            self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.rect.height + 10
        self.speed = ENEMY2_SPEED
        self.health = 70  # Stronger than regular enemy

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < 0:
            self.kill()

class Enemy3(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(os.path.join("enemy3.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (70, 70))
        except pygame.error:
            self.image = pygame.Surface((70, 70))
            self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.rect.height + 5
        self.speed = ENEMY3_SPEED
        self.health = 90  # Stronger enemy 3

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < 0:
            self.kill()

# Boss Enemy Class with Bullet Shooting & Up-Down Movement
class BossEnemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(os.path.join("boss.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (120, 120))
        except pygame.error:
            self.image = pygame.Surface((120, 120))
            self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH - 130
        self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT - 250  # Start higher for vertical movement
        self.speed_y = 2  # Up/down speed
        self.health = 15  # Takes 15 hits to die
        self.max_health = 15  # For health bar

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top <= 100 or self.rect.bottom >= SCREEN_HEIGHT - 150:
            self.speed_y = -self.speed_y

# Boss Bullet Class
class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("bullet.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 20))
        except pygame.error:
            self.image = pygame.Surface((40, 20))
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = BOSS_BULLET_SPEED

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Collectible class with Mushroom Image
class Collectible(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(os.path.join("mushroom.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (COLLECTIBLE_SIZE, COLLECTIBLE_SIZE))
        except pygame.error:
            self.image = pygame.Surface((COLLECTIBLE_SIZE, COLLECTIBLE_SIZE))
            self.image.fill((0, 0, 255))  # fallback blue box
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(100, SCREEN_WIDTH - 100)
        self.rect.y = random.randint(50, SCREEN_HEIGHT - GROUND_HEIGHT - 50)

font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)

def draw_text_center(surface, text, font, color, y_offset=0):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    surface.blit(render, rect)

def main():
    clock = pygame.time.Clock()

    # Game states
    STATE_START = 0
    STATE_PLAYING = 1
    STATE_GAMEOVER = 2
    STATE_WIN = 3

    state = STATE_START

    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    projectiles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    enemies2 = pygame.sprite.Group()
    enemies3 = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()
    all_clouds = pygame.sprite.Group()
    for _ in range(5):
        cloud = Cloud()
        all_clouds.add(cloud)

    score = 0
    boss_spawned = False
    super_fireball_unlocked = False
    boss_shoot_cooldown = 1500
    last_boss_shot_time = 0
    level_text = None
    level_text_start_time = 0
    level_text_duration = 0
    level_2_shown = False
    level_3_shown = False

    running = True
    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == STATE_START:
                if event.type == pygame.KEYDOWN:
                    try:
                        pygame.mixer.music.play(-1)
                    except:
                        pass

                    player = Player()
                    all_sprites = pygame.sprite.Group()
                    all_sprites.add(player)
                    projectiles = pygame.sprite.Group()
                    enemies = pygame.sprite.Group()
                    enemies2 = pygame.sprite.Group()
                    enemies3 = pygame.sprite.Group()
                    collectibles = pygame.sprite.Group()
                    boss_group = pygame.sprite.Group()
                    boss_bullets = pygame.sprite.Group()

                    all_clouds = pygame.sprite.Group()
                    for _ in range(5):
                        cloud = Cloud()
                        all_clouds.add(cloud)

                    score = 0
                    boss_spawned = False
                    super_fireball_unlocked = False

                    state = STATE_PLAYING
                    level_text = "Level 1"
                    level_text_start_time = current_time
                    level_text_duration = 5000
                    level_2_shown = False
                    level_3_shown = False

            elif state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        mods = pygame.key.get_mods()
                        if mods & pygame.KMOD_CTRL:
                            player.jump(double_height=True)
                        else:
                            if (current_time - player.last_space_press_time) <= DOUBLE_TAP_TIME:
                                player.jump(double_height=True)
                            else:
                                player.jump(double_height=False)
                            player.last_space_press_time = current_time

                    if event.key == pygame.K_f:
                        if boss_spawned:
                            y_offset = 10
                            fireball = Projectile(player.rect.right, player.rect.centery - y_offset, super_fire=False)
                            superfireball = Projectile(player.rect.right, player.rect.centery + y_offset, super_fire=True)
                            all_sprites.add(fireball, superfireball)
                            projectiles.add(fireball, superfireball)
                        else:
                            projectile = Projectile(player.rect.right, player.rect.centery - 10, super_fire=super_fireball_unlocked)
                            all_sprites.add(projectile)
                            projectiles.add(projectile)

            elif state == STATE_GAMEOVER or state == STATE_WIN:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        player = Player()
                        all_sprites = pygame.sprite.Group()
                        all_sprites.add(player)
                        projectiles = pygame.sprite.Group()
                        enemies = pygame.sprite.Group()
                        enemies2 = pygame.sprite.Group()
                        enemies3 = pygame.sprite.Group()
                        collectibles = pygame.sprite.Group()
                        boss_group = pygame.sprite.Group()
                        boss_bullets = pygame.sprite.Group()

                        all_clouds = pygame.sprite.Group()
                        for _ in range(5):
                            cloud = Cloud()
                            all_clouds.add(cloud)

                        score = 0
                        boss_spawned = False
                        super_fireball_unlocked = False

                        try:
                            pygame.mixer.music.play(-1)
                        except:
                            pass

                        state = STATE_PLAYING
                        level_text = "Level 1"
                        level_text_start_time = current_time
                        level_text_duration = 5000
                        level_2_shown = False
                        level_3_shown = False
                    elif event.key == pygame.K_q:
                        running = False

        if state == STATE_GAMEOVER or state == STATE_WIN:
            pygame.mixer.music.stop()

        if state == STATE_START:
            if menu_background:
                screen.blit(menu_background, (0, 0))
            else:
                screen.fill(WHITE)
            draw_text_center(screen, "Side-Scrolling Game", font, BLACK, y_offset=-50)
            draw_text_center(screen, "Press any key to start", small_font, BLACK, y_offset=20)
            draw_text_center(screen, "Jump: Space (Double tap or Ctrl for double jump)", small_font, BLACK, y_offset=60)
            draw_text_center(screen, "Shoot: F", small_font, BLACK, y_offset=90)
            pygame.display.flip()

        elif state == STATE_PLAYING:
            all_sprites.update()
            boss_group.update()
            boss_bullets.update()
            all_clouds.update()

            if score >= 500 and not boss_spawned:
                if not super_fireball_unlocked:
                    super_fireball_unlocked = True
                if len(enemies2) < 3 and random.randint(1, 100) < 10:
                    enemy2 = Enemy2()
                    all_sprites.add(enemy2)
                    enemies2.add(enemy2)
                    if not level_2_shown:
                        level_text = "Level 2"
                        level_text_start_time = current_time
                        level_text_duration = 4000
                        level_2_shown = True

            if score >= 1200 and not boss_spawned:
                if len(enemies3) < 3 and random.randint(1, 100) < 8:
                    enemy3 = Enemy3()
                    all_sprites.add(enemy3)
                    enemies3.add(enemy3)
                    if not level_3_shown:
                        level_text = "Level 3"
                        level_text_start_time = current_time
                        level_text_duration = 4000
                        level_3_shown = True

            if score >= 1500 and not boss_spawned:
                boss = BossEnemy()
                all_sprites.add(boss)
                boss_group.add(boss)
                boss_spawned = True
                for enemy in enemies:
                    enemy.kill()
                for enemy2 in enemies2:
                    enemy2.kill()
                for enemy3 in enemies3:
                    enemy3.kill()

            if boss_spawned and (current_time - last_boss_shot_time) > boss_shoot_cooldown:
                for b in boss_group:
                    bullet = BossBullet(b.rect.left, b.rect.centery)
                    all_sprites.add(bullet)
                    boss_bullets.add(bullet)
                last_boss_shot_time = current_time

            if not boss_spawned and score < 500:
                spawn_chance = min(2 + score // 100, 5)
                if random.randint(1, 100) < spawn_chance:
                    enemy = Enemy()
                    all_sprites.add(enemy)
                    enemies.add(enemy)

            enemies.update()
            enemies2.update()
            enemies3.update()

            for projectile in projectiles:
                enemy_hits = pygame.sprite.spritecollide(projectile, enemies, False)
                for enemy in enemy_hits:
                    enemy.health -= 20
                    projectile.kill()
                    if enemy.health <= 0:
                        enemy.kill()
                        score += 10

                enemy2_hits = pygame.sprite.spritecollide(projectile, enemies2, False)
                for enemy2 in enemy2_hits:
                    if projectile.super_fire:
                        enemy2.health -= 20
                        projectile.kill()
                        if enemy2.health <= 0:
                            enemy2.kill()
                            score += 20

                enemy3_hits = pygame.sprite.spritecollide(projectile, enemies3, False)
                for enemy3 in enemy3_hits:
                    enemy3.health -= 25
                    projectile.kill()
                    if enemy3.health <= 0:
                        enemy3.kill()
                        score += 30

                boss_hits = pygame.sprite.spritecollide(projectile, boss_group, False)
                for boss in boss_hits:
                    boss.health -= 1
                    projectile.kill()
                    if boss.health <= 0:
                        boss.kill()
                        score += 500
                        boss_spawned = False
                        state = STATE_WIN

            if pygame.sprite.spritecollide(player, enemies, False):
                player.take_damage(DAMAGE)
            if pygame.sprite.spritecollide(player, enemies2, False):
                player.take_damage(DAMAGE + 5)
            if pygame.sprite.spritecollide(player, enemies3, False):
                player.take_damage(DAMAGE + 10)
            if pygame.sprite.spritecollide(player, boss_group, False):
                player.take_damage(DAMAGE + 10)

            if pygame.sprite.spritecollide(player, boss_bullets, True):
                player.take_damage(DAMAGE + 8)

            if len(collectibles) < 3:
                if random.randint(1, 100) < 5:
                    collectible = Collectible()
                    all_sprites.add(collectible)
                    collectibles.add(collectible)

            collected = pygame.sprite.spritecollide(player, collectibles, True)
            for item in collected:
                score += 50

            screen.fill(WHITE)
            all_clouds.draw(screen)
            screen.blit(ground_image, (0, SCREEN_HEIGHT - GROUND_HEIGHT))
            all_sprites.draw(screen)

            health_bar_back = pygame.Rect(10, 10, 200, 25)
            health_bar_front = pygame.Rect(10, 10, 200 * (player.health / player.max_health), 25)
            pygame.draw.rect(screen, RED, health_bar_back)
            pygame.draw.rect(screen, GREEN, health_bar_front)

            lives_text = small_font.render(f"Lives: {player.lives}", True, RED)
            score_text = small_font.render(f"Score: {score}", True, BLACK)
            screen.blit(lives_text, (10, 45))
            screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

            if boss_spawned and len(boss_group) > 0:
                boss = next(iter(boss_group))
                boss_bar_back = pygame.Rect(SCREEN_WIDTH//2 - 100, 50, 200, 20)
                boss_bar_front = pygame.Rect(SCREEN_WIDTH//2 - 100, 50, 200 * (boss.health / boss.max_health), 20)
                pygame.draw.rect(screen, RED, boss_bar_back)
                pygame.draw.rect(screen, GREEN, boss_bar_front)
                boss_text = small_font.render("Boss Health", True, BLACK)
                screen.blit(boss_text, (SCREEN_WIDTH//2 - boss_text.get_width()//2, 20))

            if level_text is not None:
                elapsed = current_time - level_text_start_time
                if elapsed < level_text_duration:
                    large_font = pygame.font.SysFont("Arial", 72)
                    text_render = large_font.render(level_text, True, ORANGE)
                    text_rect = text_render.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 200))
                    shadow_render = large_font.render(level_text, True, BLACK)
                    shadow_rect = shadow_render.get_rect(center=(SCREEN_WIDTH//2 + 3, SCREEN_HEIGHT//2 - 197))
                    screen.blit(shadow_render, shadow_rect)
                    screen.blit(text_render, text_rect)
                else:
                    level_text = None

            pygame.display.flip()

            if player.lives <= 0:
                state = STATE_GAMEOVER

        elif state == STATE_GAMEOVER:
            if end_background:
                screen.blit(end_background, (0, 0))
            else:
                screen.fill(WHITE)
            draw_text_center(screen, "Game Over", font, RED, y_offset=-100)
            draw_text_center(screen, f"Final Score: {score}", small_font, BLACK, y_offset=0)
            draw_text_center(screen, "Press R to Restart or Q to Quit", small_font, BLACK, y_offset=50)
            pygame.display.flip()

        elif state == STATE_WIN:
            if end_background:
                screen.blit(end_background, (0, 0))
            else:
                screen.fill(WHITE)
            draw_text_center(screen, "YOU WON!", font, GREEN, y_offset=-100)
            draw_text_center(screen, f"Final Score: {score}", small_font, BLACK, y_offset=0)
            draw_text_center(screen, "Press R to Restart or Q to Quit", small_font, BLACK, y_offset=50)
            pygame.display.flip()



    pygame.quit()

if __name__ == "__main__":
    main()

