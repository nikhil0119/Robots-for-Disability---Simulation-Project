import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
SHAPE_SIZE = 50
BASE_FALL_SPEED = 5
DANGER_SHAPE_COLOR = (255, 0, 0)  # Red (Dangerous)
SAFE_SHAPE_COLOR = (0, 255, 0)  # Green (Safe)
NEUTRAL_SHAPE_COLOR = (0, 0, 255)  # Blue (Neutral)
EXTRA_SHAPE_COLOR = (255, 255, 0)  # Yellow (Extra points)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT = pygame.font.SysFont('Arial', 32)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Focus Training Game")

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 10

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

# Falling Shape Class
class FallingShape(pygame.sprite.Sprite):
    def __init__(self, shape_type, speed):
        super().__init__()
        self.image = pygame.Surface((SHAPE_SIZE, SHAPE_SIZE))
        self.color = self.get_color(shape_type)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - SHAPE_SIZE)
        self.rect.y = -SHAPE_SIZE
        self.speed = speed
        self.shape_type = shape_type

    def get_color(self, shape_type):
        if shape_type == "dangerous":
            return DANGER_SHAPE_COLOR
        elif shape_type == "safe":
            return SAFE_SHAPE_COLOR
        elif shape_type == "neutral":
            return NEUTRAL_SHAPE_COLOR
        elif shape_type == "extra":
            return EXTRA_SHAPE_COLOR

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Function to display text input GUI
def ask_duration():
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return int(text)
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(WHITE)
        txt_surface = FONT.render(text, True, BLACK)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        prompt_text = FONT.render("Enter game duration (seconds):", True, BLACK)
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 75))
        pygame.display.flip()

# Game Function
def run_game():
    player = Player()
    all_sprites = pygame.sprite.Group()
    falling_shapes = pygame.sprite.Group()
    all_sprites.add(player)

    # Gameplay Variables
    clock = pygame.time.Clock()
    score = 0
    time_elapsed = 0
    fall_speed = BASE_FALL_SPEED
    yellow_count = 0
    blue_count = 0

    # Ask user for game duration
    duration = ask_duration()
    game_start_time = pygame.time.get_ticks()
    
    running = True

    while running:
        screen.fill(WHITE)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update time and adjust speed
        current_time = pygame.time.get_ticks()
        time_elapsed = (current_time - game_start_time) / 1000  # Convert to seconds
        if time_elapsed > duration:
            running = False  # End the game after user-defined duration

        # Gradual increase in fall speed
        fall_speed = BASE_FALL_SPEED + (time_elapsed // 3)  # Speed increases every 3 seconds

        # Spawn Shapes
        if random.randint(1, 15) == 1:  # Adjust spawn frequency
            shape_type = random.choices(
                ["dangerous", "safe", "neutral", "extra"],
                weights=[4, 6, 2 if blue_count < 5 else 0, 1 if yellow_count < 3 else 0],
            )[0]
            if shape_type == "extra":
                yellow_count += 1
            elif shape_type == "neutral":
                blue_count += 1

            shape = FallingShape(shape_type, fall_speed)
            falling_shapes.add(shape)
            all_sprites.add(shape)

        # Update Sprites
        all_sprites.update()

        # Collision Detection
        for shape in pygame.sprite.spritecollide(player, falling_shapes, True):
            if shape.shape_type == "dangerous":
                running = False  # End game on collision with dangerous shape
            elif shape.shape_type == "safe":
                score += 1
            elif shape.shape_type == "extra":
                score += 5  # Extra points for yellow shapes

        # Draw Sprites
        all_sprites.draw(screen)

        # Display Score and Time
        score_text = FONT.render(f"Score: {score}", True, BLACK)
        time_text = FONT.render(f"Time: {max(0, int(duration - time_elapsed))}s", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 50))

        # Update Display
        pygame.display.flip()

        # Maintain FPS
        clock.tick(FPS)

    # End of Game - Restart or Quit
    while True:
        screen.fill(WHITE)
        end_text = FONT.render("Game Over!", True, BLACK)
        score_text = FONT.render(f"Final Score: {score}", True, BLACK)
        restart_text = FONT.render("Press R to Restart or Q to Quit", True, BLACK)
        screen.blit(end_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return  # Restart the game
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Start the Game
while True:
    run_game()
