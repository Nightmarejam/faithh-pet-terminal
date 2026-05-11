"""
PLC-like State Manager for FAITHH
Deterministic state machine with safety interlocks and validation
"""

import json
import time
import enum
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

class SystemState(enum.Enum):
    """PLC-like discrete system states"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    EMERGENCY_STOP = "emergency_stop"
    RECOVERING = "recovering"
    SHUTTING_DOWN = "shutting_down"

class InputSensor(enum.Enum):
    """System input sensors (like PLC inputs)"""
    USER_REQUEST = "user_request"
    API_CALL = "api_call"
    SYSTEM_HEALTH = "system_health"
    BUDGET_STATUS = "budget_status"
    MODEL_AVAILABILITY = "model_availability"
    ERROR_SIGNAL = "error_signal"
    MAINTENANCE_REQUEST = "maintenance_request"

class OutputActuator(enum.Enum):
    """System output actuators (like PLC outputs)"""
    MODEL_SELECTION = "model_selection"
    TASK_EXECUTION = "task_execution"
    ERROR_RESPONSE = "error_response"
    SYSTEM_SHUTDOWN = "system_shutdown"
    BUDGET_ALERT = "budget_alert"
    STATE_NOTIFICATION = "state_notification"

@dataclass
class StateTransition:
    """State transition definition with validation"""
    from_state: SystemState
    to_state: SystemState
    trigger: InputSensor
    conditions: List[str]
    actions: List[str]
    timestamp: float
    validated: bool = False

@dataclass
class SystemStatus:
    """Current system status (PLC scan data)"""
    state: SystemState
    timestamp: float
    sensors: Dict[InputSensor, Any]
    actuators: Dict[OutputActuator, Any]
    health_score: float
    error_count: int
    last_transition: Optional[StateTransition]

class PLCStateManager:
    """PLC-like deterministic state manager"""
    
    def __init__(self, state_file: str = "plc_system_state.json"):
        self.state_file = Path(state_file)
        self.current_state = SystemState.IDLE
        self.status = SystemStatus(
            state=SystemState.IDLE,
            timestamp=time.time(),
            sensors={},
            actuators={},
            health_score=1.0,
            error_count=0,
            last_transition=None
        )
        self.transition_log: List[StateTransition] = []
        self.state_matrix = self._build_state_matrix()
        self.load_state()
    
    def _build_state_matrix(self) -> Dict[SystemState, Dict[InputSensor, SystemState]]:
        """Build deterministic state transition matrix"""
        return {
            SystemState.IDLE: {
                InputSensor.USER_REQUEST: SystemState.PROCESSING,
                InputSensor.API_CALL: SystemState.PROCESSING,
                InputSensor.MAINTENANCE_REQUEST: SystemState.MAINTENANCE,
                InputSensor.ERROR_SIGNAL: SystemState.ERROR,
            },
            SystemState.PROCESSING: {
                InputSensor.USER_REQUEST: SystemState.PROCESSING,  # Queue requests
                InputSensor.API_CALL: SystemState.PROCESSING,      # Queue requests
                InputSensor.ERROR_SIGNAL: SystemState.ERROR,
                InputSensor.SYSTEM_HEALTH: SystemState.ERROR,       # Health failure
            },
            SystemState.ERROR: {
                InputSensor.USER_REQUEST: SystemState.RECOVERING,
                InputSensor.API_CALL: SystemState.RECOVERING,
                InputSensor.ERROR_SIGNAL: SystemState.EMERGENCY_STOP,
            },
            SystemState.RECOVERING: {
                InputSensor.SYSTEM_HEALTH: SystemState.IDLE,        # Recovery successful
                InputSensor.ERROR_SIGNAL: SystemState.EMERGENCY_STOP,
            },
            SystemState.MAINTENANCE: {
                InputSensor.USER_REQUEST: SystemState.IDLE,          # Maintenance complete
                InputSensor.API_CALL: SystemState.IDLE,
            },
            SystemState.EMERGENCY_STOP: {
                InputSensor.USER_REQUEST: SystemState.RECOVERING,    # Manual recovery
                InputSensor.MAINTENANCE_REQUEST: SystemState.MAINTENANCE,
            },
            SystemState.SHUTTING_DOWN: {
                # No transitions from shutting down
            }
        }
    
    def scan_inputs(self) -> Dict[InputSensor, Any]:
        """Scan all input sensors (PLC input scan)"""
        sensors = {}
        
        # Scan system health
        try:
            with open("fingerprint_state.json", "r") as f:
                health_data = json.load(f)
                sensors[InputSensor.SYSTEM_HEALTH] = health_data.get("overall_health", 0.8)
        except:
            sensors[InputSensor.SYSTEM_HEALTH] = 0.5
        
        # Scan budget status
        try:
            with open("anthropic_usage.json", "r") as f:
                budget_data = json.load(f)
                budget_used = budget_data.get("usage_usd", 0.0)
                sensors[InputSensor.BUDGET_STATUS] = budget_used < 20.0
        except:
            sensors[InputSensor.BUDGET_STATUS] = True
        
        # Scan model availability
        sensors[InputSensor.MODEL_AVAILABILITY] = True  # Simplified
        
        # Scan for error conditions
        sensors[InputSensor.ERROR_SIGNAL] = self.status.error_count > 5
        
        return sensors
    
    def validate_transition(self, trigger: InputSensor, proposed_state: SystemState) -> Tuple[bool, List[str]]:
        """Validate state transition before execution (safety interlock)"""
        validation_errors = []
        
        # Check if transition is allowed in state matrix
        allowed_transitions = self.state_matrix.get(self.current_state, {})
        if trigger not in allowed_transitions:
            validation_errors.append(f"Transition {self.current_state} -> {proposed_state} not allowed for trigger {trigger}")
            return False, validation_errors
        
        if allowed_transitions[trigger] != proposed_state:
            validation_errors.append(f"Transition mismatch: expected {allowed_transitions[trigger]}, got {proposed_state}")
            return False, validation_errors
        
        # Check system health for critical transitions
        if proposed_state == SystemState.PROCESSING:
            health = self.status.sensors.get(InputSensor.SYSTEM_HEALTH, 0.0)
            if health < 0.7:
                validation_errors.append(f"System health too low for processing: {health}")
        
        # Check budget for processing
        if proposed_state == SystemState.PROCESSING:
            budget_ok = self.status.sensors.get(InputSensor.BUDGET_STATUS, True)
            if not budget_ok:
                validation_errors.append("Budget exhausted - cannot process")
        
        # Check error count
        if proposed_state == SystemState.PROCESSING and self.status.error_count > 3:
            validation_errors.append(f"Too many errors ({self.status.error_count}) for processing")
        
        return len(validation_errors) == 0, validation_errors
    
    def execute_transition(self, trigger: InputSensor, proposed_state: SystemState, actions: List[str] = None) -> bool:
        """Execute validated state transition (PLC output execution)"""
        # Validate first
        is_valid, errors = self.validate_transition(trigger, proposed_state)
        if not is_valid:
            logger.error(f"Transition validation failed: {errors}")
            self.status.error_count += 1
            return False
        
        # Create transition record
        transition = StateTransition(
            from_state=self.current_state,
            to_state=proposed_state,
            trigger=trigger,
            conditions=[],
            actions=actions or [],
            timestamp=time.time(),
            validated=True
        )
        
        # Execute actions
        if actions:
            for action in actions:
                try:
                    self._execute_action(action)
                except Exception as e:
                    logger.error(f"Action execution failed: {action} - {e}")
                    self.status.error_count += 1
        
        # Update state
        old_state = self.current_state
        self.current_state = proposed_state
        self.status.last_transition = transition
        self.transition_log.append(transition)
        
        # Update status
        self.status.state = proposed_state
        self.status.timestamp = time.time()
        
        logger.info(f"State transition: {old_state} -> {proposed_state} (trigger: {trigger})")
        
        # Save state
        self.save_state()
        
        return True
    
    def _execute_action(self, action: str):
        """Execute state transition action"""
        if action == "clear_errors":
            self.status.error_count = 0
        elif action == "save_backup":
            # Create backup of current state
            backup_file = f"plc_state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.save_state(backup_file)
        elif action == "notify_user":
            # Send notification (placeholder)
            logger.info(f"User notification: State changed to {self.current_state}")
        # Add more actions as needed
    
    def get_status(self) -> SystemStatus:
        """Get current system status (PLC scan data)"""
        self.status.sensors = self.scan_inputs()
        return self.status
    
    def emergency_stop(self, reason: str = "Manual emergency stop"):
        """Execute emergency stop"""
        logger.warning(f"EMERGENCY STOP: {reason}")
        self.execute_transition(InputSensor.ERROR_SIGNAL, SystemState.EMERGENCY_STOP, ["notify_user"])
    
    def request_maintenance(self):
        """Request maintenance mode"""
        return self.execute_transition(InputSensor.MAINTENANCE_REQUEST, SystemState.MAINTENANCE)
    
    def save_state(self, filename: str = None):
        """Save current state to file"""
        file_path = Path(filename or self.state_file)
        
        state_data = {
            "current_state": self.current_state.value,
            "status": asdict(self.status),
            "transition_log": [asdict(t) for t in self.transition_log[-100:]],  # Keep last 100
            "timestamp": time.time(),
            "version": "1.0"
        }
        
        # Convert enums to strings for JSON serialization
        state_data["status"]["state"] = state_data["status"]["state"].value
        for i, transition in enumerate(state_data["transition_log"]):
            transition["from_state"] = transition["from_state"].value
            transition["to_state"] = transition["to_state"].value
            transition["trigger"] = transition["trigger"].value
        
        with open(file_path, "w") as f:
            json.dump(state_data, f, indent=2)
    
    def load_state(self):
        """Load state from file"""
        if not self.state_file.exists():
            return
        
        try:
            with open(self.state_file, "r") as f:
                state_data = json.load(f)
            
            # Restore current state
            self.current_state = SystemState(state_data["current_state"])
            
            # Restore status
            status_data = state_data["status"]
            status_data["state"] = SystemState(status_data["state"])
            self.status = SystemStatus(**status_data)
            
            # Restore transition log
            self.transition_log = []
            for transition_data in state_data.get("transition_log", []):
                transition_data["from_state"] = SystemState(transition_data["from_state"])
                transition_data["to_state"] = SystemState(transition_data["to_state"])
                transition_data["trigger"] = InputSensor(transition_data["trigger"])
                self.transition_log.append(StateTransition(**transition_data))
            
            logger.info(f"State loaded: {self.current_state}")
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            self.current_state = SystemState.IDLE

# Global instance
plc_state_manager = PLCStateManager()
