"""
Main Game Engine
Central game loop and management
"""
import pygame
import random
from typing import List, Dict
from config.game_config import *
from src.player import Player
from src.agents.base_agent import BaseAgent
from src.agents.explorer import ExplorerAgent
from src.agents.collector import CollectorAgent
from src.agents.attacker import AttackerAgent
from src.agents.strategist import StrategistAgent
from src.environment.map import GameMap
from src.environment.resource import ResourceManager
from src.environment.base_camp import BaseCamp, ThiefHideout
from src.communication.blackboard import get_blackboard
from src.ui.ui_manager import UIManager
from src.utils.helpers import distance, is_in_range


class GameEngine:
    """Main game engine and management"""
    
    def __init__(self):
        """Initialize the game engine"""
        pygame.init()
        
        # Display setup
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        self.game_state = GAME_STATE_RUNNING
        self.elapsed_time = 0
        self.frame_count = 0
        self.fps = 0
        
        # Game entities
        self.player: Player = None
        self.agents: List[BaseAgent] = []
        self.map: GameMap = None
        self.resource_manager: ResourceManager = None
        self.base_camp: BaseCamp = None
        self.hideout: ThiefHideout = None
        self.blackboard = get_blackboard()
        
        # UI
        self.ui_manager = UIManager()
        self.game_messages = []
        self.communication_log = []  # Track all agent communications
        
        # Initialize game
        self._initialize_game()
    
    def _initialize_game(self) -> None:
        """Initialize all game components"""
        # Create map
        self.map = GameMap(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Create resource manager
        self.resource_manager = ResourceManager()
        self.resource_manager.initialize_resources(self.map)
        
        # Create base camp and hideout
        self.base_camp = BaseCamp(BASE_CAMP_X, BASE_CAMP_Y)
        self.hideout = ThiefHideout(HIDEOUT_X, HIDEOUT_Y)
        
        # Create player (start at hideout)
        self.player = Player(HIDEOUT_X, HIDEOUT_Y)
        
        # Create agents
        self._spawn_agents()
        
        # Update blackboard with initial values
        self.blackboard.update_data({
            "resources_at_base": self.base_camp.get_resources(),
            "game_state": self.game_state,
        })
    
    def _spawn_agents(self) -> None:
        """Spawn AI agents"""
        self.agents = []
        
        # Spawn strategist (brain of the team)
        strategist = StrategistAgent("agent_strategist", BASE_CAMP_X, BASE_CAMP_Y)
        self.agents.append(strategist)
        
        # Spawn explorers
        for i in range(1):
            angle = i * (2 * 3.14159 / 2)
            import math
            x = BASE_CAMP_X + 150 * math.cos(angle)
            y = BASE_CAMP_Y + 150 * math.sin(angle)
            explorer = ExplorerAgent(f"agent_explorer_{i}", x, y)
            self.agents.append(explorer)
        
        # Spawn collectors
        for i in range(1):
            angle = (i + 1) * (2 * 3.14159 / 2)
            import math
            x = BASE_CAMP_X + 150 * math.cos(angle)
            y = BASE_CAMP_Y + 150 * math.sin(angle)
            collector = CollectorAgent(f"agent_collector_{i}", x, y, self.base_camp, self.resource_manager)
            self.agents.append(collector)
        
        # Spawn attacker (starts at base, stays there until thief detected)
        attacker = AttackerAgent("agent_attacker_0", BASE_CAMP_X, BASE_CAMP_Y)
        self.agents.append(attacker)
        
        # Register agents with strategist
        for agent in self.agents:
            if isinstance(agent, StrategistAgent):
                continue
            strategist.register_agent(agent.id, agent.role)
    
    def handle_events(self) -> bool:
        """
        Handle pygame events
        
        Returns:
            False if quit event received
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_p:
                    # Toggle pause
                    self.game_state = GAME_STATE_PAUSED if self.game_state == GAME_STATE_RUNNING else GAME_STATE_RUNNING
        
        return True
    
    def update(self) -> None:
        """Update game state"""
        if self.game_state != GAME_STATE_RUNNING:
            return
        
        self.elapsed_time += 1 / FPS
        self.frame_count += 1
        
        # Handle player input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        # Update player
        self.player.update(self.map.get_obstacles())
        
        # Update resources
        self.resource_manager.update(self.map)
        
        # Update agents
        for agent in self.agents:
            agent.update(self.map.get_obstacles())
            agent.think()
        
        # Resource discovery: Explorers scan for resources
        self._scan_resources_for_explorers()
        
        # Capture communications from blackboard
        self._capture_communications()
        
        # Check player interactions
        self._check_player_interactions()
        
        # Check win conditions
        self._check_win_conditions()
        
        # Update blackboard
        self._update_blackboard()
    
    def _scan_resources_for_explorers(self) -> None:
        """Explorers scan for resources within their vision range"""
        from src.agents.explorer import ExplorerAgent
        from config.game_config import AGENT_ROLE_EXPLORER
        
        # Find all explorer agents
        explorers = [agent for agent in self.agents if isinstance(agent, ExplorerAgent) or agent.role == AGENT_ROLE_EXPLORER]
        
        # For each explorer, scan for nearby resources
        for explorer in explorers:
            # Get all resources currently on map
            all_resources = self.resource_manager.resources
            
            # Check each resource
            for resource in all_resources:
                # Calculate distance from explorer to resource
                dx = resource.x - explorer.x
                dy = resource.y - explorer.y
                distance = (dx**2 + dy**2)**0.5
                
                # If resource is within vision range and not yet reported
                if distance <= explorer.vision_range:
                    resource_id = f"{resource.x}_{resource.y}"
                    
                    # Check if we already reported this resource
                    if not hasattr(explorer, 'reported_resources'):
                        explorer.reported_resources = set()
                    
                    if resource_id not in explorer.reported_resources:
                        # Report to strategist
                        explorer.report_resource(resource.x, resource.y)
                        explorer.reported_resources.add(resource_id)
    
    def _capture_communications(self) -> None:
        """Capture and log agent communications"""
        # Get all messages from blackboard
        all_messages = self.blackboard.message_history
        
        # Check for new messages since last capture
        for msg in all_messages[-5:]:  # Last 5 messages
            if not msg.read:
                continue
                
            # Format message for display
            sender_name = msg.sender.replace("agent_", "").upper()
            recipient_name = msg.recipient.replace("agent_", "").upper() if msg.recipient != "all" else "TEAM"
            
            if msg.message_type == "thief_sighted":
                content = msg.content
                log_msg = f"🎯 {sender_name} → {recipient_name}: THIEF SPOTTED at ({int(content.get('position', [0])[0])}, {int(content.get('position', [0])[1])})"
                
            elif msg.message_type == "resource_discovered":
                content = msg.content
                log_msg = f"📦 {sender_name} → {recipient_name}: RESOURCE FOUND at ({int(content.get('position', [0])[0])}, {int(content.get('position', [0])[1])})"
                
            elif msg.message_type == "collect_resource":
                content = msg.content
                log_msg = f"📍 {sender_name} → {recipient_name}: COLLECT from ({int(content.get('position', [0])[0])}, {int(content.get('position', [0])[1])})"
                
            elif msg.message_type == "intercept_command":
                content = msg.content
                log_msg = f"⚔️  {sender_name} → {recipient_name}: INTERCEPT THIEF at ({int(content.get('target_position', [0])[0])}, {int(content.get('target_position', [0])[1])})"
                
            elif msg.message_type == "resources_delivered":
                content = msg.content
                log_msg = f"✅ {sender_name}: DELIVERED {content.get('count', 0)} resources"
                
            else:
                log_msg = f"📨 {sender_name} → {recipient_name}: {msg.message_type}"
            
            # Add to log if not already there
            if log_msg not in self.communication_log:
                self.communication_log.append(log_msg)
                
                # Keep only last 10 messages
                if len(self.communication_log) > 10:
                    self.communication_log.pop(0)
    
    def _check_player_interactions(self) -> None:
        """Check interactions between player and environment"""
        # Check if player is in base camp
        if self.base_camp.is_player_inside(self.player.x, self.player.y, self.player.size):
            # Player can steal resources
            if len(self.player.carrying) < self.player.carrying_capacity:
                stolen = self.player.steal_resources(1)
                if stolen:
                    self.base_camp.remove_resources(1)
                    self.game_messages.append("Thief stole 1 resource!")
        
        # Check if player is in hideout
        if self.hideout.is_player_inside(self.player.x, self.player.y, self.player.size):
            self.player.secure_resources(self.hideout)
            self.game_messages.append(f"Secured {len(self.player.carrying)} resources!")
        
        # Check if agent caught the player
        for agent in self.agents:
            if isinstance(agent, AttackerAgent):
                if agent.check_thief_collision(self.player.x, self.player.y, self.player.size):
                    self.game_state = GAME_STATE_AGENTS_WIN
                    self.game_messages.append("Thief caught! Agents win!")
                    return
        
        # Check if explorers can see the player
        for agent in self.agents:
            if isinstance(agent, ExplorerAgent):
                if agent.can_see(self.player.x, self.player.y) and self.player.is_visible():
                    # Only report if not already reported recently
                    if agent.detection_cooldown <= 0:
                        agent.report_thief_sighting(self.player.x, self.player.y)
    
    def _check_win_conditions(self) -> None:
        """Check if any win condition is met"""
        # Thief wins if all resources are stolen
        if self.base_camp.get_resources() <= 0:
            self.game_state = GAME_STATE_PLAYER_WIN
            self.game_messages.append("Thief stole all resources! Thief wins!")
        
        # Thief wins if secured enough resources
        if self.hideout.get_secured_resources() >= WINNING_RESOURCES_FOR_THIEF:
            self.game_state = GAME_STATE_PLAYER_WIN
            self.game_messages.append("Thief secured all resources! Thief wins!")
    
    def _update_blackboard(self) -> None:
        """Update blackboard with current game state"""
        # Update thief position (visible to agents)
        if self.player.is_visible():
            pass  # Explorers will detect through their vision range
        
        # Update resource count
        self.blackboard.post_data("resources_at_base", self.base_camp.get_resources())
        
        # Update resource locations
        resources = self.resource_manager.get_uncollected_resources()
        resource_positions = [r.get_position() for r in resources]
        self.blackboard.post_data("resources_locations", resource_positions)
        
        # Clear old messages periodically
        if self.frame_count % 300 == 0:  # Every 5 seconds
            self.blackboard.clear_old_messages()
    
    def draw(self) -> None:
        """Render game"""
        # Clear screen
        self.screen.fill(COLOR_BLACK)
        
        # Draw map
        self.map.draw(self.screen, show_explored=SHOW_AGENT_VISION)
        
        # Draw base camp
        self.base_camp.draw(self.screen)
        
        # Draw hideout
        self.hideout.draw(self.screen)
        
        # Draw resources
        self.resource_manager.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw agents
        for agent in self.agents:
            # Skip drawing inactive attackers
            from src.agents.attacker import AttackerAgent
            if isinstance(agent, AttackerAgent) and not agent.is_active:
                continue
            agent.draw(self.screen)
        
        # Draw agent vision ranges
        self.ui_manager.draw_agent_vision_ranges(self.screen, self.agents)
        
        # Draw UI
        game_state_dict = {
            "elapsed_time": self.elapsed_time,
            "resources_at_base": self.base_camp.get_resources(),
            "resources_at_hideout": self.hideout.get_secured_resources(),
            "player_carrying": self.player.get_carrying_count(),
            "status": self.game_state,
            "fps": self.fps,
        }
        
        self.ui_manager.draw_hud(self.screen, game_state_dict)
        self.ui_manager.draw_legend(self.screen)
        self.ui_manager.draw_objective_panel(self.screen, "thief")
        self.ui_manager.draw_message_log(self.screen, self.communication_log)  # Show communications
        
        # Draw game over screen if needed
        if self.game_state == GAME_STATE_PLAYER_WIN:
            stats = {
                "elapsed_time": self.elapsed_time,
                "resources_stolen": self.player.resources_secured,
                "resources_secured": self.hideout.get_secured_resources(),
                "agent_actions": len(self.agents),
            }
            self.ui_manager.draw_game_over_screen(self.screen, "thief", stats)
        elif self.game_state == GAME_STATE_AGENTS_WIN:
            stats = {
                "elapsed_time": self.elapsed_time,
                "resources_stolen": self.player.resources_secured,
                "resources_secured": self.hideout.get_secured_resources(),
                "agent_actions": len(self.agents),
            }
            self.ui_manager.draw_game_over_screen(self.screen, "agents", stats)
        
        # Update display
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop"""
        while self.running:
            # Handle events
            self.running = self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw
            self.draw()
            
            # Frame rate control
            self.clock.tick(FPS)
            self.fps = self.clock.get_fps()
            
            # Keep message log size manageable
            if len(self.game_messages) > 10:
                self.game_messages.pop(0)
        
        pygame.quit()
