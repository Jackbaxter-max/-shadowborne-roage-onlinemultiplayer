import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 200)
GREEN = (0, 150, 0)
RED = (200, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)
PURPLE = (100, 0, 100)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.speed = 3
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update(self, keys, room_walls):
        old_x, old_y = self.x, self.y
        
        # Movement with WASD and arrow keys
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
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
    
    def draw(self, screen):
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x + 2, self.y + 2, self.width - 4, self.height - 4))

class GameObject:
    def __init__(self, x, y, width, height, color, name, description=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.name = name
        self.description = description
        self.visible = True
        self.interactive = True
        
    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)
            
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) and self.visible and self.interactive

class Key(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 12, YELLOW, "Key", "A golden key. Wonder what it opens?")
        
    def draw(self, screen):
        if self.visible:
            # Draw key shape
            pygame.draw.rect(screen, self.color, self.rect)
            # Draw key teeth
            teeth_rect = pygame.Rect(self.rect.x + 14, self.rect.y + 3, 5, 6)
            pygame.draw.rect(screen, self.color, teeth_rect)

class Chest(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 30, BROWN, "Chest", "A treasure chest.")
        self.opened = False
        
    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)
            if not self.opened:
                # Draw closed lid
                lid_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 12)
                pygame.draw.rect(screen, (100, 50, 0), lid_rect)
            else:
                # Draw open lid (tilted)
                points = [
                    (self.rect.x, self.rect.y),
                    (self.rect.x + self.rect.width, self.rect.y - 15),
                    (self.rect.x + self.rect.width, self.rect.y - 3),
                    (self.rect.x, self.rect.y + 12)
                ]
                pygame.draw.polygon(screen, (100, 50, 0), points)

class LockedDoor(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, BROWN, "Locked Door", "A wooden door. It looks locked.")
        self.locked = True
        
    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)
            # Draw door handle
            handle_x = self.rect.x + self.rect.width - 12
            handle_y = self.rect.y + self.rect.height // 2
            pygame.draw.circle(screen, YELLOW, (handle_x, handle_y), 3)

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

class Room:
    def __init__(self, room_id, bg_color=DARK_GREEN):
        self.room_id = room_id
        self.walls = []
        self.doors = []
        self.objects = []  # Point-and-click objects
        self.collectibles = []  # Moving collectibles
        self.bg_color = bg_color
        
    def add_door(self, x, y, width, height, leads_to_room, spawn_x, spawn_y):
        door = Door(x, y, width, height, leads_to_room, spawn_x, spawn_y)
        self.doors.append(door)
        return door
    
    def add_wall(self, x, y, width, height):
        wall = Wall(x, y, width, height)
        self.walls.append(wall)
        return wall
    
    def add_object(self, obj):
        self.objects.append(obj)
        return obj
    
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
            
            # Check if position is valid (not on walls, doors, or objects)
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
                for obj in self.objects:
                    if temp_rect.colliderect(obj.rect):
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
        
        # Draw doors
        for door in self.doors:
            door.draw(screen)
        
        # Draw point-and-click objects
        for obj in self.objects:
            obj.draw(screen)
        
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(screen)

class HybridGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hybrid Point & Click + Top-Down Adventure")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Game state
        self.player = Player(100, 100)
        self.rooms = {}
        self.current_room_id = 0
        self.inventory = []
        self.score = 0
        self.message = "Use WASD/Arrows to move, click objects to interact!"
        self.message_timer = 300
        
        # Create rooms
        self.create_rooms()
        self.current_room = self.rooms[0]
        
    def create_rooms(self):
        wall_thickness = 20
        
        # Room 0 - Starting room with point-and-click elements
        room0 = Room(0, DARK_GREEN)
        # Create borders with door gaps
        room0.add_wall(0, 0, SCREEN_WIDTH, wall_thickness)
        room0.add_wall(0, SCREEN_HEIGHT - wall_thickness, 350, wall_thickness)
        room0.add_wall(450, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH - 450, wall_thickness)
        room0.add_wall(0, 0, wall_thickness, SCREEN_HEIGHT)
        room0.add_wall(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, 280)
        room0.add_wall(SCREEN_WIDTH - wall_thickness, 340, wall_thickness, SCREEN_HEIGHT - 340)
        
        # Add interior walls
        room0.add_wall(200, 150, 60, 60)
        room0.add_wall(500, 100, 40, 80)
        
        # Add point-and-click objects
        room0.add_object(Key(150, 300))
        room0.add_object(Chest(600, 250))
        room0.add_object(LockedDoor(350, 180, 60, 80))
        
        # Add doors to other rooms
        room0.add_door(SCREEN_WIDTH - wall_thickness, 280, wall_thickness, 60, 1, 30, 300)
        room0.add_door(350, SCREEN_HEIGHT - wall_thickness, 100, wall_thickness, 2, 400, 50)
        
        room0.spawn_random_collectibles(3)
        self.rooms[0] = room0
        
        # Room 1 - Puzzle room
        room1 = Room(1, PURPLE)
        room1.add_wall(0, 0, 300, wall_thickness)
        room1.add_wall(380, 0, SCREEN_WIDTH - 380, wall_thickness)
        room1.add_wall(0, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH, wall_thickness)
        room1.add_wall(0, 0, wall_thickness, 280)
        room1.add_wall(0, 340, wall_thickness, SCREEN_HEIGHT - 340)
        room1.add_wall(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT)
        
        # Add maze-like walls
        room1.add_wall(100, 200, 150, 20)
        room1.add_wall(400, 120, 20, 150)
        room1.add_wall(150, 80, 80, 40)
        
        # Add objects
        room1.add_object(Key(500, 400))
        room1.add_object(Chest(100, 100))
        
        room1.add_door(0, 280, wall_thickness, 60, 0, SCREEN_WIDTH - 50, 300)
        room1.add_door(300, 0, 80, wall_thickness, 3, 350, SCREEN_HEIGHT - 50)
        room1.spawn_random_collectibles(4)
        self.rooms[1] = room1
        
        # Room 2 - Collection room
        room2 = Room(2, (0, 100, 100))
        room2.add_wall(0, 0, 350, wall_thickness)
        room2.add_wall(450, 0, SCREEN_WIDTH - 450, wall_thickness)
        room2.add_wall(0, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH, wall_thickness)
        room2.add_wall(0, 0, wall_thickness, SCREEN_HEIGHT)
        room2.add_wall(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT)
        
        room2.add_wall(200, 200, 120, 20)
        room2.add_wall(400, 300, 60, 80)
        
        room2.add_object(Chest(150, 350))
        room2.add_object(Key(650, 150))
        
        room2.add_door(350, 0, 100, wall_thickness, 0, 400, SCREEN_HEIGHT - 50)
        room2.spawn_random_collectibles(6)
        self.rooms[2] = room2
        
        # Room 3 - Final room
        room3 = Room(3, (100, 100, 0))
        room3.add_wall(0, 0, SCREEN_WIDTH, wall_thickness)
        room3.add_wall(0, SCREEN_HEIGHT - wall_thickness, 300, wall_thickness)
        room3.add_wall(380, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH - 380, wall_thickness)
        room3.add_wall(0, 0, wall_thickness, SCREEN_HEIGHT)
        room3.add_wall(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT)
        
        room3.add_wall(150, 150, 200, 20)
        room3.add_wall(450, 200, 20, 100)
        
        room3.add_object(Chest(400, 300))
        room3.add_object(LockedDoor(200, 250, 50, 70))
        
        room3.add_door(300, SCREEN_HEIGHT - wall_thickness, 80, wall_thickness, 1, 350, 50)
        room3.spawn_random_collectibles(5)
        self.rooms[3] = room3
        
    def handle_click(self, pos):
        current_room = self.rooms[self.current_room_id]
        
        # Check inventory clicks first
        inv_y = SCREEN_HEIGHT - 60
        for i, item in enumerate(self.inventory):
            inv_x = 10 + i * 40
            inv_rect = pygame.Rect(inv_x, inv_y, 35, 35)
            if inv_rect.collidepoint(pos):
                self.use_item(item)
                return
        
        # Check object clicks
        for obj in current_room.objects:
            if obj.is_clicked(pos):
                self.interact_with_object(obj)
                break
                
    def interact_with_object(self, obj):
        if isinstance(obj, Key) and obj.visible:
            self.inventory.append("key")
            obj.visible = False
            self.show_message("You picked up a key!")
            
        elif isinstance(obj, LockedDoor):
            if obj.locked:
                self.show_message("The door is locked. You need a key!")
            else:
                self.show_message("The door is now unlocked!")
                
        elif isinstance(obj, Chest):
            if not obj.opened:
                obj.opened = True
                self.score += 50
                self.show_message("You opened the chest! +50 points!")
            else:
                self.show_message("The chest is already open.")
                
    def use_item(self, item):
        current_room = self.rooms[self.current_room_id]
        
        if item == "key":
            # Find nearby locked doors
            for obj in current_room.objects:
                if isinstance(obj, LockedDoor) and obj.locked:
                    # Check if player is close to the door
                    player_center = (self.player.x + self.player.width//2, self.player.y + self.player.height//2)
                    door_center = (obj.rect.centerx, obj.rect.centery)
                    distance = ((player_center[0] - door_center[0])**2 + (player_center[1] - door_center[1])**2)**0.5
                    
                    if distance < 80:
                        obj.locked = False
                        obj.description = "An unlocked door."
                        self.inventory.remove("key")
                        self.show_message("You unlocked the door!")
                        return
            
            self.show_message("No locked doors nearby to use the key on!")
        else:
            self.show_message(f"You can't use the {item} here.")
            
    def show_message(self, text):
        self.message = text
        self.message_timer = 180
        
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
                
                self.show_message(f"Entered Room {self.current_room_id}")
                break
    
    def handle_collectibles(self):
        current_room = self.rooms[self.current_room_id]
        player_rect = self.player.rect
        
        for collectible in current_room.collectibles[:]:
            if player_rect.colliderect(collectible.rect):
                current_room.collectibles.remove(collectible)
                self.score += 10
                self.show_message("Collected gem! +10 points")
        
    def draw_inventory(self):
        # Draw inventory background
        inv_rect = pygame.Rect(5, SCREEN_HEIGHT - 65, 200, 60)
        pygame.draw.rect(self.screen, GRAY, inv_rect)
        pygame.draw.rect(self.screen, BLACK, inv_rect, 2)
        
        # Draw inventory label
        inv_text = self.small_font.render("Inventory:", True, BLACK)
        self.screen.blit(inv_text, (10, SCREEN_HEIGHT - 62))
        
        # Draw inventory items
        for i, item in enumerate(self.inventory):
            inv_x = 10 + i * 40
            inv_y = SCREEN_HEIGHT - 45
            item_rect = pygame.Rect(inv_x, inv_y, 35, 35)
            pygame.draw.rect(self.screen, WHITE, item_rect)
            pygame.draw.rect(self.screen, BLACK, item_rect, 1)
            
            if item == "key":
                # Draw mini key
                key_rect = pygame.Rect(inv_x + 8, inv_y + 15, 12, 6)
                pygame.draw.rect(self.screen, YELLOW, key_rect)
                teeth_rect = pygame.Rect(inv_x + 18, inv_y + 17, 3, 2)
                pygame.draw.rect(self.screen, YELLOW, teeth_rect)
                
    def draw_ui(self):
        # Draw message
        if self.message_timer > 0:
            msg_surface = self.font.render(self.message, True, WHITE)
            msg_rect = msg_surface.get_rect()
            msg_rect.centerx = SCREEN_WIDTH // 2
            msg_rect.y = 10
            
            # Draw message background
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
            self.screen.blit(msg_surface, msg_rect)
            
            self.message_timer -= 1
            
        # Draw score and room info
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 120, 10))
        
        room_text = self.small_font.render(f"Room {self.current_room_id}", True, WHITE)
        self.screen.blit(room_text, (SCREEN_WIDTH - 80, 35))
        
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            # Get pressed keys for movement
            keys = pygame.key.get_pressed()
            
            # Update player
            current_room = self.rooms[self.current_room_id]
            self.player.update(keys, current_room.walls)
            
            # Check for room transitions
            self.check_door_transitions()
            
            # Handle collectibles
            self.handle_collectibles()
            
            # Draw everything
            current_room.draw(self.screen)
            self.player.draw(self.screen)
            self.draw_inventory()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = HybridGame()
    game.run()