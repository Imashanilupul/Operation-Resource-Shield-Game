"""
Blackboard Communication System
Shared memory for multi-agent communication and coordination
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import threading


class Message:
    """Represents a message in the communication system"""
    
    def __init__(self, sender: str, recipient: str, message_type: str, content: Any, priority: int = 1):
        """
        Initialize a message
        
        Args:
            sender: ID of sending agent
            recipient: ID of receiving agent or 'all' for broadcast
            message_type: Type of message (e.g., 'alert', 'command', 'status_update')
            content: Message content
            priority: Priority level (1-10, higher = more important)
        """
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.content = content
        self.priority = priority
        self.timestamp = datetime.now()
        self.read = False
    
    def __repr__(self):
        return f"Message({self.sender} -> {self.recipient}: {self.message_type})"


class Blackboard:
    """
    Central communication and knowledge sharing system for all agents
    Uses a shared memory approach with message passing
    """
    
    def __init__(self):
        """Initialize the blackboard"""
        self.lock = threading.Lock()
        
        # Shared knowledge
        self.data = {
            "thief_position": None,
            "thief_last_seen": None,
            "resources_at_base": 0,
            "resources_collected_total": 0,
            "resources_locations": [],
            "base_status": "safe",
            "agents_status": {},
            "strategist_commands": [],
            "exploration_progress": {},
            "game_state": "running",
            "elapsed_time": 0,
        }
        
        # Message queue
        self.messages: List[Message] = []
        self.message_history: List[Message] = []
        
        # Alerts and notifications
        self.alerts = []
        
    def post_data(self, key: str, value: Any) -> None:
        """
        Post data to the blackboard
        
        Args:
            key: Data key
            value: Data value
        """
        with self.lock:
            self.data[key] = value
    
    def read_data(self, key: str) -> Optional[Any]:
        """
        Read data from the blackboard
        
        Args:
            key: Data key
            
        Returns:
            Data value or None if not found
        """
        with self.lock:
            return self.data.get(key)
    
    def update_data(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple pieces of data at once
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        with self.lock:
            self.data.update(updates)
    
    def get_all_data(self) -> Dict[str, Any]:
        """
        Get a copy of all data on the blackboard
        
        Returns:
            Copy of all data
        """
        with self.lock:
            return self.data.copy()
    
    def send_message(self, message: Message) -> None:
        """
        Send a message through the blackboard
        
        Args:
            message: Message object to send
        """
        with self.lock:
            self.messages.append(message)
            self.message_history.append(message)
    
    def get_messages(self, recipient: str, unread_only: bool = True) -> List[Message]:
        """
        Retrieve messages for a specific recipient
        
        Args:
            recipient: Agent ID to retrieve messages for
            unread_only: If True, only return unread messages
            
        Returns:
            List of messages
        """
        with self.lock:
            if unread_only:
                messages = [m for m in self.messages 
                           if (m.recipient == recipient or m.recipient == 'all') 
                           and not m.read]
            else:
                messages = [m for m in self.messages 
                           if m.recipient == recipient or m.recipient == 'all']
            
            # Mark messages as read
            for msg in messages:
                msg.read = True
            
            return messages
    
    def broadcast_message(self, sender: str, message_type: str, content: Any, priority: int = 1) -> None:
        """
        Send a message to all agents
        
        Args:
            sender: ID of sending agent
            message_type: Type of message
            content: Message content
            priority: Priority level
        """
        message = Message(sender, 'all', message_type, content, priority)
        self.send_message(message)
    
    def post_alert(self, alert_type: str, content: Any, severity: str = 'info') -> None:
        """
        Post an alert to the blackboard
        
        Args:
            alert_type: Type of alert
            content: Alert content
            severity: Severity level ('info', 'warning', 'critical')
        """
        with self.lock:
            alert = {
                'type': alert_type,
                'content': content,
                'severity': severity,
                'timestamp': datetime.now(),
            }
            self.alerts.append(alert)
    
    def get_alerts(self, clear: bool = False) -> List[Dict]:
        """
        Get current alerts
        
        Args:
            clear: If True, clear alerts after retrieval
            
        Returns:
            List of alerts
        """
        with self.lock:
            alerts_copy = self.alerts.copy()
            if clear:
                self.alerts.clear()
            return alerts_copy
    
    def update_thief_position(self, position: tuple, observer_id: str) -> None:
        """
        Update thief position with timestamp
        
        Args:
            position: Thief coordinates (x, y)
            observer_id: ID of agent that spotted the thief
        """
        with self.lock:
            self.data["thief_position"] = position
            self.data["thief_last_seen"] = {
                "position": position,
                "observer": observer_id,
                "timestamp": datetime.now()
            }
            # Post alert directly without calling post_alert to avoid lock recursion
            alert = {
                'type': 'thief_sighting',
                'content': {"position": position, "observer": observer_id},
                'severity': 'warning',
                'timestamp': datetime.now(),
            }
            self.alerts.append(alert)
    
    def add_resource_location(self, position: tuple, discovery_id: str) -> None:
        """
        Add a discovered resource location
        
        Args:
            position: Resource coordinates (x, y)
            discovery_id: ID of agent that discovered it
        """
        with self.lock:
            locations = self.data.get("resources_locations", [])
            if position not in locations:
                locations.append(position)
                self.data["resources_locations"] = locations
    
    def remove_resource_location(self, position: tuple) -> None:
        """
        Remove a resource location (when collected)
        
        Args:
            position: Resource coordinates to remove
        """
        with self.lock:
            locations = self.data.get("resources_locations", [])
            if position in locations:
                locations.remove(position)
                self.data["resources_locations"] = locations
    
    def get_message_history(self, limit: int = 50) -> List[Message]:
        """
        Get recent message history
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of recent messages
        """
        with self.lock:
            return self.message_history[-limit:]
    
    def clear_old_messages(self, max_age_seconds: int = 300) -> None:
        """
        Clear old messages from the message queue
        
        Args:
            max_age_seconds: Remove messages older than this
        """
        with self.lock:
            current_time = datetime.now()
            self.messages = [
                m for m in self.messages 
                if (current_time - m.timestamp).total_seconds() < max_age_seconds
            ]
    
    def reset(self) -> None:
        """Reset the blackboard to initial state"""
        with self.lock:
            self.data = {
                "thief_position": None,
                "thief_last_seen": None,
                "resources_at_base": 0,
                "resources_collected_total": 0,
                "resources_locations": [],
                "base_status": "safe",
                "agents_status": {},
                "strategist_commands": [],
                "exploration_progress": {},
                "game_state": "running",
                "elapsed_time": 0,
            }
            self.messages.clear()
            self.alerts.clear()


# Global blackboard instance
_blackboard_instance = None


def get_blackboard() -> Blackboard:
    """Get or create the global blackboard instance"""
    global _blackboard_instance
    if _blackboard_instance is None:
        _blackboard_instance = Blackboard()
    return _blackboard_instance
