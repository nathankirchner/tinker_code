import os
import pygame

# Near the top where images are loaded, update the pugicorn scaling
pugicorn = pygame.image.load(os.path.join(ASSETS_DIR, "pugicorn.png"))
pugicorn = pygame.transform.scale(pugicorn, (160, 160))  # Changed from (80, 80) to (160, 160)

class Pugicorn:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2  # Start in the middle of the screen vertically
        # or you could use a specific height like:
        # self.y = WINDOW_HEIGHT - 300  # Start 300 pixels from the bottom
        self.speed = 5
        self.collected_bones = 0
        self.rect = pugicorn.get_rect(center=(self.x, self.y))
        self.facing = 'right' 

class Glitter:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.speed = 20  # Increased from 10 to 20 for faster movement
        self.dx = dx * self.speed  # Direction vector X
        self.dy = dy * self.speed  # Direction vector Y
        self.surface = glitter_img
        self.rect = self.surface.get_rect(center=(self.x, self.y))
        self.creation_time = pygame.time.get_ticks()  # Store when glitter was created
        self.lifetime = 500  # 500 milliseconds = half a second
        self.has_hit = False  # Track if glitter has hit something

    def move(self):
        if not self.has_hit:  # Only move if hasn't hit anything
            self.x += self.dx
            self.y += self.dy
            self.rect.center = (self.x, self.y)

    def should_remove(self):
        if not self.has_hit:
            return False
        current_time = pygame.time.get_ticks()
        return current_time - self.creation_time > self.lifetime

# In the main game loop, update the glitter removal code:
        # Update glitters
        for glitter in glitters[:]:
            glitter.move()
            
            # Check for collisions with corgis
            for corgi in corgis[:]:
                if glitter.rect.colliderect(corgi.rect) and not glitter.has_hit:
                    corgi.retreat()
                    glitter.has_hit = True
                    glitter.creation_time = pygame.time.get_ticks()  # Reset timer when hit occurs
                    score += 2
                    break
            
            # Remove glitter if it's been on screen too long after hitting
            if glitter.should_remove():
                glitters.remove(glitter) 

def main():
    clock = pygame.time.Clock()
    player = Pugicorn()
    bones = []
    corgis = []
    glitters = []
    score = 0
    bones_in_bowl = 0
    
    # Add bone spawn timing variables
    bone_spawn_timer = 0
    bone_spawn_delay = 500
    max_bones = 8

    # Add corgi spawn timer
    corgi_spawn_timer = 0
    corgi_spawn_delay = 3000  # Wait 3 seconds before spawning a new corgi

    while True:
        # ... existing event handling code ...

        # Spawn new bones
        bone_spawn_timer += clock.get_time()
        if bone_spawn_timer >= bone_spawn_delay and len(bones) < max_bones:
            bones.append(Bone())
            bone_spawn_timer = 0

        # Spawn new corgi only if none exist
        if len(corgis) == 0:
            corgi_spawn_timer += clock.get_time()
            if corgi_spawn_timer >= corgi_spawn_delay:
                corgis.append(Corgi())
                corgi_spawn_timer = 0

        # ... rest of the game loop ... 