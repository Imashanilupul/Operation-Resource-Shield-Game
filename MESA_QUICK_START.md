# Mesa Framework - Quick Start

## Installation

### Step 1: Update requirements.txt
```
pygame==2.5.2
numpy==1.24.3
mesa>=0.9.0
```

### Step 2: Install Mesa
```bash
pip install mesa
```

### Step 3: Verify Installation
```bash
python -c "import mesa; print(f'Mesa {mesa.__version__} installed successfully!')"
```

## Phase 1: Basic Setup (RECOMMENDED START)

### Create Mesa Model Wrapper

Create new file: `src/mesa_model.py`

```python
"""
Mesa Framework Model for Operation Guardian Game
"""
from mesa import Model
from mesa.time import RandomActivationScheduler
from typing import List, Dict
from config.game_config import *


class OperationGuardianModel(Model):
    """Mesa Model wrapper for the game"""
    
    def __init__(self, difficulty: str = "easy"):
        super().__init__()
        self.scheduler = RandomActivationScheduler(self)
        self.difficulty = difficulty
        self.is_initialized = False
        
        # Will be set by game engine
        self.engine = None
        self.agents_list = []
    
    def initialize_game(self) -> None:
        """Initialize game"""
        if self.is_initialized:
            return
        
        # Register all agents with scheduler
        if self.engine and self.engine.agents:
            for agent in self.engine.agents:
                self.scheduler.add(agent)
        
        self.is_initialized = True
    
    def step(self) -> None:
        """Execute one step"""
        if not self.is_initialized:
            return
        
        # Mesa scheduler calls step() on all agents
        self.scheduler.step()


def create_game_model(difficulty: str = "easy") -> OperationGuardianModel:
    """Factory function to create game model"""
    return OperationGuardianModel(difficulty)
```

### Test Installation

```python
# test_mesa.py
from src.mesa_model import create_game_model

model = create_game_model("easy")
print(f"✓ Mesa model created successfully!")
print(f"✓ Scheduler agents: {len(model.scheduler.agents)}")
```

## Phase 2: Migrate Base Agent (Optional)

### Create Mesa-Compatible Agent

Create new file: `src/agents/mesa_base_agent.py`

```python
"""Mesa-compatible base agent"""
from mesa import Agent
from abc import abstractmethod


class MesaBaseAgent(Agent):
    """Base class for Mesa agents"""
    
    def __init__(self, agent_id: str, model):
        super().__init__(model)
        self.agent_id = agent_id
        self.active = True
    
    def step(self):
        """Called each tick by Mesa scheduler"""
        if not self.active:
            return
        
        # Agent's thinking and actions
        self.think()
        self.move()
    
    @abstractmethod
    def think(self):
        """Agent decision-making"""
        pass
    
    def move(self):
        """Agent movement"""
        pass
```

## Decision Tree: What to Do Next?

```
Do you want Mesa integration?
│
├─ YES - Full migration
│  └─ Start with Phase 1 Setup (see MESA_IMPLEMENTATION_GUIDE.md)
│
├─ YES - Gradual migration
│  └─ Start with Phase 1 Setup only
│     (Keep current system, add Mesa alongside)
│
└─ NO - Keep current system
   └─ No changes needed
```

## Understanding Mesa Concepts

### Model
Think of it as your game world container:
```python
model = Model()  # Your entire game
```

### Agent
Individual entity in the simulation:
```python
class MyAgent(Agent):
    def step(self):
        # What this agent does each tick
        pass
```

### Scheduler
Manages when agents act:
```python
scheduler = RandomActivationScheduler(model)
scheduler.add(agent)       # Register agent
scheduler.step()           # All agents step (in random order)
```

### Step
One iteration of the simulation:
```python
model.scheduler.step()  # One step = all agents act once
```

## Comparison: Current vs Mesa

### Current System
```python
class GameEngine:
    def __init__(self):
        self.agents = []
    
    def update(self):
        for agent in self.agents:      # Manual loop
            agent.think()
            agent.move()
        self.frame_count += 1
        self.elapsed_time += 16  # ~60 FPS
```

### With Mesa
```python
class OperationGuardianModel(Model):
    def __init__(self):
        self.scheduler = RandomActivationScheduler(self)
    
    def step(self):
        self.scheduler.step()  # Scheduler calls all agents' step()

# Usage
model = OperationGuardianModel()
model.scheduler.add(agent)   # Agents register themselves
model.step()                 # All agents step automatically
```

## Common Questions

**Q: Will my game still work?**
A: Yes! Phase 1 is non-breaking. Existing code continues to work.

**Q: Do I need to rewrite all agents?**
A: No. Current agents work with Mesa Model as-is initially.

**Q: Can I use Mesa's visualization?**
A: Yes, optionally. Requires additional setup, but Pygame works too.

**Q: What if Mesa breaks something?**
A: Version control + phased approach means easy rollback.

**Q: Is Mesa slower than current system?**
A: Typically similar or faster. Mesa is optimized for ABM.

**Q: Can I use both Mesa and current system together?**
A: Yes, during migration phases.

## Next Steps

1. **Update requirements.txt** with `mesa>=0.9.0`
2. **Install Mesa**: `pip install mesa`
3. **Test Mesa**: `python -c "import mesa; print(mesa.__version__)"`
4. **Read one of these**:
   - `MESA_OVERVIEW.md` - High-level concepts
   - `MESA_MIGRATION_PLAN.md` - Full migration strategy
   - `MESA_IMPLEMENTATION_GUIDE.md` - Detailed implementation steps

## Support Resources

- **Mesa Documentation**: https://mesa.readthedocs.io/
- **Mesa GitHub**: https://github.com/projectmesa/mesa
- **Agent-Based Modeling Guide**: https://en.wikipedia.org/wiki/Agent-based_model
- **Your Project Docs**: See MESA_*.md files above

## Summary

| Document | Purpose | Read Time |
|----------|---------|-----------|
| `MESA_OVERVIEW.md` | What is Mesa? Why use it? | 5 min |
| `MESA_MIGRATION_PLAN.md` | How to migrate? What are risks? | 10 min |
| `MESA_IMPLEMENTATION_GUIDE.md` | Step-by-step implementation | 15 min |
| `MESA_QUICK_START.md` (this file) | Get started in 5 minutes | 5 min |

---

**Ready to start?** 

Install Mesa now:
```bash
pip install mesa
```

Then let me know which phase you want to implement!
