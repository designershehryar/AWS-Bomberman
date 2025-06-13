import pygame
import sys
import random
import os
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 50
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
BROWN = (165, 42, 42)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Create monster types
MONSTER_TYPES = ["slime", "ghost", "goblin"]

# Sound effects
try:
    # Create assets directory if it doesn't exist
    sound_dir = os.path.join("assets", "sounds")
    os.makedirs(sound_dir, exist_ok=True)
    
    # Sound file paths
    SOUND_BOMB = os.path.join(sound_dir, "bomb.wav")
    SOUND_EXPLOSION = os.path.join(sound_dir, "explosion.wav")
    SOUND_ENEMY_DIE = os.path.join(sound_dir, "enemy_die.wav")
    SOUND_PLAYER_DIE = os.path.join(sound_dir, "player_die.wav")
    SOUND_GAME_OVER = os.path.join(sound_dir, "game_over.wav")
    SOUND_WIN = os.path.join(sound_dir, "win.wav")
    SOUND_BACKGROUND = os.path.join(sound_dir, "background.wav")
    
    # Create empty sound files if they don't exist
    for sound_file in [SOUND_BOMB, SOUND_EXPLOSION, SOUND_ENEMY_DIE, 
                      SOUND_PLAYER_DIE, SOUND_GAME_OVER, SOUND_WIN, SOUND_BACKGROUND]:
        if not os.path.exists(sound_file):
            with open(sound_file, 'wb') as f:
                # Create a minimal valid WAV file
                # RIFF header
                f.write(b'RIFF')
                f.write((36).to_bytes(4, 'little'))  # File size - 8
                f.write(b'WAVE')
                # Format chunk
                f.write(b'fmt ')
                f.write((16).to_bytes(4, 'little'))  # Chunk size
                f.write((1).to_bytes(2, 'little'))   # PCM format
                f.write((1).to_bytes(2, 'little'))   # Mono
                f.write((22050).to_bytes(4, 'little'))  # Sample rate
                f.write((22050).to_bytes(4, 'little'))  # Byte rate
                f.write((1).to_bytes(2, 'little'))   # Block align
                f.write((8).to_bytes(2, 'little'))   # Bits per sample
                # Data chunk
                f.write(b'data')
                f.write((0).to_bytes(4, 'little'))   # Data size
    
    # Load sounds
    sound_bomb = pygame.mixer.Sound(SOUND_BOMB)
    sound_explosion = pygame.mixer.Sound(SOUND_EXPLOSION)
    sound_enemy_die = pygame.mixer.Sound(SOUND_ENEMY_DIE)
    sound_player_die = pygame.mixer.Sound(SOUND_PLAYER_DIE)
    sound_game_over = pygame.mixer.Sound(SOUND_GAME_OVER)
    sound_win = pygame.mixer.Sound(SOUND_WIN)
    
    # Start background music
    pygame.mixer.music.load(SOUND_BACKGROUND)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop indefinitely
    
    has_sound = True
    
except Exception as e:
    print(f"Error loading sounds: {e}")
    has_sound = False
    
    # Create dummy sound class if loading fails
    class DummySound:
        def play(self):
            pass
    
    sound_bomb = DummySound()
    sound_explosion = DummySound()
    sound_enemy_die = DummySound()
    sound_player_die = DummySound()
    sound_game_over = DummySound()
    sound_win = DummySound()

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bomberman")
clock = pygame.time.Clock()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bombs = 1
        self.speed = 1
        self.alive = True
        self.lives = 3
        self.score = 0
        self.direction = (0, 1)  # Facing down initially
        self.animation_frame = 0
        self.animation_counter = 0
        self.animation_speed = 5
        self.last_moved = False
    
    def move(self, dx, dy, grid):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Update direction
        if dx != 0 or dy != 0:
            self.direction = (dx, dy)
            self.last_moved = True
        
        # Check if the new position is valid
        if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and 
            grid[new_y][new_x] == 0):
            self.x = new_x
            self.y = new_y
    
    def place_bomb(self, bombs):
        if self.bombs > 0:
            bombs.append(Bomb(self.x, self.y))
            self.bombs -= 1
    
    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.alive = False
        return self.alive
    
    def update(self):
        # Update animation
        if self.last_moved:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.animation_frame = (self.animation_frame + 1) % 4
            self.last_moved = False
    
    def draw(self):
        # Base player body (rounded rectangle)
        player_rect = pygame.Rect(self.x * GRID_SIZE + 5, self.y * GRID_SIZE + 5, 
                                 GRID_SIZE - 10, GRID_SIZE - 10)
        pygame.draw.rect(screen, BLUE, player_rect, border_radius=8)
        
        # Draw face based on direction
        face_x = self.x * GRID_SIZE + GRID_SIZE // 2
        face_y = self.y * GRID_SIZE + GRID_SIZE // 2
        
        # Eyes
        eye_offset_x = 0
        eye_offset_y = 0
        
        # Adjust eye position based on direction
        if self.direction[0] > 0:  # Right
            eye_offset_x = 5
        elif self.direction[0] < 0:  # Left
            eye_offset_x = -5
        
        if self.direction[1] > 0:  # Down
            eye_offset_y = 3
        elif self.direction[1] < 0:  # Up
            eye_offset_y = -3
        
        # Left eye
        pygame.draw.circle(screen, WHITE, 
                         (face_x - 8 + eye_offset_x, face_y - 5 + eye_offset_y), 
                         4)
        pygame.draw.circle(screen, BLACK, 
                         (face_x - 8 + eye_offset_x, face_y - 5 + eye_offset_y), 
                         2)
        
        # Right eye
        pygame.draw.circle(screen, WHITE, 
                         (face_x + 8 + eye_offset_x, face_y - 5 + eye_offset_y), 
                         4)
        pygame.draw.circle(screen, BLACK, 
                         (face_x + 8 + eye_offset_x, face_y - 5 + eye_offset_y), 
                         2)
        
        # Mouth (changes with animation frame)
        if self.animation_frame % 2 == 0:
            # Smile
            pygame.draw.arc(screen, BLACK, 
                          (face_x - 10, face_y + 2, 20, 10),
                          0, 3.14, 2)
        else:
            # "O" mouth
            pygame.draw.circle(screen, BLACK, (face_x, face_y + 7), 5, 2)
        
        # Draw helmet/hat
        helmet_color = (50, 50, 200)  # Darker blue
        pygame.draw.ellipse(screen, helmet_color,
                          (self.x * GRID_SIZE + 5, self.y * GRID_SIZE, 
                           GRID_SIZE - 10, GRID_SIZE // 3))
        
        # Draw antenna on helmet
        pygame.draw.line(screen, BLACK,
                       (face_x, self.y * GRID_SIZE + 2),
                       (face_x, self.y * GRID_SIZE - 8),
                       2)
        pygame.draw.circle(screen, RED, (face_x, self.y * GRID_SIZE - 8), 3)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 1
        self.move_counter = 0
        self.move_delay = 15  # Move every 15 frames (0.5 seconds at 30 FPS)
        self.alive = True
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.monster_type = random.choice(MONSTER_TYPES)
        self.animation_frame = 0
        self.animation_speed = 5
        self.animation_counter = 0
        
        # Monster colors based on type
        self.colors = {
            "slime": (0, 200, 0),      # Green slime
            "ghost": (200, 200, 255),  # Light blue ghost
            "goblin": (255, 100, 0)    # Orange goblin
        }
    
    def update(self, grid, explosions):
        # Check if enemy is hit by explosion
        for explosion in explosions:
            for x, y in explosion.tiles:
                if self.x == x and self.y == y:
                    self.alive = False
                    return
        
        # Move enemy
        self.move_counter += 1
        if self.move_counter >= self.move_delay:
            self.move_counter = 0
            
            # Try to move in current direction
            new_x = self.x + self.direction[0]
            new_y = self.y + self.direction[1]
            
            # If can't move in current direction, choose a new random direction
            if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and grid[new_y][new_x] == 0):
                # Choose a new random direction
                possible_directions = []
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = self.x + dx, self.y + dy
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and grid[ny][nx] == 0:
                        possible_directions.append((dx, dy))
                
                if possible_directions:
                    self.direction = random.choice(possible_directions)
                    new_x = self.x + self.direction[0]
                    new_y = self.y + self.direction[1]
                else:
                    # No valid moves, stay in place
                    return
            
            self.x, self.y = new_x, new_y
        
        # Update animation
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % 4
    
    def draw(self):
        if not self.alive:
            return
            
        color = self.colors.get(self.monster_type, ORANGE)
        rect = pygame.Rect(self.x * GRID_SIZE + 5, self.y * GRID_SIZE + 5, 
                          GRID_SIZE - 10, GRID_SIZE - 10)
        
        # Draw base monster shape
        pygame.draw.rect(screen, color, rect)
        
        # Draw monster features based on type
        if self.monster_type == "slime":
            # Draw slime eyes
            eye_size = GRID_SIZE // 8
            eye_y = self.y * GRID_SIZE + GRID_SIZE // 3
            
            # Eyes move slightly based on animation frame
            eye_offset = self.animation_frame % 2 * 2
            
            # Left eye
            pygame.draw.circle(screen, WHITE, 
                             (self.x * GRID_SIZE + GRID_SIZE // 3, eye_y + eye_offset), 
                             eye_size)
            pygame.draw.circle(screen, BLACK, 
                             (self.x * GRID_SIZE + GRID_SIZE // 3, eye_y + eye_offset), 
                             eye_size // 2)
            
            # Right eye
            pygame.draw.circle(screen, WHITE, 
                             (self.x * GRID_SIZE + GRID_SIZE * 2 // 3, eye_y + eye_offset), 
                             eye_size)
            pygame.draw.circle(screen, BLACK, 
                             (self.x * GRID_SIZE + GRID_SIZE * 2 // 3, eye_y + eye_offset), 
                             eye_size // 2)
            
            # Mouth
            mouth_y = self.y * GRID_SIZE + GRID_SIZE * 2 // 3
            pygame.draw.arc(screen, BLACK, 
                          (self.x * GRID_SIZE + GRID_SIZE // 4, mouth_y, 
                           GRID_SIZE // 2, GRID_SIZE // 4),
                          0, 3.14, 2)
            
        elif self.monster_type == "ghost":
            # Draw ghost eyes
            eye_size = GRID_SIZE // 8
            eye_y = self.y * GRID_SIZE + GRID_SIZE // 3
            
            # Eyes move based on direction
            eye_x_offset = 0
            eye_y_offset = 0
            if self.direction[0] > 0:  # Moving right
                eye_x_offset = 2
            elif self.direction[0] < 0:  # Moving left
                eye_x_offset = -2
            elif self.direction[1] > 0:  # Moving down
                eye_y_offset = 2
            elif self.direction[1] < 0:  # Moving up
                eye_y_offset = -2
            
            # Left eye
            pygame.draw.circle(screen, WHITE, 
                             (self.x * GRID_SIZE + GRID_SIZE // 3 + eye_x_offset, 
                              eye_y + eye_y_offset), 
                             eye_size)
            pygame.draw.circle(screen, BLACK, 
                             (self.x * GRID_SIZE + GRID_SIZE // 3 + eye_x_offset, 
                              eye_y + eye_y_offset), 
                             eye_size // 2)
            
            # Right eye
            pygame.draw.circle(screen, WHITE, 
                             (self.x * GRID_SIZE + GRID_SIZE * 2 // 3 + eye_x_offset, 
                              eye_y + eye_y_offset), 
                             eye_size)
            pygame.draw.circle(screen, BLACK, 
                             (self.x * GRID_SIZE + GRID_SIZE * 2 // 3 + eye_x_offset, 
                              eye_y + eye_y_offset), 
                             eye_size // 2)
            
            # Ghost bottom edge (wavy)
            bottom_y = self.y * GRID_SIZE + GRID_SIZE - 5
            wave_height = 3 + self.animation_frame % 2 * 2
            
            for i in range(3):
                pygame.draw.arc(screen, color,
                              (self.x * GRID_SIZE + 5 + i * (GRID_SIZE - 10) // 3,
                               bottom_y - wave_height,
                               (GRID_SIZE - 10) // 3, wave_height * 2),
                              3.14, 2 * 3.14, 2)
            
        elif self.monster_type == "goblin":
            # Draw goblin eyes
            eye_size = GRID_SIZE // 8
            eye_y = self.y * GRID_SIZE + GRID_SIZE // 3
            
            # Angry eyes
            pygame.draw.circle(screen, WHITE, 
                             (self.x * GRID_SIZE + GRID_SIZE // 3, eye_y), 
                             eye_size)
            pygame.draw.circle(screen, BLACK, 
                             (self.x * GRID_SIZE + GRID_SIZE // 3, eye_y), 
                             eye_size // 2)
            
            pygame.draw.circle(screen, WHITE, 
                             (self.x * GRID_SIZE + GRID_SIZE * 2 // 3, eye_y), 
                             eye_size)
            pygame.draw.circle(screen, BLACK, 
                             (self.x * GRID_SIZE + GRID_SIZE * 2 // 3, eye_y), 
                             eye_size // 2)
            
            # Eyebrows
            eyebrow_y = self.y * GRID_SIZE + GRID_SIZE // 4
            pygame.draw.line(screen, BLACK,
                           (self.x * GRID_SIZE + GRID_SIZE // 4, eyebrow_y),
                           (self.x * GRID_SIZE + GRID_SIZE // 2 - 2, eyebrow_y - 3),
                           2)
            pygame.draw.line(screen, BLACK,
                           (self.x * GRID_SIZE + GRID_SIZE // 2 + 2, eyebrow_y - 3),
                           (self.x * GRID_SIZE + GRID_SIZE * 3 // 4, eyebrow_y),
                           2)
            
            # Mouth with teeth
            mouth_y = self.y * GRID_SIZE + GRID_SIZE * 2 // 3
            pygame.draw.rect(screen, BLACK,
                           (self.x * GRID_SIZE + GRID_SIZE // 3,
                            mouth_y,
                            GRID_SIZE // 3,
                            GRID_SIZE // 6))
            
            # Teeth (alternating based on animation frame)
            if self.animation_frame % 2 == 0:
                pygame.draw.rect(screen, WHITE,
                               (self.x * GRID_SIZE + GRID_SIZE // 3 + 2,
                                mouth_y + 2,
                                GRID_SIZE // 10,
                                GRID_SIZE // 10))
                pygame.draw.rect(screen, WHITE,
                               (self.x * GRID_SIZE + GRID_SIZE // 2 + 2,
                                mouth_y + 2,
                                GRID_SIZE // 10,
                                GRID_SIZE // 10))
            else:
                pygame.draw.rect(screen, WHITE,
                               (self.x * GRID_SIZE + GRID_SIZE // 3 + GRID_SIZE // 8,
                                mouth_y + 2,
                                GRID_SIZE // 10,
                                GRID_SIZE // 10))
                pygame.draw.rect(screen, WHITE,
                               (self.x * GRID_SIZE + GRID_SIZE // 2 - GRID_SIZE // 8,
                                mouth_y + 2,
                                GRID_SIZE // 10,
                                GRID_SIZE // 10))

class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 90  # 3 seconds at 30 FPS
        self.exploded = False
        self.explosion_range = 2
        self.pulse_size = 0
        self.growing = True
        self.flash_timer = 0
        self.flash_state = False
    
    def update(self):
        if not self.exploded:
            self.timer -= 1
            
            # Animate bomb pulsing
            if self.growing:
                self.pulse_size += 0.5
                if self.pulse_size >= 5:
                    self.growing = False
            else:
                self.pulse_size -= 0.5
                if self.pulse_size <= 0:
                    self.growing = True
            
            # Flash faster as timer gets lower
            self.flash_timer += 1
            flash_speed = 15
            if self.timer < 30:  # Last second
                flash_speed = 5
            elif self.timer < 60:  # Second to last second
                flash_speed = 10
                
            if self.flash_timer >= flash_speed:
                self.flash_timer = 0
                self.flash_state = not self.flash_state
            
            if self.timer <= 0:
                self.exploded = True
                if has_sound:
                    sound_explosion.play()
                return True
        return False
    
    def draw(self):
        if not self.exploded:
            center_x = self.x * GRID_SIZE + GRID_SIZE // 2
            center_y = self.y * GRID_SIZE + GRID_SIZE // 2
            bomb_radius = GRID_SIZE // 3
            
            # Draw bomb body (slightly oval)
            pygame.draw.ellipse(screen, BLACK, 
                              (center_x - bomb_radius, 
                               center_y - bomb_radius,
                               bomb_radius * 2,
                               bomb_radius * 2 + 5))
            
            # Draw bomb cap (top part)
            cap_width = bomb_radius // 2
            pygame.draw.rect(screen, GRAY,
                           (center_x - cap_width // 2,
                            center_y - bomb_radius - 5,
                            cap_width,
                            5))
            
            # Draw bomb fuse
            fuse_start_x = center_x
            fuse_start_y = center_y - bomb_radius - 3
            
            # Wavy fuse line
            fuse_segments = 4
            fuse_height = 12
            prev_x, prev_y = fuse_start_x, fuse_start_y
            
            for i in range(1, fuse_segments + 1):
                next_x = fuse_start_x + (i % 2) * 4 - 2
                next_y = fuse_start_y - (i * fuse_height / fuse_segments)
                pygame.draw.line(screen, BROWN, (prev_x, prev_y), (next_x, next_y), 3)
                prev_x, prev_y = next_x, next_y
            
            # Draw fuse spark (flashing)
            if self.flash_state:
                spark_color = RED
            else:
                spark_color = ORANGE
                
            pygame.draw.circle(screen, spark_color, 
                             (prev_x, prev_y - 3), 
                             3 + self.pulse_size)
            
            # Draw bomb highlight (reflection)
            pygame.draw.ellipse(screen, WHITE, 
                              (center_x - bomb_radius + 5, 
                               center_y - bomb_radius + 5,
                               bomb_radius - 2,
                               bomb_radius - 2))
            
            # Draw "BOMB" text or timer numbers
            if self.timer < 30:  # Show countdown in last second
                font = pygame.font.SysFont(None, 20)
                text = font.render(str((self.timer // 3) + 1), True, WHITE)
                screen.blit(text, (center_x - text.get_width() // 2, 
                                  center_y - text.get_height() // 2))

class Explosion:
    def __init__(self, x, y, range_val, grid):
        self.x = x
        self.y = y
        self.range = range_val
        self.timer = 30  # 1 second at 30 FPS
        self.tiles = self.calculate_tiles(grid)
        self.animation_frame = 0
        self.animation_speed = 3
    
    def calculate_tiles(self, grid):
        tiles = [(self.x, self.y)]  # Center tile
        
        # Check in four directions
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for r in range(1, self.range + 1):
                nx, ny = self.x + dx * r, self.y + dy * r
                
                # Check if out of bounds
                if not (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT):
                    break
                
                # If hit a wall, stop in this direction
                if grid[ny][nx] == 1:
                    break
                
                # Add this tile to explosion
                tiles.append((nx, ny))
                
                # If hit a destructible block, destroy it and stop
                if grid[ny][nx] == 2:
                    grid[ny][nx] = 0
                    break
        
        return tiles
    
    def update(self):
        self.timer -= 1
        # Update animation frame
        if self.timer % self.animation_speed == 0:
            self.animation_frame = (self.animation_frame + 1) % 3
        return self.timer <= 0
    
    def draw(self):
        for x, y in self.tiles:
            # Base explosion
            pygame.draw.rect(screen, RED, 
                           (x * GRID_SIZE, y * GRID_SIZE, 
                            GRID_SIZE, GRID_SIZE))
            
            # Add explosion details based on animation frame
            center_x = x * GRID_SIZE + GRID_SIZE // 2
            center_y = y * GRID_SIZE + GRID_SIZE // 2
            
            # Draw explosion waves
            wave_colors = [(255, 200, 0), (255, 150, 0), (255, 100, 0)]
            for i, color in enumerate(wave_colors):
                size = GRID_SIZE // 2 - i * 5 - self.animation_frame * 2
                if size > 0:
                    pygame.draw.circle(screen, color, (center_x, center_y), size)
            
            # Draw sparks
            spark_count = 5 + self.animation_frame * 2
            for _ in range(spark_count):
                angle = random.random() * 6.28  # 2*pi
                distance = random.random() * GRID_SIZE // 3
                spark_x = center_x + int(math.cos(angle) * distance)
                spark_y = center_y + int(math.sin(angle) * distance)
                spark_size = random.randint(1, 3)
                pygame.draw.circle(screen, (255, 255, 200), 
                                 (spark_x, spark_y), spark_size)

def create_grid():
    # 0 = empty, 1 = wall (indestructible), 2 = block (destructible)
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    # Add walls around the edges
    for x in range(GRID_WIDTH):
        grid[0][x] = 1
        grid[GRID_HEIGHT-1][x] = 1
    
    for y in range(GRID_HEIGHT):
        grid[y][0] = 1
        grid[y][GRID_WIDTH-1] = 1
    
    # Add walls in a grid pattern
    for y in range(2, GRID_HEIGHT - 2, 2):
        for x in range(2, GRID_WIDTH - 2, 2):
            grid[y][x] = 1
    
    # Add random destructible blocks
    for y in range(1, GRID_HEIGHT - 1):
        for x in range(1, GRID_WIDTH - 1):
            if grid[y][x] == 0 and random.random() < 0.3:
                # Keep the player's starting area clear
                if not (x < 3 and y < 3):
                    grid[y][x] = 2
    
    # Ensure player starting position is clear
    grid[1][1] = 0
    
    return grid

def spawn_enemies(grid, num_enemies):
    enemies = []
    for _ in range(num_enemies):
        # Find a random empty cell for the enemy
        while True:
            x = random.randint(1, GRID_WIDTH - 2)
            y = random.randint(1, GRID_HEIGHT - 2)
            # Make sure it's empty and not too close to player start
            if grid[y][x] == 0 and (x > 3 or y > 3):
                enemies.append(Enemy(x, y))
                break
    return enemies

def draw_grid(grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if grid[y][x] == 0:  # Empty
                pygame.draw.rect(screen, GREEN, rect)
            elif grid[y][x] == 1:  # Wall
                pygame.draw.rect(screen, GRAY, rect)
            elif grid[y][x] == 2:  # Block
                pygame.draw.rect(screen, BROWN, rect)

def draw_ui(player):
    # Draw score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {player.score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Draw lives
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))

def main():
    # This function is no longer used, replaced by game_loop
    pass
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.place_bomb(bombs)
                    if has_sound:
                        sound_bomb.play()
                # Set key_pressed to True when arrow key is pressed
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    key_pressed = True
            elif event.type == pygame.KEYUP:
                # Reset key_pressed when arrow key is released
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    key_pressed = False
                    move_cooldown = 0
        
        # Handle player movement if alive and not respawning
        if player.alive and respawn_timer <= 0:
            # Decrease move cooldown
            if move_cooldown > 0:
                move_cooldown -= 1
            
            # Only move if cooldown is 0 and key is pressed
            if move_cooldown == 0 and key_pressed:
                keys = pygame.key.get_pressed()
                moved = False
                
                if keys[pygame.K_UP]:
                    player.move(0, -player.speed, grid)
                    moved = True
                elif keys[pygame.K_DOWN]:
                    player.move(0, player.speed, grid)
                    moved = True
                elif keys[pygame.K_LEFT]:
                    player.move(-player.speed, 0, grid)
                    moved = True
                elif keys[pygame.K_RIGHT]:
                    player.move(player.speed, 0, grid)
                    moved = True
                
                # Set cooldown after movement
                if moved:
                    move_cooldown = 10  # Adjust this value to control movement speed
            
            # Update player animation
            player.update()
        elif respawn_timer > 0:
            respawn_timer -= 1
            if respawn_timer <= 0:
                # Reset player position
                player.x = 1
                player.y = 1
        
        # Update bombs
        for bomb in bombs[:]:
            if bomb.update():
                bombs.remove(bomb)
                explosions.append(Explosion(bomb.x, bomb.y, bomb.explosion_range, grid))
                player.bombs += 1  # Return the bomb to the player
        
        # Update explosions
        for explosion in explosions[:]:
            if explosion.update():
                explosions.remove(explosion)
            
            # Check if player is hit by explosion
            if player.alive and respawn_timer <= 0:
                for x, y in explosion.tiles:
                    if player.x == x and player.y == y:
                        if has_sound:
                            sound_player_die.play()
                        if not player.lose_life():
                            # Game over
                            if has_sound:
                                sound_game_over.play()
                        else:
                            # Start respawn timer
                            respawn_timer = 60  # 2 seconds at 30 FPS
        
        # Update enemies
        for enemy in enemies[:]:
            if enemy.alive:
                enemy.update(grid, explosions)
                
                # Check if player collides with enemy
                if player.alive and respawn_timer <= 0 and player.x == enemy.x and player.y == enemy.y:
                    if has_sound:
                        sound_player_die.play()
                    if not player.lose_life():
                        # Game over
                        if has_sound:
                            sound_game_over.play()
                    else:
                        # Start respawn timer
                        respawn_timer = 60  # 2 seconds at 30 FPS
            else:
                # Enemy killed, add score
                player.score += 100
                if has_sound:
                    sound_enemy_die.play()
                enemies.remove(enemy)
        
        # Check win condition
        if not enemies and player.alive:
            if not win_bonus_added:
                # Add bonus for completing the level (only once)
                if player.lives > 0:
                    player.score += player.lives * 200
                win_bonus_added = True
            win = True
        else:
            win = False
        
        # Draw everything
        screen.fill(BLACK)
        draw_grid(grid)
        
        for bomb in bombs:
            bomb.draw()
        
        for explosion in explosions:
            explosion.draw()
        
        for enemy in enemies:
            enemy.draw()
        
        # Draw UI (score and lives)
        draw_ui(player)
        
        if player.alive:
            # Don't draw player during respawn blink
            if respawn_timer <= 0 or respawn_timer % 10 >= 5:
                player.draw()
            
            # Display win message if all enemies are defeated
            if win:
                if not level_complete:
                    level_complete = True
                    level_complete_timer = 90  # 3 seconds at 30 FPS
                
                font = pygame.font.SysFont(None, 72)
                text = font.render(f"Level {level} Complete!", True, GREEN)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                                  SCREEN_HEIGHT // 2 - text.get_height() // 2))
                
                # Show next level message
                next_font = pygame.font.SysFont(None, 36)
                next_text = next_font.render(f"Next Level in {level_complete_timer//30 + 1}...", True, WHITE)
                screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, 
                                      SCREEN_HEIGHT // 2 + 50))
                
                # Play win sound once
                if has_sound and not pygame.mixer.get_busy():
                    sound_win.play()
                    
                # Countdown to next level
                level_complete_timer -= 1
                if level_complete_timer <= 0:
                    # Save current score and lives
                    score = player.score
                    lives = player.lives
                    level += 1
                    running = False  # End current level loop
        else:
            font = pygame.font.SysFont(None, 72)
            text = font.render("Game Over", True, RED)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                              SCREEN_HEIGHT // 2 - text.get_height() // 2))
            
            # Display final score
            score_font = pygame.font.SysFont(None, 48)
            score_text = score_font.render(f"Final Score: {player.score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                                    SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
        clock.tick(30)  # 30 FPS

def game_loop():
    level = 1
    score = 0
    lives = 3
    
    while True:
        grid = create_grid()
        player = Player(1, 1)
        player.score = score  # Carry over score from previous level
        player.lives = lives  # Carry over lives from previous level
        enemies = spawn_enemies(grid, min(3 + level - 1, 10))  # More enemies each level, max 10
        bombs = []
        explosions = []
        
        running = True
        respawn_timer = 0
        win_bonus_added = False  # Flag to track if win bonus has been added
        level_complete = False
        level_complete_timer = 0
        
        # Movement control variables
        move_cooldown = 0
        key_pressed = False
        
        # Display level start message
        screen.fill(BLACK)
        font = pygame.font.SysFont(None, 72)
        level_text = font.render(f"Level {level}", True, GREEN)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 
                              SCREEN_HEIGHT // 2 - level_text.get_height() // 2))
        
        # Display enemy count
        enemy_font = pygame.font.SysFont(None, 36)
        enemy_text = enemy_font.render(f"Enemies: {len(enemies)}", True, WHITE)
        screen.blit(enemy_text, (SCREEN_WIDTH // 2 - enemy_text.get_width() // 2, 
                               SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
        pygame.time.delay(2000)  # 2 second delay before level starts
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.place_bomb(bombs)
                        if has_sound:
                            sound_bomb.play()
                    # Set key_pressed to True when arrow key is pressed
                    elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                        key_pressed = True
                elif event.type == pygame.KEYUP:
                    # Reset key_pressed when arrow key is released
                    if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                        key_pressed = False
                        move_cooldown = 0
            
            # Handle player movement if alive and not respawning
            if player.alive and respawn_timer <= 0:
                # Decrease move cooldown
                if move_cooldown > 0:
                    move_cooldown -= 1
                
                # Only move if cooldown is 0 and key is pressed
                if move_cooldown == 0 and key_pressed:
                    keys = pygame.key.get_pressed()
                    moved = False
                    
                    if keys[pygame.K_UP]:
                        player.move(0, -player.speed, grid)
                        moved = True
                    elif keys[pygame.K_DOWN]:
                        player.move(0, player.speed, grid)
                        moved = True
                    elif keys[pygame.K_LEFT]:
                        player.move(-player.speed, 0, grid)
                        moved = True
                    elif keys[pygame.K_RIGHT]:
                        player.move(player.speed, 0, grid)
                        moved = True
                    
                    # Set cooldown after movement
                    if moved:
                        move_cooldown = 10  # Adjust this value to control movement speed
                
                # Update player animation
                player.update()
            elif respawn_timer > 0:
                respawn_timer -= 1
                if respawn_timer <= 0:
                    # Reset player position
                    player.x = 1
                    player.y = 1
            
            # Update bombs
            for bomb in bombs[:]:
                if bomb.update():
                    bombs.remove(bomb)
                    explosions.append(Explosion(bomb.x, bomb.y, bomb.explosion_range, grid))
                    player.bombs += 1  # Return the bomb to the player
            
            # Update explosions
            for explosion in explosions[:]:
                if explosion.update():
                    explosions.remove(explosion)
                
                # Check if player is hit by explosion
                if player.alive and respawn_timer <= 0:
                    for x, y in explosion.tiles:
                        if player.x == x and player.y == y:
                            if has_sound:
                                sound_player_die.play()
                            if not player.lose_life():
                                # Game over
                                if has_sound:
                                    sound_game_over.play()
                            else:
                                # Start respawn timer
                                respawn_timer = 60  # 2 seconds at 30 FPS
            
            # Update enemies
            for enemy in enemies[:]:
                if enemy.alive:
                    enemy.update(grid, explosions)
                    
                    # Check if player collides with enemy
                    if player.alive and respawn_timer <= 0 and player.x == enemy.x and player.y == enemy.y:
                        if has_sound:
                            sound_player_die.play()
                        if not player.lose_life():
                            # Game over
                            if has_sound:
                                sound_game_over.play()
                        else:
                            # Start respawn timer
                            respawn_timer = 60  # 2 seconds at 30 FPS
                else:
                    # Enemy killed, add score
                    player.score += 100
                    if has_sound:
                        sound_enemy_die.play()
                    enemies.remove(enemy)
            
            # Check win condition
            if not enemies and player.alive:
                if not win_bonus_added:
                    # Add bonus for completing the level (only once)
                    if player.lives > 0:
                        player.score += player.lives * 200
                    win_bonus_added = True
                win = True
            else:
                win = False
            
            # Draw everything
            screen.fill(BLACK)
            draw_grid(grid)
            
            for bomb in bombs:
                bomb.draw()
            
            for explosion in explosions:
                explosion.draw()
            
            for enemy in enemies:
                enemy.draw()
            
            # Draw UI (score and lives)
            draw_ui(player)
            
            if player.alive:
                # Don't draw player during respawn blink
                if respawn_timer <= 0 or respawn_timer % 10 >= 5:
                    player.draw()
                
                # Display win message if all enemies are defeated
                if win:
                    if not level_complete:
                        level_complete = True
                        level_complete_timer = 90  # 3 seconds at 30 FPS
                    
                    font = pygame.font.SysFont(None, 72)
                    text = font.render(f"Level {level} Complete!", True, GREEN)
                    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                                      SCREEN_HEIGHT // 2 - text.get_height() // 2))
                    
                    # Show next level message
                    next_font = pygame.font.SysFont(None, 36)
                    next_text = next_font.render(f"Next Level in {level_complete_timer//30 + 1}...", True, WHITE)
                    screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, 
                                          SCREEN_HEIGHT // 2 + 50))
                    
                    # Play win sound once
                    if has_sound and not pygame.mixer.get_busy():
                        sound_win.play()
                        
                    # Countdown to next level
                    level_complete_timer -= 1
                    if level_complete_timer <= 0:
                        # Save current score and lives
                        score = player.score
                        lives = player.lives
                        level += 1
                        running = False  # End current level loop
            else:
                font = pygame.font.SysFont(None, 72)
                text = font.render("Game Over", True, RED)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                                  SCREEN_HEIGHT // 2 - text.get_height() // 2))
                
                # Display final score
                score_font = pygame.font.SysFont(None, 48)
                score_text = score_font.render(f"Final Score: {player.score}", True, WHITE)
                screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                                        SCREEN_HEIGHT // 2 + 50))
                
                # Display restart message
                restart_font = pygame.font.SysFont(None, 36)
                restart_text = restart_font.render("Press any key to restart", True, WHITE)
                screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                         SCREEN_HEIGHT // 2 + 100))
                
                pygame.display.flip()
                
                # Wait for key press to restart
                waiting_for_key = True
                while waiting_for_key:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            waiting_for_key = False
                            level = 1
                            score = 0
                            lives = 3
                            running = False
            
            pygame.display.flip()
            clock.tick(30)  # 30 FPS

if __name__ == "__main__":
    game_loop()
    pygame.quit()
    sys.exit()