# Mesa Framework Migration Plan

## Overview
Migrating from a custom multi-agent system to **Python Mesa** framework for better agent-based modeling capabilities, built-in scheduling, and agent management.

## Why Mesa?

| Feature | Current | Mesa |
|---------|---------|------|
| **Agent Management** | Manual lists & loops | Built-in agent registry & iteration |
| **Scheduling** | Manual frame counting | Robust discrete event scheduler |
| **Agent Communication** | Custom Blackboard | Agents can directly interact |
| **Model Structure** | Game Engine handles everything | Separate Model & Agent classes |
| **Extensibility** | Custom implementation | Proven framework patterns |
| **Visualization** | Pygame-based UI | Mesa Server + built-in utilities |
| **Testing** | Manual | Framework supports unit testing |

## Migration Strategy: Phased Approach

### **Phase 1: Setup & Dependencies**
- [ ] Add Mesa to `requirements.txt`
- [ ] Create Mesa model wrapper around game engine
- [ ] Install and test Mesa installation
- [ ] **NO BREAKING CHANGES** - Keep Pygame UI working

### **Phase 2: Agent Base Class Migration**
- [ ] Create `MesaBaseAgent` extending Mesa's `Agent` class
- [ ] Migrate common agent properties (position, vision, speed, etc.)
- [ ] Implement Mesa's `step()` method pattern
- [ ] Wrap existing agent logic without changing behavior

### **Phase 3: Scheduler Implementation**
- [ ] Replace manual frame loop with Mesa `RandomActivationScheduler`
- [ ] Map Mesa scheduler to game engine loop
- [ ] Maintain frame-accurate behavior
- [ ] Keep Pygame rendering synchronized

### **Phase 4: Specialized Agent Migration**
- [ ] Migrate `ExplorerAgent` to Mesa model
- [ ] Migrate `CollectorAgent` to Mesa model
- [ ] Migrate `AttackerAgent` to Mesa model
- [ ] Migrate `StrategistAgent` to Mesa model
- [ ] Test each agent type individually

### **Phase 5: Environment & Resource Management**
- [ ] Create Mesa `Model` class as game container
- [ ] Integrate `ResourceManager` with Mesa agent scheduler
- [ ] Integrate `BaseCamp` and `Hideout` as agents or model resources
- [ ] Migrate `Blackboard` communication to Mesa patterns

### **Phase 6: Integration & Testing**
- [ ] Full game loop integration with Mesa scheduler
- [ ] Verify game rules and win conditions still work
- [ ] Test with all difficulty levels
- [ ] Performance testing (Mesa vs manual)

### **Phase 7: Cleanup & Documentation**
- [ ] Remove redundant agent management code
- [ ] Update documentation
- [ ] Create Mesa-specific examples

## Key Migration Changes

### Old Pattern (Current)
```python
class GameEngine:
    def __init__(self):
        self.agents = []
        
    def update(self):
        for agent in self.agents:
            agent.think()
            agent.move(self.obstacles)
```

### New Pattern (Mesa)
```python
from mesa import Model, Agent
from mesa.time import RandomActivationScheduler

class GameModel(Model):
    def __init__(self):
        self.scheduler = RandomActivationScheduler(self)
        
    def step(self):
        self.scheduler.step()  # All agents step automatically

class GameAgent(Agent):
    def __init__(self, model):
        super().__init__(model)
        model.scheduler.add(self)
        
    def step(self):
        # Agent decision + movement
        self.think()
        self.move()
```

## Current Project Statistics

- **Total Python Files**: 44
- **Agent Classes**: 5 specialized + 1 base
- **Agents per Game**: 1-12 (Easy/Medium/Hard)
- **Communication Systems**: Blackboard + direct messages
- **Rendering**: Pygame-based
- **Game States**: 6 states

## Compatibility Notes

✅ **Will Keep**:
- Pygame rendering and UI
- Game configuration system
- Resource and map systems
- Win conditions and game rules
- Communication blackboard
- Difficulty levels

⚠️ **Will Change**:
- Agent instantiation and management
- Game loop structure
- Agent scheduling
- Agent base class inheritance

🔄 **Will Simplify**:
- Agent registration process
- Manual agent list management
- Custom scheduler logic
- Agent iteration and updates

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Mesa API complexity | Low | Medium | Thorough research, incremental migration |
| Performance degradation | Low | Medium | Profile before/after, optimize if needed |
| Behavioral changes | Medium | High | Extensive testing, version control |
| Breaking existing features | Medium | High | Keep Pygame UI, test each phase |
| Learning curve | Medium | Low | Documentation, comments, examples |

## Rollback Plan

Each phase is independent. If issues arise:
1. Keep original code in comments/backup
2. Version control each phase
3. Can revert to phase N-1 if phase N fails
4. Maintain git history for comparison

## Timeline Estimate

- **Phase 1-2**: 2-3 hours (setup + base class)
- **Phase 3-4**: 3-4 hours (scheduler + agents)
- **Phase 5-6**: 2-3 hours (integration + testing)
- **Phase 7**: 1-2 hours (cleanup + docs)

**Total: 10-15 hours of development**

## Next Steps

1. ✅ Review this plan with user
2. ⏳ Install Mesa and test environment
3. ⏳ Create Mesa Model wrapper
4. ⏳ Begin agent migration (Phase 2)
5. ⏳ Integrate with existing game loop
6. ⏳ Full game testing
7. ⏳ Documentation update

---

**Decision Point**: Would you like to proceed with this migration?
- **Option A**: Start with Phase 1 (non-breaking setup)
- **Option B**: Full migration (all phases)
- **Option C**: Skip Mesa (keep current system)
