"""
Resource Management System
Handles resource spawning, collection, and tracking
"""
from typing import List, Tuple
import pygame
import random
from config.game_config import *
from src.utils.helpers import distance, is_in_range


class Resource:
    """Represents a collectible resource on the map"""
    
    def __init__(self, x: float, y: float, resource_id: str):
        """
        Initialize a resource
        
        Args:
            x: X coordinate
            y: Y coordinate
            resource_id: Unique identifier for the resource
        """
        self.x = x
        self.y = y
        self.id = resource_id
        self.collected = False
        self.collection_time = 0
    
    def get_position(self) -> Tuple[float, float]:
        """Get resource position"""
        return (self.x, self.y)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the resource"""
        pygame.draw.circle(surface, COLOR_YELLOW, (int(self.x), int(self.y)), RESOURCE_SIZE)
        pygame.draw.circle(surface, COLOR_ORANGE, (int(self.x), int(self.y)), RESOURCE_SIZE, 2)
    
    def __repr__(self):
        return f"Resource({self.id}, {self.x}, {self.y})"


class ResourceManager:
    """Manages all resources in the game"""
    
    def __init__(self):
        """Initialize resource manager"""
        self.resources: List[Resource] = []
        self.resource_counter = 0
        self.base_resources = RESOURCES_INITIAL_COUNT
        self.resources_collected = 0
        self.spawn_timer = 0
    
    def initialize_resources(self, map_obj) -> None:
        """
        Initialize resources at the start of the game
        
        Args:
            map_obj: GameMap object for collision checking
        """
        for i in range(RESOURCES_INITIAL_COUNT):
            self._spawn_resource(map_obj)
    
    def _spawn_resource(self, map_obj) -> None:
        """
        Spawn a single resource at a random location
        
        Args:
            map_obj: GameMap object for collision checking
        """
        # Try to spawn in a free area
        for _ in range(10):  # Try up to 10 times
            x = random.randint(50, WINDOW_WIDTH - 50)
            y = random.randint(50, WINDOW_HEIGHT - 50)
            
            if not map_obj.is_blocked(x, y, RESOURCE_SIZE):
                resource = Resource(x, y, f"resource_{self.resource_counter}")
                self.resources.append(resource)
                self.resource_counter += 1
                return
    
    def update(self, map_obj) -> None:
        """
        Update resources and spawn new ones
        
        Args:
            map_obj: GameMap object for collision checking
        """
        # Attempt to spawn new resources
        self.spawn_timer += 1
        
        if (self.spawn_timer > 60 and  # Every 1 second at 60 FPS
            len(self.resources) < RESOURCES_MAX_ON_MAP and
            random.random() < RESOURCES_SPAWN_RATE):
            self._spawn_resource(map_obj)
            self.spawn_timer = 0
    
    def get_resource_at(self, x: float, y: float, radius: float = 20) -> 'Resource':
        """
        Get a resource near the given position
        
        Args:
            x: X coordinate
            y: Y coordinate
            radius: Search radius
            
        Returns:
            Resource if found, None otherwise
        """
        for resource in self.resources:
            if not resource.collected and distance((x, y), resource.get_position()) < radius:
                return resource
        return None
    
    def collect_resource(self, resource: Resource) -> bool:
        """
        Collect a resource
        
        Args:
            resource: Resource to collect
            
        Returns:
            True if successfully collected
        """
        if resource in self.resources and not resource.collected:
            resource.collected = True
            self.resources.remove(resource)
            self.resources_collected += 1
            return True
        return False
    
    def get_uncollected_resources(self) -> List[Resource]:
        """Get list of uncollected resources"""
        return [r for r in self.resources if not r.collected]
    
    def get_resource_count(self) -> int:
        """Get total uncollected resource count"""
        return len(self.get_uncollected_resources())
    
    def get_resources_in_area(self, x: float, y: float, radius: float) -> List[Resource]:
        """
        Get all resources in an area
        
        Args:
            x: Center X coordinate
            y: Center Y coordinate
            radius: Search radius
            
        Returns:
            List of resources in area
        """
        return [r for r in self.get_uncollected_resources()
                if distance((x, y), r.get_position()) < radius]
    
    def get_nearest_resource(self, x: float, y: float) -> 'Resource':
        """
        Get the nearest resource
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Nearest resource or None
        """
        uncollected = self.get_uncollected_resources()
        if not uncollected:
            return None
        
        return min(uncollected, key=lambda r: distance((x, y), r.get_position()))
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all resources"""
        for resource in self.resources:
            if not resource.collected:
                resource.draw(surface)
    
    def reset(self) -> None:
        """Reset resource manager"""
        self.resources.clear()
        self.resource_counter = 0
        self.resources_collected = 0
        self.spawn_timer = 0
