"""
Mesa Framework Model for Operation Guardian Game
Wraps the game engine with Mesa's Model and Scheduler

To use this module, first install Mesa:
    pip install mesa
"""
from typing import Dict, List, Optional

try:
    from mesa import Model
    from mesa.time import RandomActivationScheduler
    MESA_AVAILABLE = True
except ImportError:
    MESA_AVAILABLE = False
    # Provide fallback if Mesa not installed yet
    class Model:
        def __init__(self):
            pass
    
    class RandomActivationScheduler:
        def __init__(self, model):
            self.model = model
            self.agents = []
        
        def add(self, agent):
            self.agents.append(agent)
        
        def step(self):
            for agent in self.agents:
                if hasattr(agent, 'step'):
                    agent.step()

from config.game_config import *


class OperationGuardianModel(Model):
    """
    Mesa Model for Operation Guardian Game
    
    This model wraps the existing game engine and provides Mesa scheduling
    for agent-based modeling framework integration.
    """
    
    def __init__(self, difficulty: str = "easy"):
        """
        Initialize the Mesa model
        
        Args:
            difficulty: Game difficulty level ("easy", "medium", "hard")
        """
        super().__init__()
        
        # Create Mesa scheduler
        self.scheduler = RandomActivationScheduler(self)
        
        # Game state
        self.difficulty = difficulty
        self.is_initialized = False
        self.game_engine = None
        self.step_count = 0
        
        # Game statistics (for data collection)
        self.resources_collected = 0
        self.resources_at_base = 0
        self.agents_active = 0
    
    def set_game_engine(self, engine) -> None:
        """
        Set reference to the game engine
        
        Args:
            engine: GameEngine instance
        """
        self.game_engine = engine
    
    def initialize_game(self) -> None:
        """Initialize game and register agents with scheduler"""
        if self.is_initialized or not self.game_engine:
            return
        
        # Register all agents with Mesa scheduler
        if self.game_engine.agents:
            for agent in self.game_engine.agents:
                # Add agent to scheduler
                self.scheduler.add(agent)
        
        self.is_initialized = True
    
    def step(self) -> None:
        """
        Execute one step of the model
        
        Mesa scheduler calls step() on all agents in order defined by scheduler
        (RandomActivationScheduler = random order each step)
        """
        if not self.is_initialized:
            return
        
        # Let Mesa scheduler step all agents
        self.scheduler.step()
        
        # Update game statistics
        self._update_statistics()
        
        self.step_count += 1
    
    def _update_statistics(self) -> None:
        """Update game statistics for analysis"""
        if not self.game_engine:
            return
        
        self.resources_collected = self.game_engine.player.resources_collected
        self.resources_at_base = self.game_engine.base_camp.get_resources()
        self.agents_active = len([a for a in self.game_engine.agents if a.active])
    
    def get_game_state(self) -> Dict:
        """
        Get current game state
        
        Returns:
            Dictionary with game state information
        """
        if not self.game_engine:
            return {}
        
        return {
            "step": self.step_count,
            "difficulty": self.difficulty,
            "game_state": self.game_engine.game_state,
            "elapsed_time": self.game_engine.elapsed_time,
            "frame_count": self.game_engine.frame_count,
            "player_resources": self.game_engine.player.resources_collected,
            "base_resources": self.game_engine.base_camp.get_resources(),
            "agents_count": len(self.game_engine.agents),
            "agents_active": self.agents_active,
        }
    
    def get_agent_states(self) -> List[Dict]:
        """
        Get states of all agents
        
        Returns:
            List of agent state dictionaries
        """
        agent_states = []
        
        if not self.game_engine:
            return agent_states
        
        for agent in self.game_engine.agents:
            state = {
                "id": agent.id,
                "role": agent.role,
                "position": agent.get_position(),
                "active": agent.active,
                "carrying": len(agent.carrying),
                "target": agent.target_position,
            }
            agent_states.append(state)
        
        return agent_states
    
    def get_resources_state(self) -> Dict:
        """
        Get resource state
        
        Returns:
            Dictionary with resource information
        """
        if not self.game_engine or not self.game_engine.resource_manager:
            return {}
        
        resources = self.game_engine.resource_manager.resources
        
        return {
            "total_resources": len(resources),
            "resources_collected": self.game_engine.resource_manager.resources_collected,
            "resources_active": len([r for r in resources if not r.collected]),
        }


def create_game_model(difficulty: str = "easy") -> OperationGuardianModel:
    """
    Factory function to create a new game model
    
    Args:
        difficulty: Game difficulty level
        
    Returns:
        Initialized Mesa model
    """
    model = OperationGuardianModel(difficulty)
    return model
