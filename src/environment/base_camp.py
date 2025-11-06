"""
Base Camp System
Manages the team's base camp where resources are stored
"""
import pygame
from config.game_config import *
from src.utils.helpers import distance, circle_overlap


class BaseCamp:
    """Represents the base camp"""
    
    def __init__(self, x: float = BASE_CAMP_X, y: float = BASE_CAMP_Y):
        """
        Initialize the base camp
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y
        self.size = BASE_CAMP_SIZE
        self.resources_stored = RESOURCES_INITIAL_COUNT
        self.resources_stolen = 0
        self.last_breach_time = None
        self.breach_count = 0
    
    def get_position(self) -> tuple:
        """Get base camp position"""
        return (self.x, self.y)
    
    def is_player_inside(self, player_x: float, player_y: float, player_size: float) -> bool:
        """
        Check if player is inside the base camp
        
        Args:
            player_x: Player X coordinate
            player_y: Player Y coordinate
            player_size: Player collision radius
            
        Returns:
            True if player is inside
        """
        return circle_overlap((self.x, self.y), self.size,
                            (player_x, player_y), player_size)
    
    def is_agent_inside(self, agent_x: float, agent_y: float, agent_size: float) -> bool:
        """
        Check if an agent is inside the base camp
        
        Args:
            agent_x: Agent X coordinate
            agent_y: Agent Y coordinate
            agent_size: Agent collision radius
            
        Returns:
            True if agent is inside
        """
        return circle_overlap((self.x, self.y), self.size,
                            (agent_x, agent_y), agent_size)
    
    def add_resources(self, count: int) -> None:
        """
        Add resources to the base
        
        Args:
            count: Number of resources to add
        """
        self.resources_stored += count
    
    def remove_resources(self, count: int) -> bool:
        """
        Remove resources from the base
        
        Args:
            count: Number of resources to remove
            
        Returns:
            True if successful, False if not enough resources
        """
        if self.resources_stored >= count:
            self.resources_stored -= count
            self.resources_stolen += count
            self.breach_count += 1
            return True
        return False
    
    def get_resources(self) -> int:
        """Get current resource count in base"""
        return self.resources_stored
    
    def get_resources_stolen(self) -> int:
        """Get total resources stolen"""
        return self.resources_stolen
    
    def get_breach_count(self) -> int:
        """Get number of thief breaches"""
        return self.breach_count
    
    def record_breach(self) -> None:
        """Record a base breach"""
        import time
        self.last_breach_time = time.time()
        self.breach_count += 1
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the base camp"""
        # Draw catching range (detection zone for attacker)
        # This shows the range within which the attacker can catch the thief
        from config.game_config import CATCHING_DISTANCE, AGENT_SIZE
        catching_range = self.size + CATCHING_DISTANCE + AGENT_SIZE + 15  # Thief size ~15
        pygame.draw.circle(surface, (255, 100, 100), (int(self.x), int(self.y)), int(catching_range), 1)
        
        # Draw base circle
        pygame.draw.circle(surface, BASE_CAMP_COLOR, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, COLOR_GREEN, (int(self.x), int(self.y)), self.size, 3)
        
        # Draw base label and resource count
        font = pygame.font.Font(None, 24)
        
        # "BASE" text
        text_base = font.render("BASE", True, COLOR_WHITE)
        surface.blit(text_base, (self.x - 20, self.y - 30))
        
        # Resource count
        text_resources = font.render(f"{self.resources_stored}", True, COLOR_WHITE)
        surface.blit(text_resources, (self.x - 10, self.y + 5))
    
    def reset(self) -> None:
        """Reset base camp"""
        self.resources_stored = RESOURCES_INITIAL_COUNT
        self.resources_stolen = 0
        self.breach_count = 0
        self.last_breach_time = None


class ThiefHideout:
    """Represents the thief's hideout"""
    
    def __init__(self, x: float = HIDEOUT_X, y: float = HIDEOUT_Y):
        """
        Initialize the thief hideout
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y
        self.size = HIDEOUT_SIZE
        self.secured_count = 0
    
    def get_position(self) -> tuple:
        """Get hideout position"""
        return (self.x, self.y)
    
    def is_player_inside(self, player_x: float, player_y: float, player_size: float) -> bool:
        """
        Check if player is inside the hideout
        
        Args:
            player_x: Player X coordinate
            player_y: Player Y coordinate
            player_size: Player collision radius
            
        Returns:
            True if player is inside
        """
        return circle_overlap((self.x, self.y), self.size,
                            (player_x, player_y), player_size)
    
    def secure_resources(self, count: int) -> None:
        """
        Secure stolen resources in hideout
        
        Args:
            count: Number of resources to secure
        """
        self.secured_count += count
    
    def get_secured_resources(self) -> int:
        """Get number of secured resources"""
        return self.secured_count
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the hideout"""
        # Draw hideout circle
        pygame.draw.circle(surface, HIDEOUT_COLOR, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, COLOR_RED, (int(self.x), int(self.y)), self.size, 3)
        
        # Draw hideout label
        font = pygame.font.Font(None, 20)
        text = font.render("HIDEOUT", True, COLOR_WHITE)
        surface.blit(text, (self.x - 30, self.y - 10))
    
    def reset(self) -> None:
        """Reset hideout"""
        self.secured_count = 0
