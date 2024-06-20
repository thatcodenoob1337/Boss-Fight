import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_HEIGHT = -18  # Increased jump height
ARROW_SPEED = 10
FIREBALL_SPEED = 7
BOSS_SPEED = 2  # Boss movement speed
LASER_COOLDOWN = 5000  # Increased cooldown between boss attacks
DUCK_HEIGHT = 25
BOSS_HEALTH = 500
PLAYER_HEALTH = 100
BOUNCE_VEL_Y = -20  # Velocity when bouncing on boss
VICTORY_TIME = 2000  # Time to display victory screen in milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Boss Fight Game")

# Font
font = pygame.font.Font(None, 36)

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 50
        self.height = 50
        self.color = BLUE
        self.rect = pygame.Rect(100, SCREEN_HEIGHT - self.height, self.width, self.height)
        self.health = PLAYER_HEALTH
        self.vel_y = 0
        self.on_ground = True
        self.last_shot = pygame.time.get_ticks()
        self.ducking = False
        self.original_height = self.height

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if not self.ducking and keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_HEIGHT
            self.on_ground = False
        if keys[pygame.K_f]:
            self.shoot()
        if keys[pygame.K_d]:
            self.ducking = True
            self.rect.height = DUCK_HEIGHT
        else:
            self.ducking = False
            self.rect.height = self.original_height

        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Check if on the ground
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True
            self.vel_y = 0

        # Health regeneration
        self.health = min(PLAYER_HEALTH, self.health + 0.01)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > 1000:
            self.last_shot = now
            arrow = Arrow(self.rect.right, self.rect.centery)
            all_sprites.add(arrow)
            arrows.add(arrow)

    def bounce(self):
        self.vel_y = BOUNCE_VEL_Y

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 20
        self.height = 5
        self.color = RED
        self.rect = pygame.Rect(x, y - self.height // 2, self.width, self.height)

    def update(self):
        self.rect.x += ARROW_SPEED
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.radius = 15
        self.color = RED
        self.rect = pygame.Rect(x - self.radius, y - self.radius + 50, self.radius * 2, self.radius * 2)  # Lower position

    def update(self):
        self.rect.x -= FIREBALL_SPEED
        if self.rect.right < 0:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 150
        self.height = 10
        self.color = RED
        self.rect = pygame.Rect(x, y - self.height // 2, self.width, self.height)

    def update(self):
        self.rect.x -= FIREBALL_SPEED
        if self.rect.right < 0:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 100
        self.height = 100
        self.color = GREEN
        self.rect = pygame.Rect(SCREEN_WIDTH - self.width - 100, SCREEN_HEIGHT - self.height, self.width, self.height)
        self.health = BOSS_HEALTH
        self.last_shot = pygame.time.get_ticks()
        self.last_laser = pygame.time.get_ticks()
        self.laser_active = False
        self.fireball_active = False
        self.vel_x = BOSS_SPEED

    def update(self):
        now = pygame.time.get_ticks()
        if not self.laser_active and not self.fireball_active:
            if now - self.last_shot > 3000:  # Increased cooldown between attacks
                self.last_shot = now
                if random.random() < 0.5:
                    self.fireball_active = True
                    fireball = Fireball(self.rect.left, self.rect.centery)
                    all_sprites.add(fireball)
                    fireballs.add(fireball)
                else:
                    self.laser_active = True
                    laser = Laser(self.rect.left, self.rect.centery)
                    all_sprites.add(laser)
                    lasers.add(laser)
        elif self.laser_active and now - self.last_laser > LASER_COOLDOWN:
            self.laser_active = False
            self.last_laser = now
        elif self.fireball_active:
            self.fireball_active = False

        # Boss movement
        self.rect.x += self.vel_x
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.vel_x = -self.vel_x

# Groups
all_sprites = pygame.sprite.Group()
arrows = pygame.sprite.Group()
fireballs = pygame.sprite.Group()
lasers = pygame.sprite.Group()

player = Player()
boss = Boss()

all_sprites.add(player)
all_sprites.add(boss)

# Countdown function
def draw_countdown(count):
    if count > 0:
        text = font.render(str(count), True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

# Victory screen function
def draw_victory():
    text = font.render("Victory!", True, GREEN)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(VICTORY_TIME)

# Main game loop
def main():
    clock = pygame.time.Clock()
    running = True
    game_started = False
    game_over = False
    victory = False
    countdown = 3
    countdown_timer = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game_started and event.type == pygame.KEYDOWN:
                game_started = True
                countdown_timer = pygame.time.get_ticks()
            if game_over and event.type == pygame.KEYDOWN:
                game_over = False
                game_started = True
                player.health = PLAYER_HEALTH
                boss.health = BOSS_HEALTH
                player.rect.topleft = (100, SCREEN_HEIGHT - player.height)
                boss.rect.topleft = (SCREEN_WIDTH - boss.width - 100, SCREEN_HEIGHT - boss.height)
                arrows.empty()
                fireballs.empty()
                lasers.empty()

        if game_started and not game_over:
            current_time = pygame.time.get_ticks()
            if current_time - countdown_timer > 1000:
                countdown -= 1
                countdown_timer = current_time

            all_sprites.update()

            # Collision detection
            if player.rect.colliderect(boss.rect):
                if player.vel_y > 0 and player.rect.bottom <= boss.rect.centery:
                    player.bounce()
                    boss.health -= 20  # Increased damage when bouncing
                else:
                    player.health -= 10
            for fireball in fireballs:
                if player.rect.colliderect(fireball.rect):
                    player.health -= 10
                    fireball.kill()
            for laser in lasers:
                if player.rect.colliderect(laser.rect):
                    player.health -= 20
                    laser.kill()
            for arrow in arrows:
                if boss.rect.colliderect(arrow.rect):
                    boss.health -= 10
                    arrow.kill()

            # Check game over
            if player.health <= 0:
                game_over = True
            if boss.health <= 0:
                victory = True
                game_over = True

        screen.fill(WHITE)
        if not game_started:
            draw_countdown(countdown)
            if countdown == 0:
                game_started = True
        elif victory:
            draw_victory()
            text = font.render("Press any key to play again", True, BLACK)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            player.vel_y = 0  # Reset player velocity
        elif game_over:
            text = font.render("Game Over", True, RED)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
            text2 = font.render("Press any key to return to menu", True, BLACK)
            screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        else:
            pygame.draw.rect(screen, player.color, player.rect)
            pygame.draw.rect(screen, boss.color, boss.rect)
            for arrow in arrows:
                pygame.draw.rect(screen, arrow.color, arrow.rect)
            for fireball in fireballs:
                pygame.draw.circle(screen, fireball.color, fireball.rect.center, fireball.radius)
            for laser in lasers:
                pygame.draw.rect(screen, laser.color, laser.rect)

            # Draw health bars
            pygame.draw.rect(screen, RED, (20, 20, 200, 20))
            pygame.draw.rect(screen, GREEN, (20, 20, player.health * 2, 20))
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH - 220, 20, 200, 20))
            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 220, 20, boss.health * 0.4, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
