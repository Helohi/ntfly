from datetime import date
from typing import List

from models import Event, TimeSlot, User, WeekSchedule

users: List[User] = []

events: List[Event] = [
    Event(
        id=1,
        name="НПИ - Онлайн лекции",
        description="Напоминание для НПИшников про онлайн лекции",
        from_date=date(2025, 9, 1),
        till_date=date(2026, 6, 30),
        top_week=WeekSchedule(
            tuesday=[
                TimeSlot(
                    time="09:00",
                    description="*Основы информационной безопасности*\nСсылка: ???",
                )
            ],
            friday=[
                TimeSlot(
                    time="09:00",
                    description="*Вычислительные системы, сети и телекоммуникации*\nСсылка: ",
                )
            ],
        ),
        bottom_week=WeekSchedule(
            tuesday=[
                TimeSlot(
                    time="09:00",
                    description="*Интеллектуальные системы*\nСсылка: https://telemost.yandex.ru/j/5081495234",
                ),
                TimeSlot(
                    time="10:30",
                    description="*Теория вероятностей и математическая статистика*\nСсылка: https://telemost.yandex.ru/j/6626217220",
                ),
            ],
            friday=[
                TimeSlot(
                    time="09:00",
                    description="*Структуры данных и парадигмы программирования*\nСсылка: https://telemost.yandex.ru/j/9547126616",
                )
            ],
        ),
    )
]
