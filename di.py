"""
Dependency Injection container.

Import `time_trigger` from this module wherever you need the scheduler.
This ensures a single APSchedulerTimeTrigger instance is shared across the
entire application instead of each module creating its own.
"""

from time_trigger_abs import TimeTriggerAbs
from time_trigger import APSchedulerTimeTrigger

# The sole scheduler instance used throughout the application.
# Type is annotated as the abstract base so callers depend on the interface,
# not the concrete implementation.
time_trigger: TimeTriggerAbs = APSchedulerTimeTrigger()
