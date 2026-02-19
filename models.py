from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class TimeSlot:
    time: str  # "HH:MM" 24-hour format
    description: str


@dataclass
class WeekSchedule:
    monday: List[TimeSlot] = field(default_factory=list)
    tuesday: List[TimeSlot] = field(default_factory=list)
    wednesday: List[TimeSlot] = field(default_factory=list)
    thursday: List[TimeSlot] = field(default_factory=list)
    friday: List[TimeSlot] = field(default_factory=list)
    saturday: List[TimeSlot] = field(default_factory=list)
    sunday: List[TimeSlot] = field(default_factory=list)


@dataclass
class Event:
    id: int
    name: str
    description: str
    from_date: date
    till_date: date
    top_week: WeekSchedule
    bottom_week: WeekSchedule
    subscriber_telegram_ids: List[int] = field(default_factory=list)


@dataclass
class User:
    id: int
    telegram_id: int
