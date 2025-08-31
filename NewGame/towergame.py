import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.speed = 5
        self.color = BLUE
        self.enemies_defeated = 0
        self.attack_range = 40
        self.attack_cooldown = 0
        
    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            
        # Keep player on screen
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
    
    def update(self):
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def attack(self):
        if self.attack_cooldown == 0:
            self.attack_cooldown = 30  # 30 frames cooldown (0.5 seconds at 60 FPS)
            return True
        return False
    
    def draw(self, screen):
        # Change color when attacking
        color = RED if self.attack_cooldown > 25 else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
        # Draw a small white dot in the center to show direction
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 3)
        
        # Draw attack range when attacking
        if self.attack_cooldown > 25:
            pygame.draw.circle(screen, (255, 0, 0, 50), (int(self.x), int(self.y)), self.attack_range, 2)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)

# Remove the Collectible class entirely since we don't need it anymore

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 15
        self.speed = 2
        self.color = RED
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.alive = True
        self.death_animation = 0
        
    def update(self):
        if not self.alive:
            if self.death_animation > 0:
                self.death_animation -= 1
            return
            
        self.x += self.speed * self.direction_x
        self.y += self.speed * self.direction_y
        
        # Bounce off walls
        if self.x <= self.size or self.x >= SCREEN_WIDTH - self.size:
            self.direction_x *= -1
        if self.y <= self.size or self.y >= SCREEN_HEIGHT - self.size:
            self.direction_y *= -1
            
        # Keep enemy on screen
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
    
    def take_damage(self):
        self.alive = False
        self.death_animation = 20  # Animation frames
    
    def draw(self, screen):
        if not self.alive:
            # Death animation - shrinking red circle
            if self.death_animation > 0:
                size = self.size * (self.death_animation / 20)
                alpha = int(255 * (self.death_animation / 20))
                color = (*self.color, alpha)
                # Create a surface for alpha blending
                death_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(death_surface, color, (size, size), size)
                screen.blit(death_surface, (self.x - size, self.y - size))
            return
            
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        # Draw angry eyes
        pygame.draw.circle(screen, WHITE, (int(self.x - 5), int(self.y - 5)), 3)
        pygame.draw.circle(screen, WHITE, (int(self.x + 5), int(self.y - 5)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x - 5), int(self.y - 5)), 1)
        pygame.draw.circle(screen, BLACK, (int(self.x + 5), int(self.y - 5)), 1)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size,
                          self.size * 2, self.size * 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Top-Down Combat Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.game_over = False
        self.win = False
        
        self.spawn_enemies()
        
    def spawn_enemies(self):
        for _ in range(8):  # More enemies since they're the main objective
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            # Make sure enemies don't spawn too close to player
            while math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2) < 100:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
            self.enemies.append(Enemy(x, y))
    
    def check_collisions(self):
        player_rect = self.player.get_rect()
        
        # Check if player attacked
        if self.player.attack_cooldown > 25:  # Attack is happening
            for enemy in self.enemies:
                if enemy.alive:
                    enemy_rect = enemy.get_rect()
                    distance = math.sqrt((self.player.x - enemy.x)**2 + (self.player.y - enemy.y)**2)
                    if distance <= self.player.attack_range:
                        enemy.take_damage()
                        self.player.enemies_defeated += 1
        
        # Check enemy collisions with player (only living enemies)
        for enemy in self.enemies:
            if enemy.alive and player_rect.colliderect(enemy.get_rect()):
                self.game_over = True
                return
        
        # Check win condition - all enemies defeated
        if all(not enemy.alive for enemy in self.enemies):
            self.win = True
    
    def draw_hud(self):
        defeated_text = self.font.render(f"Enemies Defeated: {self.player.enemies_defeated}", True, WHITE)
        self.screen.blit(defeated_text, (10, 10))
        
        remaining = sum(1 for enemy in self.enemies if enemy.alive)
        remaining_text = self.small_font.render(f"Enemies left: {remaining}", True, WHITE)
        self.screen.blit(remaining_text, (10, 50))
        
        # Attack cooldown indicator
        if self.player.attack_cooldown > 0:
            cooldown_text = self.small_font.render("Attacking!", True, RED)
            self.screen.blit(cooldown_text, (10, 80))
        
        # Instructions
        instructions = [
            "Use WASD or Arrow keys to move",
            "Press SPACE to attack nearby enemies",
            "Defeat all enemies to win!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, GRAY)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 80 + i * 20))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.win:
            title = self.font.render("YOU WIN!", True, GREEN)
            message = self.font.render(f"Enemies Defeated: {self.player.enemies_defeated}", True, WHITE)
        else:
            title = self.font.render("GAME OVER", True, RED)
            message = self.font.render(f"Enemies Defeated: {self.player.enemies_defeated}", True, WHITE)
        
        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(message, message_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def restart(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.game_over = False
        self.win = False
        self.spawn_enemies()
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and (self.game_over or self.win):
                        self.restart()
                    elif event.key == pygame.K_SPACE and not self.game_over and not self.win:
                        self.player.attack()
            
            if not self.game_over and not self.win:
                # Get pressed keys for smooth movement
                keys = pygame.key.get_pressed()
                
                # Update game objects
                self.player.update()
                self.player.move(keys)
                
                for enemy in self.enemies:
                    enemy.update()
                
                self.check_collisions()
            
            # Draw everything
            self.screen.fill(DARK_GREEN)
            
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Draw player
            self.player.draw(self.screen)
            
            # Draw HUD
            self.draw_hud()
            
            # Draw game over screen if needed
            if self.game_over or self.win:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()