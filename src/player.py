"""
Player (Thief) Character
The player-controlled thief character
"""
import pygame
from config.game_config import *
from src.utils.helpers import clamp_position, distance


class Player:
    """Represents the player-controlled thief"""
    
    def __init__(self, x: float = 50, y: float = 50):
        """
        Initialize the player
        
        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
        """
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.vx = 0
        self.vy = 0
        
        # Inventory
        self.carrying = []
        self.carrying_capacity = PLAYER_CARRYING_CAPACITY
        
        # Stealth ability
        self.stealth_active = False
        self.stealth_timer = 0
        self.stealth_cooldown = 0
        
        # State
        self.alive = True
        self.caught = False
        self.resources_secured = 0
    
    def get_position(self) -> tuple:
        """Get player position"""
        return (self.x, self.y)
    
    def set_position(self, x: float, y: float) -> None:
        """Set player position"""
        self.x, self.y = clamp_position((x, y), WINDOW_WIDTH, WINDOW_HEIGHT)
    
    def handle_input(self, keys) -> None:
        """
        Handle keyboard input
        
        Args:
            keys: Pygame keys array from pygame.key.get_pressed()
        """
        self.vx = 0
        self.vy = 0
        
        # WASD or Arrow keys for movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vy = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vy = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = self.speed
        
        # Stealth ability (SPACE)
        if keys[pygame.K_SPACE] and not self.stealth_active and self.stealth_cooldown <= 0:
            self.activate_stealth()
    
    def update(self, obstacles=None) -> None:
        """
        Update player state
        
        Args:
            obstacles: List of obstacles for collision checking
        """
        # Move player
        new_x = self.x + self.vx
        new_y = self.y + self.vy
        
        # Check collision with obstacles
        if obstacles:
            if not any(obs.contains_circle(new_x, new_y, self.size) for obs in obstacles):
                self.set_position(new_x, new_y)
        else:
            self.set_position(new_x, new_y)
        
        # Update stealth
        if self.stealth_active:
            self.stealth_timer -= 1
            if self.stealth_timer <= 0:
                self.stealth_active = False
                self.stealth_cooldown = PLAYER_STEALTH_COOLDOWN
        
        if self.stealth_cooldown > 0:
            self.stealth_cooldown -= 1
    
    def activate_stealth(self) -> None:
        """Activate stealth ability"""
        self.stealth_active = True
        self.stealth_timer = PLAYER_STEALTH_DURATION
    
    def steal_resources(self, count: int) -> bool:
        """
        Steal resources from base
        
        Args:
            count: Number of resources to steal
            
        Returns:
            True if successfully stole resources
        """
        if len(self.carrying) < self.carrying_capacity:
            steal_amount = min(count, self.carrying_capacity - len(self.carrying))
            for _ in range(steal_amount):
                self.carrying.append({"value": RESOURCE_VALUE})
            return True
        return False
    
    def get_carrying_count(self) -> int:
        """Get number of resources being carried"""
        return len(self.carrying)
    
    def secure_resources(self, hideout) -> bool:
        """
        Secure stolen resources in hideout
        
        Args:
            hideout: ThiefHideout object
            
        Returns:
            True if resources secured
        """
        if len(self.carrying) > 0:
            count = len(self.carrying)
            hideout.secure_resources(count)
            self.resources_secured += count
            self.carrying.clear()
            return True
        return False
    
    def is_visible(self) -> bool:
        """Check if player is visible (not in stealth)"""
        return not self.stealth_active
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the player"""
        # Draw player circle
        player_color = COLOR_CYAN if not self.stealth_active else (100, 200, 255)
        pygame.draw.circle(surface, player_color, (int(self.x), int(self.y)), self.size)
        
        # Draw outline
        outline_color = COLOR_YELLOW if self.stealth_active else COLOR_WHITE
        pygame.draw.circle(surface, outline_color, (int(self.x), int(self.y)), self.size, 2)
        
        # Draw carrying indicator
        if len(self.carrying) > 0:
            pygame.draw.circle(surface, COLOR_YELLOW, (int(self.x), int(self.y) - 15), 3)
        
        # Label
        font = pygame.font.Font(None, 16)
        label = font.render("T", True, COLOR_WHITE)
        surface.blit(label, (self.x - 4, self.y - 4))
        
        # Stealth indicator
        if self.stealth_active:
            font_small = pygame.font.Font(None, 12)
            stealth_text = font_small.render("STEALTH", True, (100, 200, 255))
            surface.blit(stealth_text, (self.x - 25, self.y - 25))
    
    def reset(self) -> None:
        """Reset player to initial state"""
        self.set_position(50, 50)
        self.vx = 0
        self.vy = 0
        self.carrying.clear()
        self.stealth_active = False
        self.stealth_timer = 0
        self.stealth_cooldown = 0
        self.alive = True
        self.caught = False
        self.resources_secured = 0
