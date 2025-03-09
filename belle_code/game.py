import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pugicorn's Adventure")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
GAME_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(GAME_DIR, "assets")

pugicorn = pygame.image.load(os.path.join(ASSETS_DIR, "pugicorn.png"))
pugicorn = pygame.transform.scale(pugicorn, (80, 80))

# You'll need to download a corgi image and save it as corgi.png in assets folder
corgi = pygame.image.load(os.path.join(ASSETS_DIR, "corgi.png"))
corgi = pygame.transform.scale(corgi, (60, 60))

# Create bone and bowl images or load them
bone = pygame.Surface((20, 10))
bone.fill(WHITE)
bowl = pygame.Surface((100, 50))
bowl.fill(WHITE)

# Constants for bowl position
BOWL_WIDTH = 100
BOWL_HEIGHT = 50
BOWL_X = (WINDOW_WIDTH - BOWL_WIDTH) // 2
BOWL_Y = WINDOW_HEIGHT - 60

# Load glitter image
glitter_img = pygame.image.load(os.path.join(ASSETS_DIR, "glitter.jpg"))
glitter_img = pygame.transform.scale(glitter_img, (20, 20))  # Adjust size as needed

class Pugicorn:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - 100
        self.speed = 5
        self.collected_bones = 0
        self.rect = pugicorn.get_rect(center=(self.x, self.y))
        self.facing = 'right'  # Track which direction pugicorn is facing
        
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
            self.facing = 'left'
        if keys[pygame.K_RIGHT] and self.x < WINDOW_WIDTH:
            self.x += self.speed
            self.facing = 'right'
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < WINDOW_HEIGHT:
            self.y += self.speed
        self.rect.center = (self.x, self.y)

    def shoot_glitter(self, corgis):
        # Find the nearest corgi
        nearest_corgi = None
        min_distance = float('inf')
        
        for corgi in corgis:
            dx = corgi.x - self.x
            dy = corgi.y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest_corgi = corgi
        
        if nearest_corgi:
            # Calculate direction vector to nearest corgi
            dx = nearest_corgi.x - self.x
            dy = nearest_corgi.y - self.y
            # Normalize the vector
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length > 0:
                dx = dx / length
                dy = dy / length
                return Glitter(self.x, self.y, dx, dy)
        return None

class Bone:
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(-100, 0)
        self.speed = 2
        self.surface = bone  # Store the surface as an attribute
        self.rect = self.surface.get_rect(center=(self.x, self.y))

    def move(self):
        self.y += self.speed
        self.rect.center = (self.x, self.y)

class Corgi:
    def __init__(self):
        self.speed = 3
        # Randomly choose left or right side
        self.side = random.choice(['left', 'right'])
        if self.side == 'left':
            self.x = -60  # Start off-screen on the left
            self.speed_x = self.speed
        else:
            self.x = WINDOW_WIDTH + 60  # Start off-screen on the right
            self.speed_x = -self.speed
        self.y = random.randint(WINDOW_HEIGHT - 150, WINDOW_HEIGHT - 50)  # Near the bowl height
        self.surface = corgi
        self.rect = self.surface.get_rect(center=(self.x, self.y))
        self.has_stolen = False

    def move(self):
        self.x += self.speed_x
        self.rect.center = (self.x, self.y)

class Glitter:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.speed = 10
        self.dx = dx * self.speed  # Direction vector X
        self.dy = dy * self.speed  # Direction vector Y
        self.surface = glitter_img
        self.rect = self.surface.get_rect(center=(self.x, self.y))

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)

def main():
    clock = pygame.time.Clock()
    player = Pugicorn()
    bones = []
    corgis = []
    glitters = []
    score = 0
    bones_in_bowl = 0  # Track bones in the bowl separately

    # Define bowl rectangle for collision detection
    bowl_rect = pygame.Rect(BOWL_X, BOWL_Y, BOWL_WIDTH, BOWL_HEIGHT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    glitter = player.shoot_glitter(corgis)
                    if glitter:
                        glitters.append(glitter)

        # Update game objects
        player.move()
        
        # Generate new bones
        if random.random() < 0.02:
            bones.append(Bone())
            
        # Generate new corgis
        if random.random() < 0.01:
            corgis.append(Corgi())

        # Update bones
        for bone in bones[:]:
            bone.move()
            if bone.rect.colliderect(player.rect):
                bones.remove(bone)
                bones_in_bowl += 1  # Add to bowl instead of score
                score += 1
            elif bone.y > WINDOW_HEIGHT:
                bones.remove(bone)

        # Update corgis
        for corgi in corgis[:]:
            corgi.move()
            # Check if corgi reaches the bowl and hasn't stolen yet
            if corgi.rect.colliderect(bowl_rect) and not corgi.has_stolen and bones_in_bowl > 0:
                bones_in_bowl -= 1  # Steal a bone
                corgi.has_stolen = True
            # Remove corgi if it goes off screen
            if (corgi.side == 'left' and corgi.x > WINDOW_WIDTH + 60) or \
               (corgi.side == 'right' and corgi.x < -60):
                corgis.remove(corgi)

        # Update glitters
        for glitter in glitters[:]:
            glitter.move()
            # Remove glitter if it goes off screen
            if glitter.y < 0 or glitter.x < 0 or glitter.x > WINDOW_WIDTH:
                glitters.remove(glitter)
            for corgi in corgis[:]:
                if glitter.rect.colliderect(corgi.rect):
                    corgis.remove(corgi)
                    glitters.remove(glitter)
                    score += 2  # Bonus points for hitting corgis
                    break

        # Draw everything
        screen.fill(BLACK)
        # Draw pugicorn (flipped based on direction)
        if player.facing == 'left':
            flipped_pugicorn = pygame.transform.flip(pugicorn, True, False)
            screen.blit(flipped_pugicorn, player.rect)
        else:
            screen.blit(pugicorn, player.rect)
        
        for bone in bones:
            screen.blit(bone.surface, bone.rect)
            
        for corgi in corgis:
            screen.blit(corgi.surface, corgi.rect)
            
        for glitter in glitters:
            screen.blit(glitter.surface, glitter.rect)

        # Draw score and bowl
        pygame.draw.rect(screen, WHITE, bowl_rect)  # Bowl
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score} (Bowl: {bones_in_bowl})', True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main() 