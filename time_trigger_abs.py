from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Any, List, Union

from models import Event, TimeSlot

# Type alias for the trigger callback signature
TriggerCallback = Callable[[Event, TimeSlot], Coroutine[Any, Any, None]]


class TimeTriggerAbs(ABC):
    """Abstract base for a schedule-driven trigger system.

    Each *trigger* corresponds to a single Event's schedule.
    When a scheduled time arrives the registered callback is invoked
    with the relevant Event and TimeSlot.
    """

    @abstractmethod
    async def add_trigger(
        self,
        event: Event,
        func_to_trigger: TriggerCallback,
    ) -> None:
        """Register all time-slots of *event* and call *func_to_trigger* at each one."""
        ...

    @abstractmethod
    async def remove_trigger(self, event_id: str) -> None:
        """Remove all scheduled jobs associated with *event_id*."""
        ...

    @abstractmethod
    async def import_triggers(
        self,
        events: List[Event],
        funcs_to_trigger: Union[TriggerCallback, List[TriggerCallback]],
    ) -> None:
        """Bulk-register triggers.

        *funcs_to_trigger* may be:
        - a single callable  → applied to every event
        - a list of callables → must match *events* length 1-to-1
        """
        ...

    @abstractmethod
    async def remove_all_triggers(self) -> None:
        """Remove every scheduled job managed by this instance."""
        ...
