from datetime import datetime
from typing import Callable, Coroutine, Any, List, Union

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from models import Event, TimeSlot, WeekSchedule
from time_trigger_abs import TimeTriggerAbs, TriggerCallback

# Maps Python dataclass field names → APScheduler day-of-week abbreviations
_DAY_FIELD_TO_CRON: dict[str, str] = {
    "monday": "mon",
    "tuesday": "tue",
    "wednesday": "wed",
    "thursday": "thu",
    "friday": "fri",
    "saturday": "sat",
    "sunday": "sun",
}


def _is_top_week() -> bool:
    """Odd ISO-week numbers are treated as 'top', even as 'bottom'."""
    return datetime.now().isocalendar()[1] % 2 != 0


def _build_job_id(event_id: str, week_type: str, day: str, time_str: str) -> str:
    return f"{event_id}__{week_type}__{day}__{time_str.replace(':', '')}"


class APSchedulerTimeTrigger(TimeTriggerAbs):
    """Concrete trigger implementation backed by APScheduler's AsyncIOScheduler.

    Call :meth:`start` once the asyncio event-loop is running (e.g. inside
    Application.post_init).
    """

    def __init__(self) -> None:
        self._scheduler: AsyncIOScheduler = AsyncIOScheduler()

    def start(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()

    # ── internal helpers ───────────────────────────────────────────────────────

    def _schedule_slot(
        self,
        event: Event,
        week_type: str,
        day_name: str,
        slot: TimeSlot,
        func: TriggerCallback,
    ) -> None:
        hour, minute = map(int, slot.time.split(":"))
        is_top = week_type == "top"
        job_id = _build_job_id(event.id, week_type, day_name, slot.time)

        # Capture loop variables via default arguments to avoid closure issues
        async def _job(
            _event: Event = event,
            _slot: TimeSlot = slot,
            _top: bool = is_top,
            _func: TriggerCallback = func,
        ) -> None:
            if _is_top_week() == _top:
                await _func(_event, _slot)

        self._scheduler.add_job(
            _job,
            CronTrigger(day_of_week=_DAY_FIELD_TO_CRON[day_name], hour=hour, minute=minute),
            id=job_id,
            replace_existing=True,
        )

    def _schedule_week(
        self, event: Event, week_type: str, week: WeekSchedule, func: TriggerCallback
    ) -> None:
        for day_name, slots in vars(week).items():
            for slot in slots:
                self._schedule_slot(event, week_type, day_name, slot, func)

    # ── TimeTriggerAbs interface ───────────────────────────────────────────────

    async def add_trigger(self, event: Event, func_to_trigger: TriggerCallback) -> None:
        self._schedule_week(event, "top", event.top_week, func_to_trigger)
        self._schedule_week(event, "bottom", event.bottom_week, func_to_trigger)

    async def remove_trigger(self, event_id: str) -> None:
        for job in self._scheduler.get_jobs():
            if job.id.startswith(f"{event_id}__"):
                self._scheduler.remove_job(job.id)

    async def import_triggers(
        self,
        events: List[Event],
        funcs_to_trigger: Union[TriggerCallback, List[TriggerCallback]],
    ) -> None:
        if callable(funcs_to_trigger):
            for event in events:
                await self.add_trigger(event, funcs_to_trigger)
        else:
            if len(events) != len(funcs_to_trigger):
                raise ValueError(
                    f"events ({len(events)}) and funcs_to_trigger ({len(funcs_to_trigger)}) "
                    "must have the same length."
                )
            for event, func in zip(events, funcs_to_trigger):
                await self.add_trigger(event, func)

    async def remove_all_triggers(self) -> None:
        self._scheduler.remove_all_jobs()
