import pygame
import random
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 1200  

WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Wesley's hurdling game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0) 
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
PINK = (250, 190, 212)
# Add mountain colors
SKY_COLOR = (115, 185, 255)  # Light blue sky
MOUNTAIN_COLORS = [
    (90, 90, 90),    # Dark gray
    (120, 120, 120), # Medium gray
    (150, 150, 150)  # Light gray
]

# Add this after the other color definitions
INPUT_BOX_COLOR = (100, 100, 100)
INPUT_TEXT_COLOR = WHITE

# Player properties
class Player:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = 100
        self.y = WINDOW_HEIGHT - 60
        self.velocity_y = 0
        self.jumping = False  
        self.speed = 10
        self.lives = 3
        # Add zombie colors
        self.body_color = (0, 150, 20)  # Zombie green
        self.face_color = (70, 100, 0)  # Darker green for features

    def jump(self):
        if not self.jumping:
            self.velocity_y = -15
            self.jumping = True

    def move(self):
        # Gravity
        self.velocity_y += 0.8 
        self.y += self.velocity_y

        # Ground collision
        if self.y > WINDOW_HEIGHT - 60:
            self.y = WINDOW_HEIGHT - 60
            self.jumping = False
            self.velocity_y = 0

    def draw(self, screen):
        # Draw main body (green cube)
        pygame.draw.rect(screen, self.body_color, (self.x, self.y, self.width, self.height))
        
        # Draw zombie face features
        # Eyes (2 small dark green rectangles)
        eye_width = 6
        eye_height = 6
        pygame.draw.rect(screen, self.face_color, (self.x + 5, self.y + 8, eye_width, eye_height))
        pygame.draw.rect(screen, self.face_color, (self.x + 19, self.y + 8, eye_width, eye_height))
        
        # Mouth (dark green rectangle)
        mouth_width = 12
        mouth_height = 4
        pygame.draw.rect(screen, self.face_color, (self.x + 9, self.y + 18, mouth_width, mouth_height))

# Hurdle properties
class Hurdle:
    def __init__(self, x):
        self.width = 50  # Make it wider
        self.height = 45  # Make it taller
        self.x = x
        self.y = WINDOW_HEIGHT - 80
        # Colors for hurdle parts
        self.post_color = (192, 192, 192)  # Silver/gray for posts
        self.bar_color = (200, 50, 50)  # White for top bar
        self.post_width = 5  # Width of each post
        self.bar_height = 5 # Height of the top bar

    def move(self, speed):
        self.x -= speed

    def draw(self, screen):
        # Draw left post
        pygame.draw.rect(screen, self.post_color, 
                        (self.x, self.y, self.post_width, self.height))
        
        # Draw right post
        pygame.draw.rect(screen, self.post_color, 
                        (self.x + self.width - self.post_width, self.y, 
                         self.post_width, self.height))
        
        # Draw top bar
        pygame.draw.rect(screen, self.bar_color,
                        (self.x, self.y, self.width, self.bar_height))

# Add mountain class
class Mountain:
    def __init__(self, x, height, color):
        self.x = x
        self.height = height
        self.color = color
        self.width = 200  # Width of mountain base
        
    def draw(self, screen):
        points = [
            (self.x, WINDOW_HEIGHT),  # Bottom left
            (self.x + self.width//2, WINDOW_HEIGHT - self.height),  # Peak
            (self.x + self.width, WINDOW_HEIGHT),  # Bottom right
        ]
        pygame.draw.polygon(screen, self.color, points)

# Add this class for handling name input
class InputBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ''
        self.active = True
        self.font = pygame.font.Font(None, 36)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return None

    def draw(self, screen):
        txt_surface = self.font.render(self.text, True, INPUT_TEXT_COLOR)
        width = max(200, txt_surface.get_width()+10)
        self.rect.w = width
        screen.blit(txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, INPUT_BOX_COLOR, self.rect, 2)

# Add after the Mountain class
class Creeper:
    def __init__(self, x):
        self.width = 30
        self.height = 30
        self.x = x
        self.y = WINDOW_HEIGHT - 60  # Same level as ground
        self.color = (50, 168, 82)  # Creeper green
        self.face_color = (0, 0, 0)  # Black for face
        self.collected = False
        self.direction = 1  # 1 for right, -1 for left
        self.movement_range = 100  # How far it moves side to side
        self.start_x = x  # Remember starting position
        # Add jumping properties
        self.velocity_y = 0
        self.jumping = False

    def move(self, speed):
        self.x += self.direction * 3  # Move 3 pixels each frame
        
        # Change direction when reaching movement limits
        if self.x > self.start_x + self.movement_range:
            self.direction = -1
        elif self.x < self.start_x - self.movement_range:
            self.direction = 1

        # Apply gravity
        self.velocity_y += 0.8
        self.y += self.velocity_y

        # Ground collision
        if self.y > WINDOW_HEIGHT - 60:
            self.y = WINDOW_HEIGHT - 60
            self.jumping = False
            self.velocity_y = 0

    def jump(self):
        if not self.jumping:
            self.velocity_y = -15
            self.jumping = True

    def draw(self, screen):
        if not self.collected:
            # Draw body
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            
            # Draw face (classic creeper face)
            # Eyes
            pygame.draw.rect(screen, self.face_color, (self.x + 5, self.y + 8, 6, 6))
            pygame.draw.rect(screen, self.face_color, (self.x + 19, self.y + 8, 6, 6))
            
            # Mouth
            pygame.draw.rect(screen, self.face_color, (self.x + 9, self.y + 14, 12, 8))
            pygame.draw.rect(screen, self.face_color, (self.x + 13, self.y + 18, 4, 4))

# Game setup
player = Player()
hurdles = [Hurdle(WINDOW_WIDTH + i * 300) for i in range(3)]
clock = pygame.time.Clock()
game_speed = 5
score = 0
creepers_squashed = 0  # New counter for creepers

# Add mountains to game setup
mountains = [
    Mountain(0, 200, MOUNTAIN_COLORS[0]),
    Mountain(150, 250, MOUNTAIN_COLORS[1]),
    Mountain(400, 180, MOUNTAIN_COLORS[2]),
    Mountain(600, 220, MOUNTAIN_COLORS[0])
]

# Add after game setup section
creepers = [Creeper(300 + i * 400) for i in range(3)]  # Spawn 3 creepers at fixed positions

# Add this function near the top of the file after imports
def update_player_score(player_name, new_score):
    scores = {}
    
    # Read existing scores if file exists
    if os.path.exists('my scores.txt'):
        with open('my scores.txt', 'r') as f:
            for line in f:
                if '- Player:' in line:
                    parts = line.split(' - Player: ')[1]
                    name = parts.split(' - Score: ')[0]
                    score = int(parts.split(' - Score: ')[1])
                    scores[name] = score
    
    # Update score for player (add to existing score if player exists)
    if player_name in scores:
        scores[player_name] += new_score
    else:
        scores[player_name] = new_score
    
    # Write all scores back to file
    with open('my scores.txt', 'w') as f:
        for name, score in scores.items():
            date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
            f.write(f'{date_str} - Player: {name} - Score: {score}\n')

# Add after game setup, before the main game loop
def show_countdown():
    font = pygame.font.Font(None, 74)
    countdown_numbers = ["3", "2", "1", "GO!"]
    
    for number in countdown_numbers:
        screen.fill(SKY_COLOR)
        # Draw mountains
        for mountain in mountains:
            mountain.draw(screen)
        # Draw ground
        pygame.draw.rect(screen, (34, 139, 34), (0, WINDOW_HEIGHT - 30, WINDOW_WIDTH, 30))
        
        text = font.render(number, True, BLACK)
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(1000)  # Wait 1 second between numbers

# Show countdown before game starts
show_countdown()

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    # Get keyboard input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.x > 0:
        player.x -= player.speed
    if keys[pygame.K_RIGHT] and player.x < WINDOW_WIDTH - player.width:
        player.x += player.speed

    # Update game objects
    player.move()
    
    # Move and reset hurdles
    for hurdle in hurdles:
        hurdle.move(game_speed)
        if hurdle.x < -hurdle.width:
            hurdle.x = WINDOW_WIDTH
            score += 1

        # Collision detection
        if (player.x < hurdle.x + hurdle.width and 
            player.x + player.width > hurdle.x and 
            player.y < hurdle.y + hurdle.height and 
            player.y + player.height > hurdle.y):
            player.lives -= 1
            hurdle.x = WINDOW_WIDTH
            
            # Flash red and orange in an expanding circle pattern
            for radius in range(0, 200, 40):  # Explosion grows in size
                # Red flash
                screen.fill(SKY_COLOR)
                pygame.draw.circle(screen, (255, 0, 0), 
                                 (int(player.x + player.width/2), 
                                  int(player.y + player.height/2)), 
                                 radius)
                pygame.display.flip()
                pygame.time.delay(50)
                
                # Orange flash
                screen.fill(SKY_COLOR)
                pygame.draw.circle(screen, (255, 140, 0), 
                                 (int(player.x + player.width/2), 
                                  int(player.y + player.height/2)), 
                                 radius + 20)  # Slightly larger orange circle
                pygame.display.flip()
                pygame.time.delay(50)
            
            # Show countdown after explosion if player still has lives
            if player.lives > 0:
                show_countdown()
            
            if player.lives <= 0:
                # Game Over screen and name input
                input_box = InputBox(WINDOW_WIDTH/2 - 100, WINDOW_HEIGHT/2 + 50, 200, 32)
                waiting_for_name = True
                
                while waiting_for_name:
                    screen.fill((255, 0, 0))  # Red background
                    
                    # Draw Game Over text
                    font = pygame.font.Font(None, 74)
                    game_over_text = font.render('GAME OVER', True, WHITE)
                    text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 50))
                    screen.blit(game_over_text, text_rect)
                    
                    # Draw score
                    score_font = pygame.font.Font(None, 48)
                    final_score = score_font.render(f'Final Score: {score}', True, WHITE)
                    score_rect = final_score.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
                    screen.blit(final_score, score_rect)
                    
                    # Draw input prompt
                    prompt_font = pygame.font.Font(None, 36)
                    prompt = prompt_font.render('Enter your name:', True, WHITE)
                    prompt_rect = prompt.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 30))
                    screen.blit(prompt, prompt_rect)
                    
                    # Handle input events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        name = input_box.handle_event(event)
                        if name:  # Enter was pressed
                            update_player_score(name, score)
                            waiting_for_name = False
                    
                    input_box.draw(screen)
                    pygame.display.flip()
                
                pygame.time.delay(1000)  # Short delay after name entry
                
                # Reset game state instead of quitting
                player.lives = 3
                score = 0
                creepers_squashed = 0
                player.x = 100
                player.y = WINDOW_HEIGHT - 60
                player.velocity_y = 0
                player.jumping = False
                
                # Reset hurdles
                hurdles = [Hurdle(WINDOW_WIDTH + i * 300) for i in range(3)]
                
                # Reset creepers
                creepers = [Creeper(300 + i * 400) for i in range(3)]
                
                # Show countdown before restarting
                show_countdown()
                
                continue  # Skip to next iteration of game loop

    # Update and check creeper collisions
    for creeper in creepers:
        creeper.move(game_speed)
        
        # Make creepers jump over hurdles
        for hurdle in hurdles:
            # Check if hurdle is close and creeper is on the ground
            if (not creeper.jumping and 
                abs(creeper.x - hurdle.x) < 100 and 
                creeper.x < hurdle.x):
                creeper.jump()
        
        # Check if player lands on top of creeper
        if not creeper.collected:
            if (player.x < creeper.x + creeper.width and 
                player.x + player.width > creeper.x and 
                player.y + player.height >= creeper.y and 
                player.y + player.height <= creeper.y + 10):
                score += 10
                creepers_squashed += 1
                creeper.collected = True
                # Transform player into zombie
                player.body_color = (0, 150, 20)  # Zombie green
                player.face_color = (70, 100, 0)  # Darker green for features

    # Draw everything
    screen.fill(SKY_COLOR)  # Fill with sky color
    
    # Draw mountains
    for mountain in mountains:
        mountain.draw(screen)
        
    # Draw ground
    pygame.draw.rect(screen, (34, 139, 34), (0, WINDOW_HEIGHT - 30, WINDOW_WIDTH, 30))
    
    # Draw existing game objects
    player.draw(screen)
    for hurdle in hurdles:
        hurdle.draw(screen)

    # Draw creepers
    for creeper in creepers:
        creeper.draw(screen)

    # Draw score, lives, and creepers squashed
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, BLACK)
    lives_text = font.render(f'Lives: {player.lives}', True, BLACK)
    creeper_text = font.render(f'Creepers Squashed: {creepers_squashed}', True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(creeper_text, (10, 70))  # Display below lives

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
