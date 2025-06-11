import pygame
import sys
import random
import os

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
    
    def move(self, dx, dy, grid):
        new_x = self.x + dx
        new_y = self.y + dy
        
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
    
    def draw(self):
        pygame.draw.rect(screen, BLUE, 
                        (self.x * GRID_SIZE + 5, self.y * GRID_SIZE + 5, 
                         GRID_SIZE - 10, GRID_SIZE - 10))

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
            
            if self.timer <= 0:
                self.exploded = True
                if has_sound:
                    sound_explosion.play()
                return True
        return False
    
    def draw(self):
        if not self.exploded:
            # Draw bomb body
            pygame.draw.circle(screen, BLACK, 
                             (self.x * GRID_SIZE + GRID_SIZE // 2, 
                              self.y * GRID_SIZE + GRID_SIZE // 2), 
                             GRID_SIZE // 3)
            
            # Draw bomb fuse
            pygame.draw.line(screen, BROWN,
                           (self.x * GRID_SIZE + GRID_SIZE // 2, 
                            self.y * GRID_SIZE + GRID_SIZE // 3),
                           (self.x * GRID_SIZE + GRID_SIZE // 2 + 5, 
                            self.y * GRID_SIZE + GRID_SIZE // 4),
                           3)
            
            # Draw bomb highlight (pulsing)
            pygame.draw.circle(screen, WHITE, 
                             (self.x * GRID_SIZE + GRID_SIZE // 2 - 5, 
                              self.y * GRID_SIZE + GRID_SIZE // 2 - 5), 
                             3 + self.pulse_size)

class Explosion:
    def __init__(self, x, y, range_val, grid):
        self.x = x
        self.y = y
        self.range = range_val
        self.timer = 30  # 1 second at 30 FPS
        self.tiles = self.calculate_tiles(grid)
    
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
        return self.timer <= 0
    
    def draw(self):
        for x, y in self.tiles:
            pygame.draw.rect(screen, RED, 
                           (x * GRID_SIZE, y * GRID_SIZE, 
                            GRID_SIZE, GRID_SIZE))

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
    grid = create_grid()
    player = Player(1, 1)
    enemies = spawn_enemies(grid, 3)  # Spawn 3 enemies
    bombs = []
    explosions = []
    
    running = True
    respawn_timer = 0
    
    # Movement control variables
    move_cooldown = 0
    key_pressed = False
    
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
            win = True
            # Add bonus for completing the level
            if player.lives > 0:
                player.score += player.lives * 200
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
                font = pygame.font.SysFont(None, 72)
                text = font.render("You Win!", True, GREEN)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                                  SCREEN_HEIGHT // 2 - text.get_height() // 2))
                
                # Play win sound once
                if has_sound and not pygame.mixer.get_busy():
                    sound_win.play()
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

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()