"""Event Bus (Observer pattern) for decoupling UI frames.

Frames publish events without knowing who listens;
ViewContainer subscribes without knowing who publishes.
"""

from enum import Enum
from typing import Callable, Dict, List, Any

class Event(Enum):
    LOGIN_SUCCEEDED = "login_succeeded"
    LOGOUT = "logout"
    GO_TO_REGISTER = "go_to_register"
    GO_TO_LOGIN = "go_to_login"

class EventBus:
    _subscribers: Dict[Event, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event: Event, callback: Callable) -> None:
        cls._subscribers.setdefault(event, []).append(callback)

    @classmethod
    def unsubscribe(cls, event: Event, callback: Callable) -> None:
        callbacks = cls._subscribers.get(event)
        if callbacks and callback in callbacks:
            callbacks.remove(callback)

    @classmethod
    def publish(cls, event: Event, data: Any = None) -> None:
        for callback in cls._subscribers.get(event, []):
            callback(data)

    @classmethod
    def clear(cls) -> None:
        """For tests: remove all subscriptions."""
        cls._subscribers.clear()
