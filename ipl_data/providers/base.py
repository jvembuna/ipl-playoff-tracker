from __future__ import annotations

from abc import ABC, abstractmethod

from ipl_data.models import Match, ResultsSnapshot


class ScheduleProvider(ABC):
    @abstractmethod
    def load_schedule(self) -> list[Match]:
        raise NotImplementedError


class ResultsProvider(ABC):
    @abstractmethod
    def load_snapshot(self) -> ResultsSnapshot:
        raise NotImplementedError
