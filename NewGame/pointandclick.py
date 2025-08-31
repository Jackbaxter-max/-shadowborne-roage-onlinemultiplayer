import pygame
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
BLUE = (0, 100, 200)
GREEN = (0, 150, 0)
RED = (200, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

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

class Door(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, BROWN, "Door", "A wooden door. It looks locked.")
        self.locked = True
        
    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)
            # Draw door handle
            handle_x = self.rect.x + self.rect.width - 20
            handle_y = self.rect.y + self.rect.height // 2
            pygame.draw.circle(screen, YELLOW, (handle_x, handle_y), 5)

class Key(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 15, YELLOW, "Key", "A golden key. Wonder what it opens?")
        
    def draw(self, screen):
        if self.visible:
            # Draw key shape
            pygame.draw.rect(screen, self.color, self.rect)
            # Draw key teeth
            teeth_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 5, 8, 5)
            pygame.draw.rect(screen, self.color, teeth_rect)

class Chest(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 40, BROWN, "Chest", "A treasure chest.")
        self.opened = False
        
    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)
            if not self.opened:
                # Draw closed lid
                lid_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 15)
                pygame.draw.rect(screen, (100, 50, 0), lid_rect)
            else:
                # Draw open lid (tilted)
                points = [
                    (self.rect.x, self.rect.y),
                    (self.rect.x + self.rect.width, self.rect.y - 20),
                    (self.rect.x + self.rect.width, self.rect.y - 5),
                    (self.rect.x, self.rect.y + 15)
                ]
                pygame.draw.polygon(screen, (100, 50, 0), points)

class PointClickGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Point & Click Adventure Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Game state
        self.inventory = []
        self.message = "Click on objects to interact with them!"
        self.message_timer = 0
        
        # Create game objects
        self.objects = [
            Door(350, 200, 80, 120),
            Key(150, 400),
            Chest(600, 350)
        ]
        
        # Find specific objects for easy reference
        self.door = self.objects[0]
        self.key = self.objects[1]
        self.chest = self.objects[2]
        
    def handle_click(self, pos):
        # Check inventory clicks first
        inv_y = SCREEN_HEIGHT - 60
        for i, item in enumerate(self.inventory):
            inv_x = 10 + i * 40
            inv_rect = pygame.Rect(inv_x, inv_y, 35, 35)
            if inv_rect.collidepoint(pos):
                self.use_item(item)
                return
        
        # Check object clicks
        for obj in self.objects:
            if obj.is_clicked(pos):
                self.interact_with_object(obj)
                break
                
    def interact_with_object(self, obj):
        if obj == self.key:
            if self.key.visible:
                self.inventory.append("key")
                self.key.visible = False
                self.show_message("You picked up the key!")
                
        elif obj == self.door:
            if self.door.locked:
                self.show_message("The door is locked. You need a key!")
            else:
                self.show_message("You opened the door! Victory!")
                
        elif obj == self.chest:
            if not self.chest.opened:
                self.chest.opened = True
                self.show_message("You opened the chest! There's a shiny gem inside!")
            else:
                self.show_message("The chest is already open.")
                
    def use_item(self, item):
        if item == "key" and self.door.locked:
            self.door.locked = False
            self.door.description = "An unlocked door. Click to open!"
            self.inventory.remove("key")
            self.show_message("You unlocked the door with the key!")
        else:
            self.show_message(f"You can't use the {item} here.")
            
    def show_message(self, text):
        self.message = text
        self.message_timer = 180  # Show for 3 seconds at 60 FPS
        
    def draw_inventory(self):
        # Draw inventory background
        inv_rect = pygame.Rect(5, SCREEN_HEIGHT - 65, SCREEN_WIDTH - 10, 60)
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
                key_rect = pygame.Rect(inv_x + 8, inv_y + 15, 15, 8)
                pygame.draw.rect(self.screen, YELLOW, key_rect)
                teeth_rect = pygame.Rect(inv_x + 20, inv_y + 17, 4, 3)
                pygame.draw.rect(self.screen, YELLOW, teeth_rect)
                
    def draw_ui(self):
        # Draw message
        if self.message_timer > 0:
            msg_surface = self.font.render(self.message, True, BLACK)
            msg_rect = msg_surface.get_rect()
            msg_rect.centerx = SCREEN_WIDTH // 2
            msg_rect.y = 20
            
            # Draw message background
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, WHITE, bg_rect)
            pygame.draw.rect(self.screen, BLACK, bg_rect, 2)
            self.screen.blit(msg_surface, msg_rect)
            
            self.message_timer -= 1
            
        # Draw instructions
        instructions = [
            "Instructions:",
            "• Click objects to examine/interact",
            "• Click inventory items to use them",
            "• Find the key to unlock the door!"
        ]
        
        for i, instruction in enumerate(instructions):
            color = BLACK if i == 0 else GRAY
            font = self.font if i == 0 else self.small_font
            text = font.render(instruction, True, color)
            self.screen.blit(text, (10, 80 + i * 20))
            
    def draw_scene(self):
        # Draw background
        self.screen.fill(WHITE)
        
        # Draw simple room
        # Floor
        pygame.draw.rect(self.screen, (200, 200, 200), (0, 500, SCREEN_WIDTH, 100))
        # Walls
        pygame.draw.rect(self.screen, (220, 220, 220), (0, 0, SCREEN_WIDTH, 500))
        
        # Draw objects
        for obj in self.objects:
            obj.draw(self.screen)
            
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                        
            # Draw everything
            self.draw_scene()
            self.draw_inventory()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PointClickGame()
    game.run()