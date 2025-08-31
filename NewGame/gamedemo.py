import pygame
import random
import sys

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
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)
BROWN = (139, 69, 19)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.speed = 4
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update(self, keys, room_walls):
        old_x, old_y = self.x, self.y
        
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        # Update rect for collision detection
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Check collision with room walls
        collision = False
        for wall in room_walls:
            if self.rect.colliderect(wall.rect):
                collision = True
                break
        
        # If collision, revert to old position
        if collision:
            self.x, self.y = old_x, old_y
            self.rect.x = self.x
            self.rect.y = self.y
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        # Draw a simple face
        pygame.draw.circle(screen, WHITE, (int(self.x + 6), int(self.y + 8)), 2)
        pygame.draw.circle(screen, WHITE, (int(self.x + 19), int(self.y + 8)), 2)

class Collectible:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 12
        self.height = 12
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, RED, (self.x + 2, self.y + 2, self.width - 4, self.height - 4))

class Wall:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen):
        pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))

class Door:
    def __init__(self, x, y, width, height, leads_to_room, spawn_x, spawn_y):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.leads_to_room = leads_to_room
        self.spawn_x = spawn_x  # Where player spawns in the new room
        self.spawn_y = spawn_y
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height))

class Room:
    def __init__(self, room_id, bg_color=DARK_GREEN):
        self.room_id = room_id
        self.walls = []
        self.doors = []
        self.collectibles = []
        self.bg_color = bg_color
        
        # Create room borders
        self.create_borders()
    
    def create_borders(self):
        wall_thickness = 20
        # We'll add walls manually for each room to leave gaps for doors
    
    def add_door(self, x, y, width, height, leads_to_room, spawn_x, spawn_y):
        door = Door(x, y, width, height, leads_to_room, spawn_x, spawn_y)
        self.doors.append(door)
        return door
    
    def add_wall(self, x, y, width, height):
        wall = Wall(x, y, width, height)
        self.walls.append(wall)
        return wall
    
    def add_collectible(self, x, y):
        collectible = Collectible(x, y)
        self.collectibles.append(collectible)
        return collectible
    
    def spawn_random_collectibles(self, count):
        attempts = 0
        spawned = 0
        max_attempts = 100
        
        while spawned < count and attempts < max_attempts:
            x = random.randint(30, SCREEN_WIDTH - 50)
            y = random.randint(30, SCREEN_HEIGHT - 50)
            
            # Check if position is valid (not on walls or doors)
            temp_rect = pygame.Rect(x, y, 12, 12)
            collision = False
            
            for wall in self.walls:
                if temp_rect.colliderect(wall.rect):
                    collision = True
                    break
            
            if not collision:
                for door in self.doors:
                    if temp_rect.colliderect(door.rect):
                        collision = True
                        break
            
            if not collision:
                self.add_collectible(x, y)
                spawned += 1
            
            attempts += 1
    
    def draw(self, screen):
        # Draw background
        screen.fill(self.bg_color)
        
        # Draw walls
        for wall in self.walls:
            wall.draw(screen)
        
        # Draw doors (make them more visible)
        for door in self.doors:
            pygame.draw.rect(screen, (50, 50, 50), (door.x, door.y, door.width, door.height))
            pygame.draw.rect(screen, BLACK, (door.x + 2, door.y + 2, door.width - 4, door.height - 4))
        
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(screen)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Multi-Room Top-Down Game")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.player = Player(400, 300)
        self.rooms = {}
        self.current_room_id = 0
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        
        # Create rooms
        self.create_rooms()
        
        # Start in room 0
        self.current_room = self.rooms[0]
    
    def create_rooms(self):
        wall_thickness = 20
        
        # Room 0 - Starting room
        room0 = Room(0, DARK_GREEN)
        # Create borders with gaps for doors
        # Top wall (full)
        room0.add_wall(0, 0, SCREEN_WIDTH, wall_thickness)
        # Bottom wall (with gap for door to room 2)
        room0.add_wall(0, SCREEN_HEIGHT - wall_thickness, 350, wall_thickness)
        room0.add_wall(450, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH - 450, wall_thickness)
        # Left wall (full)
        room0.add_wall(0, 0, wall_thickness, SCREEN_HEIGHT)
        # Right wall (with gap for door to room 1)
        room0.add_wall(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, 280)
        room0.add_wall(SCREEN_WIDTH - wall_thickness, 340, wall_thickness, SCREEN_HEIGHT - 340)
        
        # Add some walls as obstacles
        room0.add_wall(200, 200, 80, 80)
        room0.add_wall(500, 100, 60, 120)
        # Door to room 1 (right side)
        room0.add_door(SCREEN_WIDTH - wall_thickness, 280, wall_thickness, 60, 1, 30, 300)
        # Door to room 2 (bottom)
        room0.add_door(350, SCREEN_HEIGHT - wall_thickness, 100, wall_thickness, 2, 400, 50)
        room0.spawn_random_collectibles(3)
        self.rooms[0] = room0
        
        # Room 1 - Right room
        room1 = Room(1, (0, 100, 0))  # Darker green
        # Create borders with gaps for doors
        # Top wall (with gap for door to room 3)
        room1.add_wall(0, 0, 300, wall_thickness)
        room1.add_wall(380, 0, SCREEN_WIDTH - 380, wall_thickness)
        # Bottom wall (full)
        room1.add_wall(0, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH, wall_thickness)
        # Left wall (with gap for door to room 0)
        room1.add_wall(0, 0, wall_thickness, 280)
        room1.add_wall(0, 340, wall_thickness, SCREEN_HEIGHT - 340)
        # Right wall (full)
        room1.add_wall(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT)
        
        room1.add_wall(100, 300, 150, 20)
        room1.add_wall(400, 150, 20, 200)
        room1.add_wall(150, 100, 100, 60)
        # Door back to room 0 (left side)
        room1.add_door(0, 280, wall_thickness, 60, 0, SCREEN_WIDTH - 50, 300)
        # Door to room 3 (top)
        room1.add_door(300, 0, 80, wall_thickness, 3, 350, SCREEN_HEIGHT - 50)
        room1.spawn_random_collectibles(4)
        self.rooms[1] = room1
        
        # Room 2 - Bottom room
        room2 = Room(2, (100, 0, 100))  # Purple-ish
        # Create borders with gaps for doors
        # Top wall (with gap for door to room 0)
        room2.add_wall(0, 0, 350, wall_thickness)
        room2.add_wall(450, 0, SCREEN_WIDTH - 450, wall_thickness)
        # Bottom wall (full)
        room2.add_wall(0, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH, wall_thickness)
        # Left wall (full)
        room2.add_wall(0, 0, wall_thickness, SCREEN_HEIGHT)
        # Right wall (full)
        room2.add_wall(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT)
        
        room2.add_wall(300, 200, 200, 20)
        room2.add_wall(100, 350, 120, 80)
        room2.add_wall(600, 300, 80, 100)
        # Door back to room 0 (top)
        room2.add_door(350, 0, 100, wall_thickness, 0, 400, SCREEN_HEIGHT - 50)
        room2.spawn_random_collectibles(5)
        self.rooms[2] = room2
        
        # Room 3 - Top room (accessible from room 1)
        room3 = Room(3, (100, 100, 0))  # Brownish
        # Create borders with gaps for doors
        # Top wall (full)
        room3.add_wall(0, 0, SCREEN_WIDTH, wall_thickness)
        # Bottom wall (with gap for door to room 1)
        room3.add_wall(0, SCREEN_HEIGHT - wall_thickness, 300, wall_thickness)
        room3.add_wall(380, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH - 380, wall_thickness)
        # Left wall (full)
        room3.add_wall(0, 0, wall_thickness, SCREEN_HEIGHT)
        # Right wall (full)
        room3.add_wall(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT)
        
        room3.add_wall(200, 200, 400, 20)
        room3.add_wall(50, 300, 100, 100)
        room3.add_wall(650, 250, 80, 150)
        # Door back to room 1 (bottom)
        room3.add_door(300, SCREEN_HEIGHT - wall_thickness, 80, wall_thickness, 1, 350, 50)
        room3.spawn_random_collectibles(6)
        self.rooms[3] = room3
    
    def check_door_transitions(self):
        player_rect = self.player.rect
        current_room = self.rooms[self.current_room_id]
        
        for door in current_room.doors:
            if player_rect.colliderect(door.rect):
                # Transition to new room
                self.current_room_id = door.leads_to_room
                self.current_room = self.rooms[self.current_room_id]
                
                # Move player to spawn position
                self.player.x = door.spawn_x
                self.player.y = door.spawn_y
                self.player.rect.x = self.player.x
                self.player.rect.y = self.player.y
                break
    
    def handle_collectibles(self):
        current_room = self.rooms[self.current_room_id]
        player_rect = self.player.rect
        
        for collectible in current_room.collectibles[:]:
            if player_rect.colliderect(collectible.rect):
                current_room.collectibles.remove(collectible)
                self.score += 10
    
    def draw(self):
        # Draw current room
        current_room = self.rooms[self.current_room_id]
        current_room.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        room_text = self.font.render(f"Room: {self.current_room_id}", True, WHITE)
        self.screen.blit(room_text, (10, 50))
        
        # Draw instructions
        instruction_text = pygame.font.Font(None, 24).render("Use WASD/Arrows to move. Walk into dark doorways to change rooms!", True, WHITE)
        self.screen.blit(instruction_text, (10, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Get pressed keys
            keys = pygame.key.get_pressed()
            
            # Update game objects
            current_room = self.rooms[self.current_room_id]
            self.player.update(keys, current_room.walls)
            
            # Check for room transitions
            self.check_door_transitions()
            
            # Handle collectibles
            self.handle_collectibles()
            
            # Draw everything
            self.draw()
            
            # Control frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()